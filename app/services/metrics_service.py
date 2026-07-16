import time
from collections import defaultdict
from threading import Lock


class MetricsRecorder:
    def __init__(self):
        self.started_at = time.time()
        self._lock = Lock()
        self._request_count = 0
        self._error_count = 0
        self._latencies_ms: list[float] = []
        self._status_counts: dict[str, int] = defaultdict(int)
        self._path_counts: dict[str, int] = defaultdict(int)
        self._job_counts: dict[str, int] = defaultdict(int)

    def observe_request(
        self,
        method: str,
        path: str,
        status_code: int,
        elapsed_ms: float,
    ) -> None:
        with self._lock:
            self._request_count += 1
            self._latencies_ms.append(elapsed_ms)
            self._status_counts[str(status_code)] += 1
            self._path_counts[f"{method} {path}"] += 1
            if status_code >= 500:
                self._error_count += 1

    def observe_job(self, status: str) -> None:
        with self._lock:
            self._job_counts[status] += 1

    def snapshot(self) -> dict:
        with self._lock:
            latencies = sorted(self._latencies_ms)
            request_count = self._request_count
            p95_index = (
                round((len(latencies) - 1) * 0.95)
                if latencies
                else 0
            )
            avg_ms = (
                sum(latencies) / len(latencies)
                if latencies
                else 0.0
            )
            uptime_seconds = round(time.time() - self.started_at, 2)
            error_rate = (
                self._error_count / request_count
                if request_count
                else 0.0
            )

            return {
                "service": "wallet_trust_api",
                "uptime_seconds": uptime_seconds,
                "request_count": request_count,
                "error_count": self._error_count,
                "error_rate": round(error_rate, 4),
                "latency": {
                    "avg_ms": round(avg_ms, 2),
                    "p95_ms": round(latencies[p95_index], 2)
                    if latencies
                    else 0.0,
                    "max_ms": round(max(latencies), 2)
                    if latencies
                    else 0.0,
                },
                "status_counts": dict(self._status_counts),
                "path_counts": dict(self._path_counts),
                "background_jobs": dict(self._job_counts),
            }


metrics_recorder = MetricsRecorder()
