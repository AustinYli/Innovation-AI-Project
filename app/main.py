from fastapi import Depends, FastAPI, HTTPException
from app.core.auth import require_api_key
from app.schemas import (
    WalletCheckRequest,
    WalletCheckResponse,
    WalletFeatureExtractionResponse,
    WalletScoreResponse,
)
from app.services.wallet_service import (
    extract_wallet_feature_response,
    ingest_wallet,
    score_wallet,
)
from app.services.validation_service import WalletValidationError

app = FastAPI(
    title="Proof-of-Human Trust API",
    description="MVP backend for wallet trust scoring and proof-of-human signals.",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Proof-of-Human Trust API is running",
        "status": "ok"
    }


@app.post(
    "/check_wallet",
    response_model=WalletCheckResponse,
    dependencies=[Depends(require_api_key)],
)
def check_wallet(request: WalletCheckRequest):
    try:
        result = ingest_wallet(request.wallet_address)
        return result
    except WalletValidationError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post(
    "/extract_features",
    response_model=WalletFeatureExtractionResponse,
    dependencies=[Depends(require_api_key)],
)
def extract_features(request: WalletCheckRequest):
    try:
        result = extract_wallet_feature_response(request.wallet_address)
        return result
    except WalletValidationError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post(
    "/score_wallet",
    response_model=WalletScoreResponse,
    dependencies=[Depends(require_api_key)],
)
def score_wallet_endpoint(request: WalletCheckRequest):
    try:
        result = score_wallet(request.wallet_address)
        return result
    except WalletValidationError as error:
        raise HTTPException(status_code=400, detail=str(error))
