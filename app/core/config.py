import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return None

load_dotenv()

ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")
ALCHEMY_API_BASE_URL = os.getenv(
    "ALCHEMY_API_BASE_URL",
    (
        f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
        if ALCHEMY_API_KEY
        else None
    ),
)
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_API_BASE_URL = os.getenv(
    "ETHERSCAN_API_BASE_URL",
    "https://api.etherscan.io/v2/api"
)
ETHERSCAN_CHAIN_ID = os.getenv("ETHERSCAN_CHAIN_ID", "1")
DATABASE_URL = os.getenv("DATABASE_URL")
TRUST_API_KEY = os.getenv("TRUST_API_KEY") or os.getenv("API_KEY")
PROOF_SECRET = os.getenv("PROOF_SECRET") or TRUST_API_KEY or "dev-proof-secret"
PROOF_VALID_FOR_HOURS = int(os.getenv("PROOF_VALID_FOR_HOURS", "24"))
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://127.0.0.1:8080",
    ).split(",")
    if origin.strip()
]
