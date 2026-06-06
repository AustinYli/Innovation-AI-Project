import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return None

load_dotenv()

ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_API_BASE_URL = os.getenv(
    "ETHERSCAN_API_BASE_URL",
    "https://api.etherscan.io/v2/api"
)
ETHERSCAN_CHAIN_ID = os.getenv("ETHERSCAN_CHAIN_ID", "1")
DATABASE_URL = os.getenv("DATABASE_URL")
TRUST_API_KEY = os.getenv("TRUST_API_KEY") or os.getenv("API_KEY")
