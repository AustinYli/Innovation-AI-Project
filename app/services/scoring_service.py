BASE_SCORE = 0.50


def _clamp_score(score: float) -> float:
    return max(0.0, min(1.0, round(score, 4)))


def _add_rule(
    rules: list[dict],
    name: str,
    points: float,
    reason: str,
) -> float:
    rules.append({
        "rule": name,
        "points": points,
        "reason": reason,
    })
    return points


def _classify_human_likelihood(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def _classify_trust_tier(score: float) -> str:
    if score >= 0.80:
        return "gold"
    if score >= 0.55:
        return "silver"
    return "bronze"


def score_wallet_features(features: dict, existing_risk_flags: list[str]) -> dict:
    score = BASE_SCORE
    rules = []
    risk_flags = [*existing_risk_flags]

    if features.get("data_quality") == "live_provider":
        score += _add_rule(
            rules,
            "live_provider_data",
            0.05,
            "Live provider data was available for this wallet.",
        )
    else:
        score += _add_rule(
            rules,
            "provider_unavailable",
            -0.05,
            "Live provider data was unavailable, so confidence is reduced.",
        )

    balance_level = features.get("balance_level")
    if balance_level == "funded":
        score += _add_rule(
            rules,
            "funded_wallet",
            0.12,
            "Wallet has meaningful native ETH balance.",
        )
    elif balance_level == "low":
        score += _add_rule(
            rules,
            "low_balance",
            0.03,
            "Wallet has some native ETH balance.",
        )
    elif balance_level == "dust":
        score += _add_rule(
            rules,
            "dust_balance",
            -0.05,
            "Wallet only has dust-level native ETH balance.",
        )
        risk_flags.append("dust_balance")
    elif balance_level == "empty":
        score += _add_rule(
            rules,
            "empty_wallet",
            -0.15,
            "Wallet has no native ETH balance.",
        )
        risk_flags.append("empty_wallet")

    activity_level = features.get("activity_level")
    if activity_level == "high":
        score += _add_rule(
            rules,
            "high_activity",
            0.12,
            "Wallet has high transaction activity.",
        )
    elif activity_level == "moderate":
        score += _add_rule(
            rules,
            "moderate_activity",
            0.08,
            "Wallet has moderate transaction activity.",
        )
    elif activity_level == "low":
        score += _add_rule(
            rules,
            "low_activity",
            -0.05,
            "Wallet has very little transaction activity.",
        )
        risk_flags.append("low_activity")
    elif activity_level == "none":
        score += _add_rule(
            rules,
            "no_activity",
            -0.20,
            "Wallet has no outgoing transaction activity.",
        )
        risk_flags.append("no_transactions")

    wallet_age_days = features.get("wallet_age_days")
    if wallet_age_days is not None:
        if wallet_age_days >= 365:
            score += _add_rule(
                rules,
                "older_wallet",
                0.12,
                "Wallet has been active for at least one year.",
            )
        elif wallet_age_days >= 90:
            score += _add_rule(
                rules,
                "established_wallet",
                0.08,
                "Wallet has been active for at least 90 days.",
            )
        elif wallet_age_days >= 30:
            score += _add_rule(
                rules,
                "maturing_wallet",
                0.03,
                "Wallet has been active for at least 30 days.",
            )
        elif wallet_age_days < 7:
            score += _add_rule(
                rules,
                "new_wallet",
                -0.15,
                "Wallet appears less than one week old.",
            )
            risk_flags.append("new_wallet")
        else:
            score += _add_rule(
                rules,
                "young_wallet",
                -0.05,
                "Wallet appears less than 30 days old.",
            )
            risk_flags.append("young_wallet")

    counterparty_count = features.get("unique_counterparty_count")
    transaction_count = features.get("transaction_count")
    if counterparty_count is not None:
        if counterparty_count >= 10:
            score += _add_rule(
                rules,
                "diverse_counterparties",
                0.08,
                "Wallet interacted with many unique counterparties.",
            )
        elif counterparty_count >= 3:
            score += _add_rule(
                rules,
                "some_counterparty_diversity",
                0.04,
                "Wallet interacted with multiple counterparties.",
            )
        elif transaction_count and transaction_count > 10:
            score += _add_rule(
                rules,
                "low_counterparty_diversity",
                -0.08,
                "Wallet has activity but limited counterparty diversity.",
            )
            risk_flags.append("low_counterparty_diversity")

    activity_frequency = features.get("activity_frequency_per_day")
    if activity_frequency is not None:
        if 0.1 <= activity_frequency <= 10:
            score += _add_rule(
                rules,
                "steady_activity_frequency",
                0.05,
                "Wallet activity frequency looks steady.",
            )
        elif activity_frequency > 20 and (counterparty_count or 0) < 5:
            score += _add_rule(
                rules,
                "possible_burst_behavior",
                -0.18,
                "High activity frequency with few counterparties can indicate burst behavior.",
            )
            risk_flags.append("possible_burst_behavior")
        elif activity_frequency > 100:
            score += _add_rule(
                rules,
                "very_high_activity_frequency",
                -0.08,
                "Very high activity frequency may require additional review.",
            )
            risk_flags.append("high_velocity_activity")

    if features.get("is_contract") is True:
        score += _add_rule(
            rules,
            "contract_address",
            -0.30,
            "Address has contract code and is not a normal externally owned wallet.",
        )
        risk_flags.append("contract_address")

    for feature_flag in features.get("feature_flags", []):
        risk_flags.append(feature_flag)

    final_score = _clamp_score(score)

    return {
        "human_likelihood": _classify_human_likelihood(final_score),
        "trust_tier": _classify_trust_tier(final_score),
        "confidence_score": final_score,
        "risk_flags": sorted(set(risk_flags)),
        "score_breakdown": {
            "base_score": BASE_SCORE,
            "final_score": final_score,
            "rules": rules,
        },
    }
