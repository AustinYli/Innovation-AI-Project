import unittest
from unittest.mock import patch

from app.services.wallet_service import (
    extract_wallet_feature_response,
    generate_proof_response,
    ingest_wallet,
    score_wallet,
)


class FakeEtherscanClient:
    def build_wallet_profile(self, wallet_address: str) -> dict:
        return {
            "provider": "etherscan",
            "provider_configured": True,
            "native_balance_wei": 250000000000000000,
            "transaction_count": 20,
            "has_contract_code": False,
            "normal_transaction_sample_size": 20,
            "first_transaction_timestamp": 1704067200,
            "last_transaction_timestamp": 1704931200,
            "unique_counterparty_count": 5,
            "message": None,
        }


class WalletServiceTests(unittest.TestCase):
    @patch("app.services.wallet_service.EtherscanClient", FakeEtherscanClient)
    @patch(
        "app.services.wallet_service.store_wallet_check_snapshot",
        return_value={
            "wallet_id": 1,
            "feature_snapshot_id": 10,
            "score_snapshot_id": 20,
            "storage_status": "stored",
        },
    )
    def test_ingest_wallet_returns_public_summary(self, _store_snapshot):
        result = ingest_wallet(
            "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        )

        self.assertEqual(result["wallet_id"], 1)
        self.assertEqual(result["storage_status"], "stored")
        self.assertTrue(result["is_valid"])
        self.assertIn(result["human_likelihood"], ["medium", "high"])
        self.assertGreater(result["confidence_score"], 0)
        self.assertIn("summary", result)
        self.assertNotIn("features", result)
        self.assertNotIn("provider_profile", result)
        self.assertNotIn("score_breakdown", result)

    @patch("app.services.wallet_service.EtherscanClient", FakeEtherscanClient)
    def test_extract_wallet_feature_response_omits_score(self):
        result = extract_wallet_feature_response(
            "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        )

        self.assertIn("provider_profile", result)
        self.assertIn("features", result)
        self.assertNotIn("confidence_score", result)
        self.assertNotIn("score_breakdown", result)

    @patch("app.services.wallet_service.EtherscanClient", FakeEtherscanClient)
    def test_score_wallet_response_omits_provider_profile(self):
        result = score_wallet(
            "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        )

        self.assertIn("features", result)
        self.assertIn("confidence_score", result)
        self.assertIn("score_breakdown", result)
        self.assertNotIn("provider_profile", result)

    @patch("app.services.wallet_service.EtherscanClient", FakeEtherscanClient)
    @patch(
        "app.services.wallet_service.store_wallet_check_snapshot",
        return_value={
            "wallet_id": 1,
            "feature_snapshot_id": 10,
            "score_snapshot_id": 20,
            "storage_status": "stored",
        },
    )
    @patch(
        "app.services.wallet_service.store_wallet_proof_snapshot",
        return_value={
            "wallet_id": 1,
            "proof_snapshot_id": 30,
            "proof_storage_status": "stored",
        },
    )
    def test_generate_proof_response_returns_public_proof(
        self,
        store_proof,
        _store_check,
    ):
        result = generate_proof_response(
            "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        )

        self.assertEqual(result["wallet_id"], 1)
        self.assertEqual(result["storage_status"], "stored")
        self.assertIn("proof", result)
        self.assertIn("behavior_fingerprint_hash", result["proof"])
        self.assertEqual(result["proof"]["status"], "active")
        self.assertTrue(result["proof"]["revocable"])
        self.assertIn("valid_until", result["proof"])
        self.assertNotIn("expires_at", result["proof"])
        self.assertNotIn("features", result)
        self.assertNotIn("score_breakdown", result)
        self.assertIsNotNone(store_proof.call_args.kwargs["score"])


if __name__ == "__main__":
    unittest.main()
