import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Lock
from typing import Callable

from app.core.config import BACKGROUND_WORKERS
from app.services.metrics_service import metrics_recorder

TERMINAL_STATUSES = {"completed", "failed"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class BackgroundJobQueue:
    def __init__(self, max_workers: int):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._jobs: dict[str, dict] = {}
        self._lock = Lock()

    def submit(
        self,
        job_type: str,
        wallet_address: str,
        handler: Callable[[str], dict],
    ) -> dict:
        job_id = f"job_{uuid.uuid4().hex[:24]}"
        job = {
            "job_id": job_id,
            "job_type": job_type,
            "status": "queued",
            "wallet_address": wallet_address,
            "created_at": _utc_now(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
        }

        with self._lock:
            self._jobs[job_id] = job

        metrics_recorder.observe_job("queued")
        self._executor.submit(
            self._run_job,
            job_id=job_id,
            handler=handler,
            wallet_address=wallet_address,
        )
        return self.get(job_id)

    def _run_job(
        self,
        job_id: str,
        handler: Callable[[str], dict],
        wallet_address: str,
    ) -> None:
        with self._lock:
            self._jobs[job_id]["status"] = "running"
            self._jobs[job_id]["started_at"] = _utc_now()
        metrics_recorder.observe_job("running")

        try:
            result = handler(wallet_address)
        except Exception as error:
            with self._lock:
                self._jobs[job_id]["status"] = "failed"
                self._jobs[job_id]["completed_at"] = _utc_now()
                self._jobs[job_id]["error"] = str(error)
            metrics_recorder.observe_job("failed")
            return

        with self._lock:
            self._jobs[job_id]["status"] = "completed"
            self._jobs[job_id]["completed_at"] = _utc_now()
            self._jobs[job_id]["result"] = result
        metrics_recorder.observe_job("completed")

    def get(self, job_id: str) -> dict:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return {
                    "job_id": job_id,
                    "found": False,
                    "status": "not_found",
                    "message": "Background job was not found.",
                }
            return {
                **job,
                "found": True,
                "message": f"Background job is {job['status']}.",
            }

    def summary(self) -> dict:
        with self._lock:
            counts: dict[str, int] = {}
            for job in self._jobs.values():
                counts[job["status"]] = counts.get(job["status"], 0) + 1
            return {
                "configured_workers": BACKGROUND_WORKERS,
                "total_jobs": len(self._jobs),
                "status_counts": counts,
            }


background_job_queue = BackgroundJobQueue(max_workers=BACKGROUND_WORKERS)
