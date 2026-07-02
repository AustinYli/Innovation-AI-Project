from urllib.parse import urlencode
from urllib.request import urlopen
import json
import ssl

try:
    import certifi
except ImportError:
    certifi = None

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

        context = (
            ssl.create_default_context(cafile=certifi.where())
            if certifi
            else None
        )

        with urlopen(url, timeout=self.timeout_seconds, context=context) as response:
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

    def get_latest_block_number(self) -> int | None:
        data = self._get({
            "module": "proxy",
            "action": "eth_blockNumber",
        })
        result = data.get("result")
        if not result:
            return None
        return int(result, 16)

    def get_block_by_number(self, block_number: int) -> dict | None:
        data = self._get({
            "module": "proxy",
            "action": "eth_getBlockByNumber",
            "tag": hex(block_number),
            "boolean": "true",
        })
        result = data.get("result")
        return result if isinstance(result, dict) else None

    def get_normal_transactions(
        self,
        wallet_address: str,
        offset: int = 100,
        sort: str = "asc",
    ) -> list[dict]:
        data = self._get({
            "module": "account",
            "action": "txlist",
            "address": wallet_address,
            "startblock": "0",
            "endblock": "99999999",
            "page": "1",
            "offset": str(offset),
            "sort": sort,
        })
        result = data.get("result")
        if not isinstance(result, list):
            return []
        return result

    def get_erc721_transfers(
        self,
        wallet_address: str,
        offset: int = 50,
    ) -> list[dict]:
        data = self._get({
            "module": "account",
            "action": "tokennfttx",
            "address": wallet_address,
            "page": "1",
            "offset": str(offset),
            "sort": "desc",
        })
        result = data.get("result")
        if not isinstance(result, list):
            return []
        return result

    def get_erc1155_transfers(
        self,
        wallet_address: str,
        offset: int = 50,
    ) -> list[dict]:
        data = self._get({
            "module": "account",
            "action": "token1155tx",
            "address": wallet_address,
            "page": "1",
            "offset": str(offset),
            "sort": "desc",
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
            recent_transactions = self.get_normal_transactions(
                wallet_address,
                offset=100,
                sort="desc",
            )
            erc721_transfers = self.get_erc721_transfers(wallet_address)
            erc1155_transfers = self.get_erc1155_transfers(wallet_address)
        except Exception as error:
            return {
                "provider": "etherscan",
                "provider_configured": True,
                "message": f"Provider validation skipped after API error: {error}",
            }

        transaction_sample = [*normal_transactions, *recent_transactions]
        transaction_timestamps = [
            int(transaction["timeStamp"])
            for transaction in transaction_sample
            if transaction.get("timeStamp")
        ]
        unique_counterparties = {
            value.lower()
            for transaction in transaction_sample
            for value in (transaction.get("from"), transaction.get("to"))
            if value and value.lower() != wallet_address.lower()
        }
        contract_interactions = [
            transaction
            for transaction in transaction_sample
            if transaction.get("input") not in {None, "", "0x"}
        ]
        contract_counterparties = {
            transaction.get("to", "").lower()
            for transaction in contract_interactions
            if transaction.get("to")
        }
        counterparties = [
            value.lower()
            for transaction in transaction_sample
            for value in (transaction.get("from"), transaction.get("to"))
            if value and value.lower() != wallet_address.lower()
        ]

        return {
            "provider": "etherscan",
            "provider_configured": True,
            "native_balance_wei": native_balance_wei,
            "transaction_count": transaction_count,
            "has_contract_code": has_contract_code,
            "normal_transaction_sample_size": len(transaction_sample),
            "first_transaction_timestamp": (
                min(transaction_timestamps) if transaction_timestamps else None
            ),
            "last_transaction_timestamp": (
                max(transaction_timestamps) if transaction_timestamps else None
            ),
            "unique_counterparty_count": len(unique_counterparties),
            "contract_interaction_count": len(contract_interactions),
            "unique_contract_counterparty_count": len(contract_counterparties),
            "counterparty_sequence": counterparties,
            "transaction_timestamps": transaction_timestamps,
            "erc721_transfer_sample_size": len(erc721_transfers),
            "erc1155_transfer_sample_size": len(erc1155_transfers),
            "nft_transfer_sample_size": len(erc721_transfers) + len(erc1155_transfers),
        }
