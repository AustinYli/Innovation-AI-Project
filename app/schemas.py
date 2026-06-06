from pydantic import BaseModel


class WalletCheckRequest(BaseModel):
    wallet_address: str


class WalletValidationDetails(BaseModel):
    validation_level: str
    normalized_address: str
    notes: list[str]


class WalletProviderProfile(BaseModel):
    provider: str
    provider_configured: bool
    native_balance_wei: int | None = None
    transaction_count: int | None = None
    has_contract_code: bool | None = None
    normal_transaction_sample_size: int | None = None
    first_transaction_timestamp: int | None = None
    last_transaction_timestamp: int | None = None
    unique_counterparty_count: int | None = None
    message: str | None = None


class WalletFeatures(BaseModel):
    data_quality: str
    native_balance_wei: int | None = None
    native_balance_eth: float | None = None
    balance_level: str
    transaction_count: int | None = None
    activity_level: str
    wallet_age_days: int | None = None
    activity_span_days: int | None = None
    activity_frequency_per_day: float | None = None
    unique_counterparty_count: int | None = None
    normal_transaction_sample_size: int | None = None
    is_contract: bool | None = None
    feature_flags: list[str]


class ScoreRule(BaseModel):
    rule: str
    points: float
    reason: str


class ScoreBreakdown(BaseModel):
    base_score: float
    final_score: float
    rules: list[ScoreRule]


class WalletFeatureExtractionResponse(BaseModel):
    wallet_address: str
    normalized_wallet_address: str
    is_valid: bool
    validation: WalletValidationDetails
    provider_profile: WalletProviderProfile
    features: WalletFeatures
    message: str


class WalletScoreResponse(BaseModel):
    wallet_address: str
    normalized_wallet_address: str
    is_valid: bool
    validation: WalletValidationDetails
    features: WalletFeatures
    human_likelihood: str
    trust_tier: str
    confidence_score: float
    score_breakdown: ScoreBreakdown
    risk_flags: list[str]
    message: str


class WalletCheckResponse(WalletScoreResponse):
    provider_profile: WalletProviderProfile
