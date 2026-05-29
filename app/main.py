from fastapi import FastAPI
from app.schemas import WalletCheckRequest, WalletCheckResponse
from app.services.wallet_service import ingest_wallet

app = FastAPI(
    title="Proof-of-Human Trust API",
    description="MVP backend for wallet trust scoring and proof-of-human signals.",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Proof-of-Human Trust API is running",
        "status": "ok"
    }


@app.post("/check_wallet", response_model=WalletCheckResponse)
def check_wallet(request: WalletCheckRequest):
    result = ingest_wallet(request.wallet_address)
    return result