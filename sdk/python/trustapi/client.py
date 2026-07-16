import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class TrustApiError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class TrustApiClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://innovation-ai-project-production.up.railway.app",
        timeout_seconds: float = 30,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _request(
        self,
        method: str,
        path: str,
        payload: dict | None = None,
    ) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {
            "Accept": "application/json",
            "X-API-Key": self.api_key,
        }
        body = None

        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload).encode("utf-8")

        request = Request(url, data=body, headers=headers, method=method)

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                response_body = response.read().decode("utf-8")
                return json.loads(response_body) if response_body else {}
        except HTTPError as error:
            detail = error.read().decode("utf-8") or error.reason
            raise TrustApiError(detail, status_code=error.code) from error
        except URLError as error:
            raise TrustApiError(f"Could not reach TrustAPI: {error.reason}") from error

    def check_wallet(self, wallet_address: str) -> dict:
        return self._request(
            "POST",
            "/check_wallet",
            {"wallet_address": wallet_address},
        )

    def score_wallet(self, wallet_address: str) -> dict:
        return self._request(
            "POST",
            "/score_wallet",
            {"wallet_address": wallet_address},
        )

    def analyze_sybil(self, wallet_address: str) -> dict:
        return self._request(
            "POST",
            "/analyze_sybil",
            {"wallet_address": wallet_address},
        )

    def generate_proof(self, wallet_address: str) -> dict:
        return self._request(
            "POST",
            "/generate_proof",
            {"wallet_address": wallet_address},
        )

    def verify_proof(self, proof_id: str) -> dict:
        return self._request(
            "POST",
            "/verify_proof",
            {"proof_id": proof_id},
        )

    def submit_score_job(self, wallet_address: str) -> dict:
        return self._request(
            "POST",
            "/jobs/score_wallet",
            {"wallet_address": wallet_address},
        )

    def get_job(self, job_id: str) -> dict:
        return self._request("GET", f"/jobs/{job_id}")
