from app.db.repository import (
    find_wallet_relationships,
    get_wallet_proof,
    store_wallet_check_snapshot,
    store_wallet_proof_snapshot,
)
from app.services.cache_service import wallet_pipeline_cache
from app.services.alchemy_client import AlchemyClient
from app.services.etherscan_client import EtherscanClient
from app.services.feature_service import extract_wallet_features
from app.services.proof_service import generate_wallet_proof
from app.services.scoring_service import score_wallet_features
from app.services.sybil_service import (
    analyze_sybil_risk,
    generate_behavior_fingerprint,
)
from app.services.validation_service import validate_wallet_address


def build_wallet_pipeline(wallet_address: str) -> dict:
    validation = validate_wallet_address(wallet_address)
    cache_key = f"wallet_pipeline:{validation.normalized_address}"
    cached_pipeline = wallet_pipeline_cache.get(cache_key)
    if cached_pipeline is not None:
        return cached_pipeline

    provider_profile = EtherscanClient().build_wallet_profile(
        validation.normalized_address
    )
    alchemy_enrichment = AlchemyClient().build_wallet_enrichment(
        validation.normalized_address
    )
    provider_profile = {
        **provider_profile,
        **alchemy_enrichment,
    }
    features = extract_wallet_features(provider_profile)
    behavior_fingerprint_hash = generate_behavior_fingerprint(features)
    relationship_context = find_wallet_relationships(
        normalized_wallet_address=validation.normalized_address,
        funding_sources=provider_profile.get("funding_sources") or [],
        direct_counterparties=provider_profile.get("direct_counterparties") or [],
        behavior_fingerprint_hash=behavior_fingerprint_hash,
    )
    sybil_analysis = analyze_sybil_risk(
        wallet_address=validation.normalized_address,
        provider_profile=provider_profile,
        features=features,
        relationship_context=relationship_context,
    )
    features = {
        **features,
        **sybil_analysis,
    }

    risk_flags = [*validation.risk_flags, *features["feature_flags"]]

    if provider_profile.get("has_contract_code"):
        risk_flags.append("contract_address")

    pipeline = {
        "wallet_address": validation.original_address,
        "normalized_wallet_address": validation.normalized_address,
        "is_valid": True,
        "validation": {
            "validation_level": validation.validation_level,
            "normalized_address": validation.normalized_address,
            "notes": validation.notes,
        },
        "provider_profile": provider_profile,
        "features": features,
        "risk_flags": sorted(set(risk_flags)),
    }
    wallet_pipeline_cache.set(cache_key, pipeline)
    return pipeline


def extract_wallet_feature_response(wallet_address: str):
    pipeline = build_wallet_pipeline(wallet_address)

    return {
        "wallet_address": pipeline["wallet_address"],
        "normalized_wallet_address": pipeline["normalized_wallet_address"],
        "is_valid": pipeline["is_valid"],
        "validation": pipeline["validation"],
        "provider_profile": pipeline["provider_profile"],
        "features": pipeline["features"],
        "message": "Wallet passed validation and feature extraction.",
    }


def score_wallet(wallet_address: str):
    pipeline = build_wallet_pipeline(wallet_address)
    score = score_wallet_features(
        pipeline["features"],
        pipeline["risk_flags"],
    )

    return {
        "wallet_address": pipeline["wallet_address"],
        "normalized_wallet_address": pipeline["normalized_wallet_address"],
        "is_valid": pipeline["is_valid"],
        "validation": pipeline["validation"],
        "features": pipeline["features"],
        "human_likelihood": score["human_likelihood"],
        "trust_tier": score["trust_tier"],
        "confidence_score": score["confidence_score"],
        "score_breakdown": score["score_breakdown"],
        "risk_flags": score["risk_flags"],
        "message": "Wallet passed validation, feature extraction, and heuristic scoring.",
    }


