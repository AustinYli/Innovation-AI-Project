import json
import ssl
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import HTTPSHandler, ProxyHandler, Request, build_opener

import certifi


@dataclass
class ApiResult:
    status_code: int
    data: dict
    elapsed_ms: float
    url: str


class ApiRequestError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class TrustApiClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None,
        timeout_seconds: float = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.opener = build_opener(
            ProxyHandler({}),
            HTTPSHandler(context=ssl_context),
        )

    def request(
        self,
        method: str,
        path: str,
        payload: dict | None = None,
    ) -> ApiResult:
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {"Accept": "application/json"}
        body = None

        if self.api_key:
            headers["X-API-Key"] = self.api_key
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload).encode("utf-8")

        request = Request(url, data=body, headers=headers, method=method.upper())
        started_at = time.perf_counter()

        try:
            with self.opener.open(request, timeout=self.timeout_seconds) as response:
                elapsed_ms = (time.perf_counter() - started_at) * 1000
                response_body = response.read().decode("utf-8")
                data = json.loads(response_body) if response_body else {}
                return ApiResult(
                    status_code=response.status,
                    data=data,
                    elapsed_ms=round(elapsed_ms, 2),
                    url=url,
                )
        except HTTPError as error:
            response_body = error.read().decode("utf-8")
            try:
                error_data = json.loads(response_body)
            except json.JSONDecodeError:
                error_data = {"detail": response_body or error.reason}
            detail = (
                error_data.get("detail")
                or error_data.get("message")
                or error_data.get("error")
                or str(error)
            )
            raise ApiRequestError(
                f"{method.upper()} {path} returned {error.code}: {detail}",
                status_code=error.code,
            ) from error
        except URLError as error:
            raise ApiRequestError(
                f"Could not reach {url}: {error.reason}"
            ) from error
