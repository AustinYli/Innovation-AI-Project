from app.db.repository import (
    store_wallet_check_snapshot,
    store_wallet_proof_snapshot,
)
from app.services.etherscan_client import EtherscanClient
from app.services.feature_service import extract_wallet_features
from app.services.proof_service import generate_wallet_proof
from app.services.scoring_service import score_wallet_features
from app.services.validation_service import validate_wallet_address


def build_wallet_pipeline(wallet_address: str) -> dict:
    validation = validate_wallet_address(wallet_address)
    provider_profile = EtherscanClient().build_wallet_profile(
        validation.normalized_address
    )
    features = extract_wallet_features(provider_profile)

    risk_flags = [*validation.risk_flags, *features["feature_flags"]]

    if provider_profile.get("has_contract_code"):
        risk_flags.append("contract_address")

    return {
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
        wallet_id=storage["wallet_id"],
    )

    public_proof = {
        key: proof[key]
        for key in [
            "proof_id",
            "proof_version",
            "behavior_fingerprint_hash",
            "issued_at",
            "expires_at",
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
