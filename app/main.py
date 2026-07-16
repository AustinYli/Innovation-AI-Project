import logging
import asyncio
import json
import time

from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.auth import require_api_key
from app.core.config import CORS_ORIGINS
from app.core.logging_config import configure_logging
from app.core.rate_limit import require_rate_limit
from app.db.session import init_db
from app.schemas import (
    DashboardSummaryResponse,
    DashboardWalletListResponse,
    DebugEnvResponse,
    HealthResponse,
    ProofVerifyRequest,
    WalletCheckRequest,
    WalletCheckResponse,
    WalletFeatureExtractionResponse,
    WalletJobStatusResponse,
    WalletJobSubmitResponse,
    WalletProofResponse,
    WalletProofVerifyResponse,
    WalletScoreResponse,
    WalletSybilAnalysisResponse,
)
from app.services.dashboard_service import (
    get_dashboard_summary_response,
    get_flagged_wallets_response,
    get_recent_wallets_response,
)
from app.services.health_service import (
    get_debug_env_response,
    get_health_response,
)
from app.services.cache_service import wallet_pipeline_cache
from app.services.job_service import TERMINAL_STATUSES, background_job_queue
from app.services.metrics_service import metrics_recorder
from app.services.wallet_service import (
    analyze_wallet_sybil_response,
    extract_wallet_feature_response,
    generate_proof_response,
    ingest_wallet,
    score_wallet,
    verify_proof_response,
)
from app.services.validation_service import WalletValidationError

configure_logging()
logger = logging.getLogger("wallet_trust_api")
protected_endpoint = [Depends(require_api_key), Depends(require_rate_limit)]

app = FastAPI(
    title="Proof-of-Human Trust API",
    description="MVP backend for wallet trust scoring and proof-of-human signals.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)


@app.on_event("startup")
def startup():
    tables_initialized = init_db()
    logger.info("startup_complete tables_initialized=%s", tables_initialized)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        metrics_recorder.observe_request(
            request.method,
            request.url.path,
            500,
            elapsed_ms,
        )
        logger.exception(
            "request_failed method=%s path=%s elapsed_ms=%s",
            request.method,
            request.url.path,
            elapsed_ms,
        )
        raise

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    metrics_recorder.observe_request(
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    logger.info(
        "request_complete method=%s path=%s status_code=%s elapsed_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.exception_handler(WalletValidationError)
async def wallet_validation_error_handler(_request: Request, error: WalletValidationError):
    logger.warning("wallet_validation_error detail=%s", str(error))
    return JSONResponse(
        status_code=400,
        content={
            "error": "wallet_validation_error",
            "detail": str(error),
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, error: Exception):
    logger.exception(
        "unhandled_error method=%s path=%s error=%s",
        request.method,
        request.url.path,
        str(error),
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "detail": "Unexpected server error. Check server logs for details.",
        },
    )


@app.get("/")
def root():
    return {
        "message": "Proof-of-Human Trust API is running",
        "status": "ok"
    }


@app.get("/health", response_model=HealthResponse)
def health():
    return get_health_response()


@app.get(
    "/debug/env",
    response_model=DebugEnvResponse,
    dependencies=protected_endpoint,
)
def debug_env():
    return get_debug_env_response()


@app.get(
    "/metrics",
    dependencies=protected_endpoint,
)
def metrics():
    return metrics_recorder.snapshot()


@app.get(
    "/cache/stats",
    dependencies=protected_endpoint,
)
def cache_stats():
    return wallet_pipeline_cache.stats()


@app.post(
    "/check_wallet",
    response_model=WalletCheckResponse,
    dependencies=protected_endpoint,
)
def check_wallet(request: WalletCheckRequest):
    return ingest_wallet(request.wallet_address)


@app.post(
    "/extract_features",
    response_model=WalletFeatureExtractionResponse,
    dependencies=protected_endpoint,
)
def extract_features(request: WalletCheckRequest):
    return extract_wallet_feature_response(request.wallet_address)


@app.post(
    "/score_wallet",
    response_model=WalletScoreResponse,
    dependencies=protected_endpoint,
)
def score_wallet_endpoint(request: WalletCheckRequest):
    return score_wallet(request.wallet_address)


@app.post(
    "/jobs/score_wallet",
    response_model=WalletJobSubmitResponse,
    dependencies=protected_endpoint,
)
def submit_score_wallet_job(request: WalletCheckRequest):
    return background_job_queue.submit(
        job_type="score_wallet",
        wallet_address=request.wallet_address,
        handler=score_wallet,
    )


@app.get(
    "/jobs/summary",
    dependencies=protected_endpoint,
)
def jobs_summary():
    return background_job_queue.summary()


@app.get(
    "/jobs/{job_id}",
    response_model=WalletJobStatusResponse,
    dependencies=protected_endpoint,
)
def job_status(job_id: str):
    return background_job_queue.get(job_id)


@app.get(
    "/jobs/{job_id}/events",
    dependencies=protected_endpoint,
)
async def job_events(job_id: str):
    async def event_stream():
        last_status = None
        for _ in range(60):
            job = background_job_queue.get(job_id)
            status = job["status"]
            if status != last_status or status in TERMINAL_STATUSES:
                yield f"data: {json.dumps(job)}\n\n"
                last_status = status
            if status in TERMINAL_STATUSES or status == "not_found":
                return
            await asyncio.sleep(1)

        job = background_job_queue.get(job_id)
        yield f"data: {json.dumps(job)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )


@app.post(
    "/analyze_sybil",
    response_model=WalletSybilAnalysisResponse,
    dependencies=protected_endpoint,
)
def analyze_sybil(request: WalletCheckRequest):
    return analyze_wallet_sybil_response(request.wallet_address)


@app.post(
    "/generate_proof",
    response_model=WalletProofResponse,
    dependencies=protected_endpoint,
)
def generate_proof(request: WalletCheckRequest):
    return generate_proof_response(request.wallet_address)


@app.post(
    "/verify_proof",
    response_model=WalletProofVerifyResponse,
    dependencies=protected_endpoint,
)
def verify_proof(request: ProofVerifyRequest):
    return verify_proof_response(request.proof_id)


@app.get(
    "/dashboard/summary",
    response_model=DashboardSummaryResponse,
    dependencies=protected_endpoint,
)
def dashboard_summary():
    return get_dashboard_summary_response()


@app.get(
    "/dashboard/recent_wallets",
    response_model=DashboardWalletListResponse,
    dependencies=protected_endpoint,
)
def dashboard_recent_wallets(limit: int = Query(default=20, ge=1, le=100)):
    return get_recent_wallets_response(limit=limit)


@app.get(
    "/dashboard/flagged_wallets",
    response_model=DashboardWalletListResponse,
    dependencies=protected_endpoint,
)
def dashboard_flagged_wallets(limit: int = Query(default=20, ge=1, le=100)):
    return get_flagged_wallets_response(limit=limit)
