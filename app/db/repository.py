from sqlalchemy import select

from app.db.models import (
    Wallet,
    WalletFeatureSnapshot,
    WalletProofSnapshot,
    WalletScoreSnapshot,
)
from app.db.session import get_database_error, get_session_factory


def _get_or_create_wallet(session, pipeline: dict) -> Wallet:
    normalized_address = pipeline["normalized_wallet_address"]
    wallet = session.scalar(
        select(Wallet).where(
            Wallet.normalized_wallet_address == normalized_address
        )
    )

    if wallet:
        return wallet

    wallet = Wallet(
        wallet_address=pipeline["wallet_address"],
        normalized_wallet_address=normalized_address,
    )
    session.add(wallet)
    session.flush()
    return wallet


def store_wallet_check_snapshot(pipeline: dict, score: dict) -> dict:
    session_factory = get_session_factory()
    if session_factory is None:
        return {
            "wallet_id": None,
            "feature_snapshot_id": None,
            "score_snapshot_id": None,
            "storage_status": (
                "skipped_database_invalid_url"
                if get_database_error()
                else "skipped_database_not_configured"
            ),
        }

    with session_factory() as session:
        wallet = _get_or_create_wallet(session, pipeline)

        feature_snapshot = WalletFeatureSnapshot(
            wallet_id=wallet.id,
            provider_profile=pipeline["provider_profile"],
            features=pipeline["features"],
        )
        session.add(feature_snapshot)
        session.flush()

        score_snapshot = WalletScoreSnapshot(
            wallet_id=wallet.id,
            human_likelihood=score["human_likelihood"],
            trust_tier=score["trust_tier"],
            confidence_score=score["confidence_score"],
            risk_flags=score["risk_flags"],
            score_breakdown=score["score_breakdown"],
        )
        session.add(score_snapshot)
        session.flush()

        result = {
            "wallet_id": wallet.id,
            "feature_snapshot_id": feature_snapshot.id,
            "score_snapshot_id": score_snapshot.id,
            "storage_status": "stored",
        }

        session.commit()
        return result


def store_wallet_proof_snapshot(
    pipeline: dict,
    proof: dict,
    wallet_id: int | None = None,
) -> dict:
    session_factory = get_session_factory()
    if session_factory is None:
        return {
            "wallet_id": wallet_id,
            "proof_snapshot_id": None,
            "proof_storage_status": (
                "skipped_database_invalid_url"
                if get_database_error()
                else "skipped_database_not_configured"
            ),
        }

    with session_factory() as session:
        if wallet_id is None:
            wallet = _get_or_create_wallet(session, pipeline)
            wallet_id = wallet.id

        proof_payload = {
            key: value
            for key, value in proof.items()
            if key not in {"issued_at_datetime", "expires_at_datetime"}
        }

        proof_snapshot = WalletProofSnapshot(
            wallet_id=wallet_id,
            proof_id=proof["proof_id"],
            behavior_fingerprint_hash=proof["behavior_fingerprint_hash"],
            proof_payload=proof_payload,
            issued_at=proof["issued_at_datetime"],
            expires_at=proof["expires_at_datetime"],
        )
        session.add(proof_snapshot)
        session.flush()

        result = {
            "wallet_id": wallet_id,
            "proof_snapshot_id": proof_snapshot.id,
            "proof_storage_status": "stored",
        }

        session.commit()
        return result
