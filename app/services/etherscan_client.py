from urllib.parse import urlencode
from urllib.request import urlopen
import json

from app.core.config import (
    ETHERSCAN_API_BASE_URL,
    ETHERSCAN_API_KEY,
    ETHERSCAN_CHAIN_ID,
)


class EtherscanClient:
    def __init__(
        self,
        api_key: str | None = ETHERSCAN_API_KEY,
        base_url: str = ETHERSCAN_API_BASE_URL,
        chain_id: str = ETHERSCAN_CHAIN_ID,
        timeout_seconds: int = 10,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.chain_id = chain_id
        self.timeout_seconds = timeout_seconds

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _get(self, params: dict[str, str]) -> dict:
        if not self.api_key:
            raise RuntimeError("ETHERSCAN_API_KEY is not configured")

        query_params = {
            "chainid": self.chain_id,
            **params,
            "apikey": self.api_key,
        }
        url = f"{self.base_url}?{urlencode(query_params)}"

        with urlopen(url, timeout=self.timeout_seconds) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload)

    def get_native_balance_wei(self, wallet_address: str) -> int | None:
        data = self._get({
            "module": "account",
            "action": "balance",
            "address": wallet_address,
            "tag": "latest",
        })
        result = data.get("result")
        if result is None:
            return None
        return int(result)

    def get_transaction_count(self, wallet_address: str) -> int | None:
        data = self._get({
            "module": "proxy",
            "action": "eth_getTransactionCount",
            "address": wallet_address,
            "tag": "latest",
        })
        result = data.get("result")
        if not result:
            return None
        return int(result, 16)

    def get_contract_code(self, wallet_address: str) -> str | None:
        data = self._get({
            "module": "proxy",
            "action": "eth_getCode",
            "address": wallet_address,
            "tag": "latest",
        })
        return data.get("result")

    def get_normal_transactions(
        self,
        wallet_address: str,
        offset: int = 100,
    ) -> list[dict]:
        data = self._get({
            "module": "account",
            "action": "txlist",
            "address": wallet_address,
            "startblock": "0",
            "endblock": "99999999",
            "page": "1",
            "offset": str(offset),
            "sort": "asc",
        })
        result = data.get("result")
        if not isinstance(result, list):
            return []
        return result

    def build_wallet_profile(self, wallet_address: str) -> dict:
        if not self.is_configured:
            return {
                "provider": "etherscan",
                "provider_configured": False,
                "message": "ETHERSCAN_API_KEY is not configured; provider validation skipped.",
            }

        try:
            native_balance_wei = self.get_native_balance_wei(wallet_address)
            transaction_count = self.get_transaction_count(wallet_address)
            contract_code = self.get_contract_code(wallet_address)
            has_contract_code = bool(contract_code and contract_code != "0x")
            normal_transactions = self.get_normal_transactions(wallet_address)
        except Exception as error:
            return {
                "provider": "etherscan",
                "provider_configured": True,
                "message": f"Provider validation skipped after API error: {error}",
            }

        transaction_timestamps = [
            int(transaction["timeStamp"])
            for transaction in normal_transactions
            if transaction.get("timeStamp")
        ]
        unique_counterparties = {
            value.lower()
            for transaction in normal_transactions
            for value in (transaction.get("from"), transaction.get("to"))
            if value and value.lower() != wallet_address.lower()
        }

        return {
            "provider": "etherscan",
            "provider_configured": True,
            "native_balance_wei": native_balance_wei,
            "transaction_count": transaction_count,
            "has_contract_code": has_contract_code,
            "normal_transaction_sample_size": len(normal_transactions),
            "first_transaction_timestamp": (
                min(transaction_timestamps) if transaction_timestamps else None
            ),
            "last_transaction_timestamp": (
                max(transaction_timestamps) if transaction_timestamps else None
            ),
            "unique_counterparty_count": len(unique_counterparties),
        }
