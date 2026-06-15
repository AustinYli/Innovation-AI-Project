import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Header, HTTPException, Request

from app.core.config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS


class InMemoryRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> None:
        if self.max_requests <= 0 or self.window_seconds <= 0:
            return

        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            request_times = self._requests[key]
            while request_times and request_times[0] <= cutoff:
                request_times.popleft()

            if len(request_times) >= self.max_requests:
                retry_after = max(1, int(self.window_seconds - (now - request_times[0])))
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Try again later.",
                    headers={"Retry-After": str(retry_after)},
                )

            request_times.append(now)


rate_limiter = InMemoryRateLimiter(
    max_requests=RATE_LIMIT_REQUESTS,
    window_seconds=RATE_LIMIT_WINDOW_SECONDS,
)


def require_rate_limit(
    request: Request,
    x_api_key: str | None = Header(default=None),
) -> None:
    client_host = request.client.host if request.client else "unknown-client"
    api_key_marker = x_api_key[:8] if x_api_key else "missing-key"
    route_path = request.url.path
    rate_limiter.check(f"{api_key_marker}:{client_host}:{route_path}")
