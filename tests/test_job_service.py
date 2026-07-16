import time
import unittest

from app.services.job_service import BackgroundJobQueue


class JobServiceTests(unittest.TestCase):
    def test_background_job_completes_with_result(self):
        queue = BackgroundJobQueue(max_workers=1)

        submitted = queue.submit(
            job_type="score_wallet",
            wallet_address="0xabc",
            handler=lambda wallet: {"wallet_address": wallet, "score": 0.9},
        )

        self.assertIn(submitted["status"], ["queued", "running", "completed"])

        for _ in range(20):
            status = queue.get(submitted["job_id"])
            if status["status"] == "completed":
                break
            time.sleep(0.01)

        self.assertEqual(status["status"], "completed")
        self.assertEqual(status["result"]["score"], 0.9)
        self.assertEqual(queue.summary()["total_jobs"], 1)

    def test_background_job_records_failure(self):
        queue = BackgroundJobQueue(max_workers=1)

        def failing_handler(_wallet: str):
            raise RuntimeError("provider unavailable")

        submitted = queue.submit(
            job_type="score_wallet",
            wallet_address="0xabc",
            handler=failing_handler,
        )

        for _ in range(20):
            status = queue.get(submitted["job_id"])
            if status["status"] == "failed":
                break
            time.sleep(0.01)

        self.assertEqual(status["status"], "failed")
        self.assertEqual(status["error"], "provider unavailable")


if __name__ == "__main__":
    unittest.main()
