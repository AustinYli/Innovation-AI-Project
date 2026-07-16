from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json

from app.core.config import PROOF_SECRET, PROOF_VALID_FOR_HOURS


PROOF_VERSION = "v1"


def _canonical_json(payload: dict) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _hmac_hex(payload: dict | str) -> str:
    if isinstance(payload, dict):
        message = _canonical_json(payload)
    else:
        message = payload.encode("utf-8")

    return hmac.new(
        PROOF_SECRET.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()


def generate_wallet_proof(pipeline: dict, score: dict) -> dict:
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(hours=PROOF_VALID_FOR_HOURS)

    fingerprint_payload = {
        "proof_version": PROOF_VERSION,
        "wallet": pipeline["normalized_wallet_address"],
        "features": {
            "balance_level": pipeline["features"].get("balance_level"),
            "activity_level": pipeline["features"].get("activity_level"),
            "wallet_age_days": pipeline["features"].get("wallet_age_days"),
            "unique_counterparty_count": pipeline["features"].get(
                "unique_counterparty_count"
            ),
            "is_contract": pipeline["features"].get("is_contract"),
            "feature_flags": pipeline["features"].get("feature_flags", []),
        },
        "score": {
            "human_likelihood": score["human_likelihood"],
            "trust_tier": score["trust_tier"],
            "confidence_score": score["confidence_score"],
            "risk_flags": score["risk_flags"],
        },
    }
    behavior_fingerprint_hash = pipeline["features"].get(
        "behavior_fingerprint_hash"
    ) or _hmac_hex(fingerprint_payload)
    proof_id = "proof_" + _hmac_hex(
        f"{behavior_fingerprint_hash}:{issued_at.isoformat()}"
    )[:32]

    return {
        "proof_id": proof_id,
        "proof_version": PROOF_VERSION,
        "status": "active",
        "revocable": True,
        "behavior_fingerprint_hash": behavior_fingerprint_hash,
        "issued_at": issued_at.isoformat(),
        "valid_until": expires_at.isoformat(),
        "valid_for_hours": PROOF_VALID_FOR_HOURS,
        "issued_at_datetime": issued_at,
        "expires_at_datetime": expires_at,
    }
