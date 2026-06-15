import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.services.wallet_service import verify_proof_response


class VerifyProofTests(unittest.TestCase):
    @patch("app.services.wallet_service.get_wallet_proof")
    def test_returns_not_found_for_missing_proof(self, get_wallet_proof):
        get_wallet_proof.return_value = {
            "found": False,
            "database_status": "connected",
        }

        result = verify_proof_response("proof_missing")

        self.assertFalse(result["is_valid"])
        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["message"], "Proof was not found.")

    @patch("app.services.wallet_service.get_wallet_proof")
    def test_returns_active_for_valid_proof(self, get_wallet_proof):
        now = datetime.now(timezone.utc)
        get_wallet_proof.return_value = {
            "found": True,
            "proof_id": "proof_active",
            "wallet_id": 1,
            "wallet_address": "0x742d35cc6634c0532925a3b844bc454e4438f44e",
            "normalized_wallet_address": (
                "0x742d35cc6634c0532925a3b844bc454e4438f44e"
            ),
            "proof_payload": {
                "human_likelihood": "high",
                "trust_tier": "gold",
                "confidence_score": 0.87,
                "revocable": True,
            },
            "issued_at": now,
            "valid_until": now + timedelta(hours=1),
        }

        result = verify_proof_response("proof_active")

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["status"], "active")
        self.assertEqual(result["trust_tier"], "gold")
        self.assertEqual(result["human_likelihood"], "high")

    @patch("app.services.wallet_service.get_wallet_proof")
    def test_returns_expired_for_expired_proof(self, get_wallet_proof):
        now = datetime.now(timezone.utc)
        get_wallet_proof.return_value = {
            "found": True,
            "proof_id": "proof_expired",
            "wallet_id": 1,
            "wallet_address": "0x742d35cc6634c0532925a3b844bc454e4438f44e",
            "normalized_wallet_address": (
                "0x742d35cc6634c0532925a3b844bc454e4438f44e"
            ),
            "proof_payload": {
                "human_likelihood": "medium",
                "trust_tier": "silver",
                "confidence_score": 0.71,
                "revocable": True,
            },
            "issued_at": now - timedelta(hours=2),
            "valid_until": now - timedelta(hours=1),
        }

        result = verify_proof_response("proof_expired")

        self.assertFalse(result["is_valid"])
        self.assertEqual(result["status"], "expired")
        self.assertEqual(result["message"], "Proof has expired.")


if __name__ == "__main__":
    unittest.main()
