from datetime import timezone

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.db.models import (
    Wallet,
    WalletFeatureSnapshot,
    WalletProofSnapshot,
    WalletScoreSnapshot,
)
from app.db.session import get_database_error, get_session_factory


def _database_unavailable_status() -> str:
    return (
        "skipped_database_invalid_url"
        if get_database_error()
        else "skipped_database_connection_error"
    )


def _empty_dashboard_summary(database_status: str) -> dict:
    return {
        "database_status": database_status,
        "total_wallets": 0,
        "total_feature_snapshots": 0,
        "total_score_snapshots": 0,
        "total_proofs": 0,
        "tier_distribution": {},
        "human_likelihood_distribution": {},
        "flagged_wallet_count": 0,
    }


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

    try:
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
    except SQLAlchemyError:
        return {
            "wallet_id": None,
            "feature_snapshot_id": None,
            "score_snapshot_id": None,
            "storage_status": _database_unavailable_status(),
        }


def store_wallet_proof_snapshot(
    pipeline: dict,
    proof: dict,
    score: dict | None = None,
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

    try:
        with session_factory() as session:
            if wallet_id is None:
                wallet = _get_or_create_wallet(session, pipeline)
                wallet_id = wallet.id

            proof_payload = {
                key: value
                for key, value in proof.items()
                if key not in {"issued_at_datetime", "expires_at_datetime"}
            }
            if score:
                proof_payload.update(
                    {
                        "human_likelihood": score["human_likelihood"],
                        "trust_tier": score["trust_tier"],
                        "confidence_score": score["confidence_score"],
                        "risk_flags": score["risk_flags"],
                    }
                )

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
    except SQLAlchemyError:
        return {
            "wallet_id": wallet_id,
            "proof_snapshot_id": None,
            "proof_storage_status": _database_unavailable_status(),
        }


def get_wallet_proof(proof_id: str) -> dict:
    session_factory = get_session_factory()
    if session_factory is None:
        return {
            "found": False,
            "database_status": (
                "skipped_database_invalid_url"
                if get_database_error()
                else "skipped_database_not_configured"
            ),
        }

    try:
        with session_factory() as session:
            proof_snapshot = session.scalar(
                select(WalletProofSnapshot)
                .where(WalletProofSnapshot.proof_id == proof_id)
                .options(joinedload(WalletProofSnapshot.wallet))
            )

            if proof_snapshot is None:
                return {
                    "found": False,
                    "database_status": "connected",
                }

            issued_at = proof_snapshot.issued_at
            expires_at = proof_snapshot.expires_at
            if issued_at.tzinfo is None:
                issued_at = issued_at.replace(tzinfo=timezone.utc)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            return {
                "found": True,
                "database_status": "connected",
                "proof_id": proof_snapshot.proof_id,
                "wallet_id": proof_snapshot.wallet_id,
                "wallet_address": proof_snapshot.wallet.wallet_address,
                "normalized_wallet_address": proof_snapshot.wallet.normalized_wallet_address,
                "proof_payload": proof_snapshot.proof_payload,
                "issued_at": issued_at,
                "valid_until": expires_at,
            }
    except SQLAlchemyError:
        return {
            "found": False,
            "database_status": _database_unavailable_status(),
        }


def _latest_scores_by_wallet(
    session,
    wallet_ids: list[int] | None = None,
) -> dict[int, WalletScoreSnapshot]:
    latest_score_ids = select(func.max(WalletScoreSnapshot.id).label("id"))
    if wallet_ids is not None:
        if not wallet_ids:
            return {}
        latest_score_ids = latest_score_ids.where(
            WalletScoreSnapshot.wallet_id.in_(wallet_ids)
        )

    latest_score_ids = latest_score_ids.group_by(
        WalletScoreSnapshot.wallet_id
    ).subquery()
    score_snapshots = session.scalars(
        select(WalletScoreSnapshot).where(
            WalletScoreSnapshot.id.in_(select(latest_score_ids.c.id))
        )
    ).all()
    return {
        score_snapshot.wallet_id: score_snapshot
        for score_snapshot in score_snapshots
    }


def get_dashboard_summary() -> dict:
    session_factory = get_session_factory()
    if session_factory is None:
        return _empty_dashboard_summary(
            "skipped_database_invalid_url"
            if get_database_error()
            else "skipped_database_not_configured"
        )

    try:
        with session_factory() as session:
            latest_scores = _latest_scores_by_wallet(session)
            tier_distribution = {}
            likelihood_distribution = {}
            flagged_wallet_count = 0

            for score_snapshot in latest_scores.values():
                tier_distribution[score_snapshot.trust_tier] = (
                    tier_distribution.get(score_snapshot.trust_tier, 0) + 1
                )
                likelihood_distribution[score_snapshot.human_likelihood] = (
                    likelihood_distribution.get(score_snapshot.human_likelihood, 0) + 1
                )
                if score_snapshot.risk_flags:
                    flagged_wallet_count += 1

            return {
                "database_status": "connected",
                "total_wallets": session.scalar(select(func.count()).select_from(Wallet)),
                "total_feature_snapshots": session.scalar(
                    select(func.count()).select_from(WalletFeatureSnapshot)
                ),
                "total_score_snapshots": session.scalar(
                    select(func.count()).select_from(WalletScoreSnapshot)
                ),
                "total_proofs": session.scalar(
                    select(func.count()).select_from(WalletProofSnapshot)
                ),
                "tier_distribution": tier_distribution,
                "human_likelihood_distribution": likelihood_distribution,
                "flagged_wallet_count": flagged_wallet_count,
            }
    except SQLAlchemyError:
        return _empty_dashboard_summary(_database_unavailable_status())


def list_recent_wallets(limit: int = 20) -> dict:
    session_factory = get_session_factory()
    if session_factory is None:
        return {
            "database_status": (
                "skipped_database_invalid_url"
                if get_database_error()
                else "skipped_database_not_configured"
            ),
            "wallets": [],
        }

    try:
        with session_factory() as session:
            wallets = session.scalars(
                select(Wallet).order_by(Wallet.created_at.desc()).limit(limit)
            ).all()
            latest_scores = _latest_scores_by_wallet(
                session,
                wallet_ids=[wallet.id for wallet in wallets],
            )

            return {
                "database_status": "connected",
                "wallets": [
                    _wallet_dashboard_row(wallet, latest_scores.get(wallet.id))
                    for wallet in wallets
                ],
            }
    except SQLAlchemyError:
        return {
            "database_status": _database_unavailable_status(),
            "wallets": [],
        }


def list_flagged_wallets(limit: int = 20) -> dict:
    session_factory = get_session_factory()
    if session_factory is None:
        return {
            "database_status": (
                "skipped_database_invalid_url"
                if get_database_error()
                else "skipped_database_not_configured"
            ),
            "wallets": [],
        }

    try:
        with session_factory() as session:
            latest_scores = _latest_scores_by_wallet(session)
            wallet_ids = [
                wallet_id
                for wallet_id, score_snapshot in latest_scores.items()
                if score_snapshot.risk_flags
            ]

            if not wallet_ids:
                return {
                    "database_status": "connected",
                    "wallets": [],
                }

            wallets = session.scalars(
                select(Wallet).where(Wallet.id.in_(wallet_ids))
            ).all()
            wallet_by_id = {wallet.id: wallet for wallet in wallets}

            flagged_rows = [
                _wallet_dashboard_row(wallet_by_id[wallet_id], latest_scores[wallet_id])
                for wallet_id in wallet_ids
                if wallet_id in wallet_by_id
            ]
            flagged_rows.sort(key=lambda row: row["confidence_score"] or 0)

            return {
                "database_status": "connected",
                "wallets": flagged_rows[:limit],
            }
    except SQLAlchemyError:
        return {
            "database_status": _database_unavailable_status(),
            "wallets": [],
        }


def _wallet_dashboard_row(
    wallet: Wallet,
    score_snapshot: WalletScoreSnapshot | None,
) -> dict:
    return {
        "wallet_id": wallet.id,
        "wallet_address": wallet.wallet_address,
        "normalized_wallet_address": wallet.normalized_wallet_address,
        "created_at": wallet.created_at.isoformat(),
        "human_likelihood": (
            score_snapshot.human_likelihood if score_snapshot else None
        ),
        "trust_tier": score_snapshot.trust_tier if score_snapshot else None,
        "confidence_score": (
            score_snapshot.confidence_score if score_snapshot else None
        ),
        "risk_flags": score_snapshot.risk_flags if score_snapshot else [],
        "scored_at": score_snapshot.scored_at.isoformat() if score_snapshot else None,
    }
