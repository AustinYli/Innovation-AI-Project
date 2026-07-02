from collections import Counter
from datetime import datetime, timezone
from math import log2


WEI_PER_ETH = 10**18


def _classify_balance(native_balance_wei: int | None) -> str:
    if native_balance_wei is None:
        return "unknown"
    if native_balance_wei == 0:
        return "empty"
    if native_balance_wei < 10**15:
        return "dust"
    if native_balance_wei < 10**17:
        return "low"
    return "funded"


def _classify_activity(transaction_count: int | None) -> str:
    if transaction_count is None:
        return "unknown"
    if transaction_count == 0:
        return "none"
    if transaction_count < 5:
        return "low"
    if transaction_count < 50:
        return "moderate"
    return "high"


def _timestamp_age_days(timestamp: int | None) -> int | None:
    if timestamp is None:
        return None

    first_seen = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    return max((now - first_seen).days, 0)


def _safe_ratio(numerator: int | None, denominator: int | None) -> float | None:
    if numerator is None or denominator in {None, 0}:
        return None
    return round(numerator / denominator, 4)


def _normalized_entropy(values: list[str]) -> float | None:
    if not values:
        return None

    counts = Counter(values)
    total = sum(counts.values())
    if total <= 1 or len(counts) <= 1:
        return 0.0

    entropy = -sum(
        (count / total) * log2(count / total)
        for count in counts.values()
    )
    max_entropy = log2(len(counts))
    return round(entropy / max_entropy, 4) if max_entropy else 0.0


def _max_transactions_in_window(
    timestamps: list[int],
    window_seconds: int,
) -> int | None:
    if not timestamps:
        return None

    ordered = sorted(timestamps)
    max_count = 0
    left = 0

    for right, timestamp in enumerate(ordered):
        while timestamp - ordered[left] > window_seconds:
            left += 1
        max_count = max(max_count, right - left + 1)

    return max_count


