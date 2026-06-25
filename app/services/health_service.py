from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core import config
from app.db.session import get_database_error, get_session_factory


SERVICE_NAME = "wallet_trust_api"
SERVICE_VERSION = "0.1.0"


def _configured_status(value: str | None) -> str:
    return "configured" if value else "missing"


def _database_check() -> dict:
    session_factory = get_session_factory()
    if session_factory is None:
        return {
            "status": (
                "invalid_url"
                if get_database_error()
                else "not_configured"
            ),
            "configured": bool(config.DATABASE_URL),
        }

    try:
        with session_factory() as session:
            session.execute(text("select 1"))
        return {
            "status": "connected",
            "configured": True,
        }
    except SQLAlchemyError:
        return {
            "status": "connection_error",
            "configured": True,
        }


def get_health_response() -> dict:
    checks = {
        "database": _database_check(),
        "etherscan": {
            "status": _configured_status(config.ETHERSCAN_API_KEY),
            "configured": bool(config.ETHERSCAN_API_KEY),
        },
        "auth": {
            "status": _configured_status(config.TRUST_API_KEY),
            "configured": bool(config.TRUST_API_KEY),
        },
    }

    service_ready = all(
        check["configured"]
        for check in [
            checks["etherscan"],
            checks["auth"],
        ]
    )
    database_ready = checks["database"]["status"] == "connected"
    status = "ok" if service_ready and database_ready else "degraded"

    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "status": status,
        "checks": checks,
        "message": (
            "Service is ready."
            if status == "ok"
            else "Service is running, but one or more dependencies need attention."
        ),
    }


def get_debug_env_response() -> dict:
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "environment": {
            "alchemy_api_key": {
                "configured": bool(config.ALCHEMY_API_KEY),
            },
            "etherscan_api_key": {
                "configured": bool(config.ETHERSCAN_API_KEY),
            },
            "database_url": {
                "configured": bool(config.DATABASE_URL),
            },
            "trust_api_key": {
                "configured": bool(config.TRUST_API_KEY),
            },
            "proof_secret": {
                "configured": bool(config.PROOF_SECRET),
            },
        },
        "runtime": {
            "cors_origins_count": len(config.CORS_ORIGINS),
            "rate_limit_requests": config.RATE_LIMIT_REQUESTS,
            "rate_limit_window_seconds": config.RATE_LIMIT_WINDOW_SECONDS,
            "proof_valid_for_hours": config.PROOF_VALID_FOR_HOURS,
            "log_level": config.LOG_LEVEL,
        },
        "message": "Environment check loaded without exposing secret values.",
    }
