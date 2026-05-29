from pydantic import BaseModel


class WalletCheckRequest(BaseModel):
    wallet_address: str


class WalletCheckResponse(BaseModel):
    wallet_address: str
    human_likelihood: str
    trust_tier: str
    confidence_score: float
    risk_flags: list[str]
    message: str