import unittest

from app.services.proof_service import generate_wallet_proof


class ProofServiceTests(unittest.TestCase):
    def test_generates_privacy_safe_proof(self):
        pipeline = {
            "normalized_wallet_address": (
                "0x742d35cc6634c0532925a3b844bc454e4438f44e"
            ),
            "features": {
                "balance_level": "funded",
                "activity_level": "high",
                "wallet_age_days": 100,
                "unique_counterparty_count": 5,
                "is_contract": False,
                "feature_flags": [],
            },
        }
        score = {
            "human_likelihood": "high",
            "trust_tier": "gold",
            "confidence_score": 0.87,
            "risk_flags": [],
        }

        proof = generate_wallet_proof(pipeline, score)

        self.assertTrue(proof["proof_id"].startswith("proof_"))
        self.assertEqual(proof["proof_version"], "v1")
        self.assertEqual(len(proof["behavior_fingerprint_hash"]), 64)
        self.assertNotIn(
            pipeline["normalized_wallet_address"],
            proof["behavior_fingerprint_hash"],
        )
        self.assertEqual(proof["valid_for_hours"], 24)


if __name__ == "__main__":
    unittest.main()
