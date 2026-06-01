from fastapi import FastAPI, HTTPException
from app.schemas import WalletCheckRequest, WalletCheckResponse
from app.services.wallet_service import ingest_wallet
from app.services.validation_service import WalletValidationError

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
    try:
        result = ingest_wallet(request.wallet_address)
        return result
    except WalletValidationError as error:
        raise HTTPException(status_code=400, detail=str(error))