def analyze_wallet_sybil_response(wallet_address: str):
    pipeline = build_wallet_pipeline(wallet_address)
    features = pipeline["features"]

    return {
        "wallet_address": pipeline["wallet_address"],
        "normalized_wallet_address": pipeline["normalized_wallet_address"],
        "is_valid": pipeline["is_valid"],
        "behavior_fingerprint_hash": features["behavior_fingerprint_hash"],
        "funding_sources": features["funding_sources"],
        "transaction_graph_connection_count": features[
            "transaction_graph_connection_count"
        ],
        "relationship_data_status": features["relationship_data_status"],
        "cluster_id": features["cluster_id"],
        "cluster_size": features["cluster_size"],
        "cluster_methods": features["cluster_methods"],
        "related_wallet_count": features["related_wallet_count"],
        "related_wallet_addresses": features["related_wallet_addresses"],
        "relationship_edges": features["relationship_edges"],
        "shared_funding_wallet_count": features[
            "shared_funding_wallet_count"
        ],
        "behavior_match_wallet_count": features[
            "behavior_match_wallet_count"
        ],
        "max_counterparty_overlap_ratio": features[
            "max_counterparty_overlap_ratio"
        ],
        "sybil_risk_score": features["sybil_risk_score"],
        "sybil_risk_level": features["sybil_risk_level"],
        "sybil_signals": features["sybil_signals"],
        "message": "Wallet relationship and Sybil risk analysis completed.",
    }


def ingest_wallet(wallet_address: str):
    pipeline = build_wallet_pipeline(wallet_address)
    score = score_wallet_features(
        pipeline["features"],
        pipeline["risk_flags"],
    )
    storage = store_wallet_check_snapshot(pipeline, score)

    return {
        "wallet_id": storage["wallet_id"],
        "wallet_address": pipeline["wallet_address"],
        "normalized_wallet_address": pipeline["normalized_wallet_address"],
        "is_valid": pipeline["is_valid"],
        "human_likelihood": score["human_likelihood"],
        "trust_tier": score["trust_tier"],
        "confidence_score": score["confidence_score"],
        "risk_flags": score["risk_flags"],
        "storage_status": storage["storage_status"],
        "summary": (
            f"Wallet is classified as {score['human_likelihood']} human likelihood "
            f"with {score['trust_tier']} trust tier."
        ),
    }


def generate_proof_response(wallet_address: str):
    pipeline = build_wallet_pipeline(wallet_address)
    score = score_wallet_features(
        pipeline["features"],
        pipeline["risk_flags"],
    )
    storage = store_wallet_check_snapshot(pipeline, score)
    proof = generate_wallet_proof(pipeline, score)
    proof_storage = store_wallet_proof_snapshot(
        pipeline,
        proof,
        score=score,
        wallet_id=storage["wallet_id"],
    )

    public_proof = {
        key: proof[key]
        for key in [
            "proof_id",
            "proof_version",
            "status",
            "revocable",
            "behavior_fingerprint_hash",
            "issued_at",
            "valid_until",
            "valid_for_hours",
        ]
    }

    return {
        "wallet_id": proof_storage["wallet_id"],
        "wallet_address": pipeline["wallet_address"],
        "normalized_wallet_address": pipeline["normalized_wallet_address"],
        "human_likelihood": score["human_likelihood"],
        "trust_tier": score["trust_tier"],
        "confidence_score": score["confidence_score"],
        "risk_flags": score["risk_flags"],
        "proof": public_proof,
        "storage_status": proof_storage["proof_storage_status"],
        "message": "Reusable wallet trust proof generated.",
    }


def verify_proof_response(proof_id: str):
    proof_record = get_wallet_proof(proof_id)

    if not proof_record["found"]:
        database_status = proof_record["database_status"]
        if database_status != "connected":
            return {
                "proof_id": proof_id,
                "is_valid": False,
                "status": "unavailable",
                "message": f"Proof verification unavailable: {database_status}.",
            }

        return {
            "proof_id": proof_id,
            "is_valid": False,
            "status": "not_found",
            "message": "Proof was not found.",
        }

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    status = "active"
    is_valid = True
    message = "Proof is valid and active."

    if proof_record["valid_until"] <= now:
        status = "expired"
        is_valid = False
        message = "Proof has expired."

    proof_payload = proof_record["proof_payload"]

    return {
        "proof_id": proof_record["proof_id"],
        "is_valid": is_valid,
        "status": status,
        "wallet_id": proof_record["wallet_id"],
        "wallet_address": proof_record["wallet_address"],
        "normalized_wallet_address": proof_record["normalized_wallet_address"],
        "human_likelihood": proof_payload.get("human_likelihood"),
        "trust_tier": proof_payload.get("trust_tier"),
        "confidence_score": proof_payload.get("confidence_score"),
        "issued_at": proof_record["issued_at"].isoformat(),
        "valid_until": proof_record["valid_until"].isoformat(),
        "revocable": proof_payload.get("revocable", True),
        "message": message,
    }
