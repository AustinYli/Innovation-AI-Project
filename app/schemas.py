from pydantic import BaseModel


class WalletCheckRequest(BaseModel):
    wallet_address: str


class ProofVerifyRequest(BaseModel):
    proof_id: str


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


class WalletCheckResponse(BaseModel):
    wallet_id: int | None = None
    wallet_address: str
    normalized_wallet_address: str
    is_valid: bool
    human_likelihood: str
    trust_tier: str
    confidence_score: float
    risk_flags: list[str]
    storage_status: str
    summary: str


class WalletProof(BaseModel):
    proof_id: str
    proof_version: str
    status: str
    revocable: bool
    behavior_fingerprint_hash: str
    issued_at: str
    valid_until: str
    valid_for_hours: int


class WalletProofResponse(BaseModel):
    wallet_id: int | None = None
    wallet_address: str
    normalized_wallet_address: str
    human_likelihood: str
    trust_tier: str
    confidence_score: float
    risk_flags: list[str]
    proof: WalletProof
    storage_status: str
    message: str


class WalletProofVerifyResponse(BaseModel):
    proof_id: str
    is_valid: bool
    status: str
    wallet_id: int | None = None
    wallet_address: str | None = None
    normalized_wallet_address: str | None = None
    human_likelihood: str | None = None
    trust_tier: str | None = None
    confidence_score: float | None = None
    issued_at: str | None = None
    valid_until: str | None = None
    revocable: bool | None = None
    message: str


class DashboardSummaryResponse(BaseModel):
    database_status: str
    total_wallets: int
    total_feature_snapshots: int
    total_score_snapshots: int
    total_proofs: int
    tier_distribution: dict[str, int]
    human_likelihood_distribution: dict[str, int]
    flagged_wallet_count: int
    message: str


class DashboardWalletRow(BaseModel):
    wallet_id: int
    wallet_address: str
    normalized_wallet_address: str
    created_at: str
    human_likelihood: str | None = None
    trust_tier: str | None = None
    confidence_score: float | None = None
    risk_flags: list[str]
    scored_at: str | None = None


class DashboardWalletListResponse(BaseModel):
    database_status: str
    count: int
    wallets: list[DashboardWalletRow]
    message: str
