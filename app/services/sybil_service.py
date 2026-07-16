import hashlib
import json


def _bucket(value: float | int | None, boundaries: list[float]) -> str:
    if value is None:
        return "unknown"

    for index, boundary in enumerate(boundaries):
        if value < boundary:
            return f"b{index}"
    return f"b{len(boundaries)}"


def generate_behavior_fingerprint(features: dict) -> str:
    payload = {
        "activity_level": features.get("activity_level"),
        "balance_level": features.get("balance_level"),
        "is_contract": features.get("is_contract"),
        "has_nft_activity": features.get("has_nft_activity"),
        "transaction_count_bucket": _bucket(
            features.get("transaction_count"),
            [1, 5, 20, 100, 500],
        ),
        "wallet_age_bucket": _bucket(
            features.get("wallet_age_days"),
            [3, 7, 30, 90, 365],
        ),
        "activity_frequency_bucket": _bucket(
            features.get("activity_frequency_per_day"),
            [0.1, 1, 10, 20, 100],
        ),
        "diversity_bucket": _bucket(
            features.get("transaction_diversity_ratio"),
            [0.1, 0.25, 0.5, 0.75],
        ),
        "contract_ratio_bucket": _bucket(
            features.get("contract_interaction_ratio"),
            [0.2, 0.5, 0.8],
        ),
        "entropy_bucket": _bucket(
            features.get("transaction_entropy"),
            [0.25, 0.5, 0.75],
        ),
        "behavior_flags": sorted(
            flag
            for flag in features.get("feature_flags", [])
            if flag
            in {
                "daily_burst_activity",
                "hourly_burst_activity",
                "low_transaction_diversity",
                "low_transaction_entropy",
                "possible_burst_behavior",
                "repeated_contract_loops",
                "short_lifespan_wallet",
            }
        ),
    }
    canonical_payload = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical_payload).hexdigest()


def _classify_sybil_risk(score: float) -> str:
    if score >= 0.60:
        return "high"
    if score >= 0.30:
        return "medium"
    return "low"


def analyze_sybil_risk(
    wallet_address: str,
    provider_profile: dict,
    features: dict,
    relationship_context: dict | None = None,
) -> dict:
    relationship_context = relationship_context or {
        "database_status": "not_checked",
        "related_wallets": [],
    }
    related_wallets = relationship_context.get("related_wallets", [])
    funding_sources = list(
        dict.fromkeys(provider_profile.get("funding_sources") or [])
    )
    behavior_fingerprint_hash = generate_behavior_fingerprint(features)

    shared_funding_wallet_count = sum(
        bool(wallet.get("shared_funding_sources"))
        for wallet in related_wallets
    )
    behavior_match_wallet_count = sum(
        bool(wallet.get("same_behavior_fingerprint"))
        for wallet in related_wallets
    )
    max_counterparty_overlap_ratio = max(
        (
            wallet.get("counterparty_overlap_ratio", 0.0)
            for wallet in related_wallets
        ),
        default=0.0,
    )

    risk_score = 0.0
    signals = []

    if shared_funding_wallet_count:
        risk_score += min(0.35 + 0.05 * (shared_funding_wallet_count - 1), 0.50)
        signals.append("shared_funding_source")

    if behavior_match_wallet_count:
        risk_score += min(0.20 + 0.05 * (behavior_match_wallet_count - 1), 0.30)
        signals.append("matching_behavior_fingerprint")

    if max_counterparty_overlap_ratio >= 0.75:
        risk_score += 0.25
        signals.append("very_high_graph_overlap")
    elif max_counterparty_overlap_ratio >= 0.50:
        risk_score += 0.15
        signals.append("high_graph_overlap")

    feature_flags = set(features.get("feature_flags", []))
    if feature_flags.intersection(
        {"hourly_burst_activity", "daily_burst_activity", "possible_burst_behavior"}
    ):
        risk_score += 0.12
        signals.append("coordinated_burst_pattern")

    if "repeated_contract_loops" in feature_flags:
        risk_score += 0.12
        signals.append("repeated_contract_pattern")

    if "short_lifespan_wallet" in feature_flags:
        risk_score += 0.10
        signals.append("short_lifespan_pattern")

    if {
        "low_transaction_diversity",
        "low_transaction_entropy",
    }.issubset(feature_flags):
        risk_score += 0.10
        signals.append("low_behavior_diversity")

    risk_score = round(min(risk_score, 1.0), 4)
    cluster_methods = sorted(
        {
            reason
            for wallet in related_wallets
            for reason in wallet.get("connection_reasons", [])
        }
    )
    cluster_seed = "|".join(
        [
            funding_sources[0] if funding_sources else "no-funder",
            behavior_fingerprint_hash,
        ]
    )
    cluster_id = "cluster_" + hashlib.sha256(
        cluster_seed.encode("utf-8")
    ).hexdigest()[:16]
    relationship_edges = [
        {
            "source": wallet_address,
            "target": wallet["normalized_wallet_address"],
            "connection_reasons": sorted(
                wallet.get("connection_reasons", [])
            ),
            "shared_funding_sources": sorted(
                wallet.get("shared_funding_sources", [])
            ),
            "counterparty_overlap_ratio": wallet.get(
                "counterparty_overlap_ratio",
                0.0,
            ),
        }
        for wallet in related_wallets
        if wallet.get("normalized_wallet_address")
    ]

    return {
        "behavior_fingerprint_hash": behavior_fingerprint_hash,
        "funding_sources": funding_sources,
        "funding_source_count": len(funding_sources),
        "primary_funding_source": funding_sources[0] if funding_sources else None,
        "transaction_graph_connection_count": len(
            provider_profile.get("transaction_graph_connections") or []
        ),
        "relationship_data_status": relationship_context.get(
            "database_status",
            "not_checked",
        ),
        "cluster_id": cluster_id,
        "cluster_size": len(related_wallets) + 1,
        "cluster_methods": cluster_methods or ["behavior_fingerprint"],
        "related_wallet_count": len(related_wallets),
        "related_wallet_addresses": sorted(
            wallet["normalized_wallet_address"]
            for wallet in related_wallets
            if wallet.get("normalized_wallet_address")
        ),
        "relationship_edges": relationship_edges,
        "shared_funding_wallet_count": shared_funding_wallet_count,
        "behavior_match_wallet_count": behavior_match_wallet_count,
        "max_counterparty_overlap_ratio": round(
            max_counterparty_overlap_ratio,
            4,
        ),
        "sybil_risk_score": risk_score,
        "sybil_risk_level": _classify_sybil_risk(risk_score),
        "sybil_signals": sorted(set(signals)),
    }
