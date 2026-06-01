from datetime import datetime, timezone


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


def extract_wallet_features(provider_profile: dict) -> dict:
    native_balance_wei = provider_profile.get("native_balance_wei")
    transaction_count = provider_profile.get("transaction_count")
    first_transaction_timestamp = provider_profile.get("first_transaction_timestamp")
    last_transaction_timestamp = provider_profile.get("last_transaction_timestamp")
    unique_counterparty_count = provider_profile.get("unique_counterparty_count")
    sample_size = provider_profile.get("normal_transaction_sample_size")

    wallet_age_days = _timestamp_age_days(first_transaction_timestamp)
    activity_span_days = None
    activity_frequency_per_day = None

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

    if (
        activity_frequency_per_day is not None
        and activity_frequency_per_day > 20
        and unique_counterparty_count is not None
        and unique_counterparty_count < 5
    ):
        feature_flags.append("possible_burst_behavior")

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
        "is_contract": provider_profile.get("has_contract_code"),
        "feature_flags": feature_flags,
    }
