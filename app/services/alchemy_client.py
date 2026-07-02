import json
import ssl
from urllib.request import Request, urlopen

try:
    import certifi
except ImportError:
    certifi = None

from app.core.config import ALCHEMY_API_BASE_URL, ALCHEMY_API_KEY


class AlchemyClient:
    def __init__(
        self,
        api_key: str | None = ALCHEMY_API_KEY,
        base_url: str | None = ALCHEMY_API_BASE_URL,
        timeout_seconds: int = 10,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.base_url)

    def _post(self, method: str, params: list | None = None) -> dict:
        if not self.is_configured:
            raise RuntimeError("ALCHEMY_API_KEY is not configured")

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or [],
        }
        request = Request(
            self.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        context = (
            ssl.create_default_context(cafile=certifi.where())
            if certifi
            else None
        )

        with urlopen(request, timeout=self.timeout_seconds, context=context) as response:
            response_payload = response.read().decode("utf-8")
            data = json.loads(response_payload)
            if "error" in data:
                raise RuntimeError(data["error"].get("message", "Alchemy API error"))
            return data

    def get_asset_transfers(
        self,
        wallet_address: str,
        direction: str,
        max_count: int = 100,
    ) -> list[dict]:
        if direction not in {"from", "to"}:
            raise ValueError("direction must be from or to")

        params = {
            "fromBlock": "0x0",
            "toBlock": "latest",
            "category": ["external", "erc20", "erc721", "erc1155"],
            "maxCount": hex(max_count),
            "excludeZeroValue": False,
        }
        params[f"{direction}Address"] = wallet_address

        data = self._post("alchemy_getAssetTransfers", [params])
        result = data.get("result", {})
        transfers = result.get("transfers", [])
        return transfers if isinstance(transfers, list) else []

    def build_wallet_enrichment(self, wallet_address: str) -> dict:
        if not self.is_configured:
            return {
                "alchemy_provider_configured": False,
                "alchemy_message": "ALCHEMY_API_KEY is not configured; Alchemy enrichment skipped.",
            }

        try:
            outgoing = self.get_asset_transfers(wallet_address, "from")
            incoming = self.get_asset_transfers(wallet_address, "to")
        except Exception as error:
            return {
                "alchemy_provider_configured": True,
                "alchemy_message": f"Alchemy enrichment skipped after API error: {error}",
            }

        transfers = [*outgoing, *incoming]
        counterparties = {
            value.lower()
            for transfer in transfers
            for value in (transfer.get("from"), transfer.get("to"))
            if value and value.lower() != wallet_address.lower()
        }
        categories = [
            transfer.get("category")
            for transfer in transfers
            if transfer.get("category")
        ]
        nft_transfers = [
            category
            for category in categories
            if category in {"erc721", "erc1155"}
        ]

        return {
            "alchemy_provider_configured": True,
            "alchemy_transfer_sample_size": len(transfers),
            "alchemy_outgoing_transfer_sample_size": len(outgoing),
            "alchemy_incoming_transfer_sample_size": len(incoming),
            "alchemy_unique_counterparty_count": len(counterparties),
            "alchemy_nft_transfer_sample_size": len(nft_transfers),
            "alchemy_transfer_categories": sorted(set(categories)),
            "alchemy_message": None,
        }
