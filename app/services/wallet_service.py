from app.services.etherscan_client import EtherscanClient
from app.services.feature_service import extract_wallet_features
from app.services.scoring_service import score_wallet_features
from app.services.validation_service import validate_wallet_address


def ingest_wallet(wallet_address: str):
    validation = validate_wallet_address(wallet_address)
    provider_profile = EtherscanClient().build_wallet_profile(
        validation.normalized_address
    )
    features = extract_wallet_features(provider_profile)

    risk_flags = [*validation.risk_flags, *features["feature_flags"]]

    if provider_profile.get("has_contract_code"):
        risk_flags.append("contract_address")

    score = score_wallet_features(features, risk_flags)

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
        "human_likelihood": score["human_likelihood"],
        "trust_tier": score["trust_tier"],
        "confidence_score": score["confidence_score"],
        "score_breakdown": score["score_breakdown"],
        "risk_flags": score["risk_flags"],
        "message": "Wallet passed validation, feature extraction, and heuristic scoring."
    }
