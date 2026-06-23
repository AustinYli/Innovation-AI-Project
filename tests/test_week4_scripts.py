import unittest

from scripts.api_client import ApiResult
from scripts.benchmark_api import run_benchmark, summarize_latencies
from scripts.simulate_developer_usage import run_simulation


class FakeTrustApiClient:
    base_url = "https://example.test"

    def __init__(self):
        self.calls = []

    def request(self, method, path, payload=None):
        self.calls.append((method, path, payload))
        responses = {
            "/": {"status": "ok"},
            "/check_wallet": {
                "human_likelihood": "high",
                "trust_tier": "gold",
                "confidence_score": 0.87,
            },
            "/generate_proof": {
                "proof": {"proof_id": "proof_test"},
            },
            "/verify_proof": {"status": "active"},
            "/dashboard/summary": {"total_wallets": 104},
            "/dashboard/recent_wallets?limit=8": {"wallets": []},
            "/dashboard/flagged_wallets?limit=8": {"wallets": []},
        }
        return ApiResult(
            status_code=200,
            data=responses[path],
            elapsed_ms=12.5,
            url=f"{self.base_url}{path}",
        )


class Week4ScriptTests(unittest.TestCase):
    def test_simulation_runs_complete_proof_flow(self):
        client = FakeTrustApiClient()

        result = run_simulation(client, "0xwallet")

        self.assertEqual(result["simulation_status"], "passed")
        self.assertEqual(result["proof_id"], "proof_test")
        self.assertEqual(result["proof_status"], "active")
        self.assertEqual(len(result["steps"]), 5)
        self.assertEqual(
            client.calls[3],
            ("POST", "/verify_proof", {"proof_id": "proof_test"}),
        )

    def test_latency_summary_reports_percentiles(self):
        summary = summarize_latencies([10, 20, 30, 40, 50])

        self.assertEqual(summary["requests"], 5)
        self.assertEqual(summary["mean_ms"], 30)
        self.assertEqual(summary["p50_ms"], 30)
        self.assertEqual(summary["p95_ms"], 50)

    def test_benchmark_uses_read_endpoints_by_default(self):
        client = FakeTrustApiClient()

        result = run_benchmark(
            client=client,
            request_count=2,
            delay_seconds=0,
            include_wallet_check=False,
            wallet_address="0xwallet",
        )

        self.assertEqual(result["benchmark_status"], "passed")
        self.assertEqual(len(result["results"]), 4)
        self.assertEqual(len(client.calls), 8)
        self.assertNotIn("/check_wallet", [call[1] for call in client.calls])


if __name__ == "__main__":
    unittest.main()