def extract_wallet_features(provider_profile: dict) -> dict:
    native_balance_wei = provider_profile.get("native_balance_wei")
    transaction_count = provider_profile.get("transaction_count")
    first_transaction_timestamp = provider_profile.get("first_transaction_timestamp")
    last_transaction_timestamp = provider_profile.get("last_transaction_timestamp")
    unique_counterparty_count = provider_profile.get("unique_counterparty_count")
    sample_size = provider_profile.get("normal_transaction_sample_size")
    contract_interaction_count = provider_profile.get("contract_interaction_count")
    unique_contract_counterparty_count = provider_profile.get(
        "unique_contract_counterparty_count"
    )
    counterparty_sequence = provider_profile.get("counterparty_sequence") or []
    transaction_timestamps = provider_profile.get("transaction_timestamps") or []
    nft_transfer_sample_size = max(
        provider_profile.get("nft_transfer_sample_size") or 0,
        provider_profile.get("alchemy_nft_transfer_sample_size") or 0,
    )

    wallet_age_days = _timestamp_age_days(first_transaction_timestamp)
    activity_span_days = None
    activity_frequency_per_day = None
    transaction_diversity_ratio = _safe_ratio(
        unique_counterparty_count,
        sample_size,
    )
    contract_interaction_ratio = _safe_ratio(
        contract_interaction_count,
        sample_size,
    )
    transaction_entropy = _normalized_entropy(counterparty_sequence)
    max_transactions_per_hour = _max_transactions_in_window(
        transaction_timestamps,
        3600,
    )
    max_transactions_per_day = _max_transactions_in_window(
        transaction_timestamps,
        86400,
    )
    repeated_contract_loop_count = None

    if contract_interaction_count:
        repeated_contract_loop_count = max(
            contract_interaction_count - (unique_contract_counterparty_count or 0),
            0,
        )

    if first_transaction_timestamp and last_transaction_timestamp:
        activity_span_days = max(
            int((last_transaction_timestamp - first_transaction_timestamp) / 86400),
            1,
        )

    if transaction_count is not None and activity_span_days:
        activity_frequency_per_day = round(transaction_count / activity_span_days, 4)

    feature_flags = []

    if transaction_count == 0:
        feature_flags.append("no_transactions")
    elif transaction_count is not None and transaction_count < 5:
        feature_flags.append("low_transaction_count")

    if native_balance_wei == 0:
        feature_flags.append("empty_wallet")

    if provider_profile.get("has_contract_code"):
        feature_flags.append("contract_address")

    if wallet_age_days is not None and wallet_age_days < 7:
        feature_flags.append("new_wallet")

    if wallet_age_days is not None and wallet_age_days < 3 and transaction_count:
        feature_flags.append("short_lifespan_wallet")

    if (
        activity_frequency_per_day is not None
        and activity_frequency_per_day > 20
        and unique_counterparty_count is not None
        and unique_counterparty_count < 5
    ):
        feature_flags.append("possible_burst_behavior")

    if max_transactions_per_hour is not None and max_transactions_per_hour >= 20:
        feature_flags.append("hourly_burst_activity")

    if max_transactions_per_day is not None and max_transactions_per_day >= 80:
        feature_flags.append("daily_burst_activity")

    if (
        repeated_contract_loop_count is not None
        and repeated_contract_loop_count >= 10
    ):
        feature_flags.append("repeated_contract_loops")

    if (
        transaction_diversity_ratio is not None
        and transaction_count
        and transaction_count >= 20
        and transaction_diversity_ratio < 0.10
    ):
        feature_flags.append("low_transaction_diversity")

    if (
        transaction_entropy is not None
        and transaction_count
        and transaction_count >= 20
        and transaction_entropy < 0.25
    ):
        feature_flags.append("low_transaction_entropy")

    if (
        contract_interaction_ratio is not None
        and contract_interaction_ratio >= 0.80
        and transaction_count
        and transaction_count >= 20
    ):
        feature_flags.append("high_contract_interaction_ratio")

    return {
        "data_quality": (
            "live_provider"
            if provider_profile.get("provider_configured")
            and provider_profile.get("message") is None
            else "provider_unavailable"
        ),
        "native_balance_wei": native_balance_wei,
        "native_balance_eth": (
            round(native_balance_wei / WEI_PER_ETH, 8)
            if native_balance_wei is not None
            else None
        ),
        "balance_level": _classify_balance(native_balance_wei),
        "transaction_count": transaction_count,
        "activity_level": _classify_activity(transaction_count),
        "wallet_age_days": wallet_age_days,
        "activity_span_days": activity_span_days,
        "activity_frequency_per_day": activity_frequency_per_day,
        "unique_counterparty_count": unique_counterparty_count,
        "normal_transaction_sample_size": sample_size,
        "transaction_diversity_ratio": transaction_diversity_ratio,
        "contract_interaction_count": contract_interaction_count,
        "contract_interaction_ratio": contract_interaction_ratio,
        "unique_contract_counterparty_count": unique_contract_counterparty_count,
        "transaction_entropy": transaction_entropy,
        "max_transactions_per_hour": max_transactions_per_hour,
        "max_transactions_per_day": max_transactions_per_day,
        "repeated_contract_loop_count": repeated_contract_loop_count,
        "nft_transfer_sample_size": nft_transfer_sample_size,
        "has_nft_activity": nft_transfer_sample_size > 0,
        "alchemy_transfer_sample_size": provider_profile.get(
            "alchemy_transfer_sample_size"
        ),
        "alchemy_unique_counterparty_count": provider_profile.get(
            "alchemy_unique_counterparty_count"
        ),
        "alchemy_transfer_categories": provider_profile.get(
            "alchemy_transfer_categories",
            [],
        ),
        "is_contract": provider_profile.get("has_contract_code"),
        "feature_flags": sorted(set(feature_flags)),
    }
