import unittest

from app.services.scoring_service import score_wallet_features


class ScoringServiceTests(unittest.TestCase):
    def test_scores_established_funded_wallet_high(self):
        features = {
            "data_quality": "live_provider",
            "balance_level": "funded",
            "activity_level": "moderate",
            "wallet_age_days": 120,
            "unique_counterparty_count": 5,
            "transaction_count": 20,
            "activity_frequency_per_day": 1.5,
            "is_contract": False,
            "feature_flags": [],
        }

        result = score_wallet_features(features, [])

        self.assertEqual(result["human_likelihood"], "high")
        self.assertEqual(result["trust_tier"], "gold")
        self.assertAlmostEqual(result["confidence_score"], 0.92)
        self.assertEqual(result["risk_flags"], [])

    def test_scores_empty_new_wallet_low(self):
        features = {
            "data_quality": "live_provider",
            "balance_level": "empty",
            "activity_level": "none",
            "wallet_age_days": 2,
            "unique_counterparty_count": 0,
            "transaction_count": 0,
            "activity_frequency_per_day": None,
            "is_contract": False,
            "feature_flags": ["empty_wallet", "new_wallet"],
        }

        result = score_wallet_features(features, [])

        self.assertEqual(result["human_likelihood"], "low")
        self.assertEqual(result["trust_tier"], "bronze")
        self.assertAlmostEqual(result["confidence_score"], 0.05)
        self.assertIn("empty_wallet", result["risk_flags"])
        self.assertIn("new_wallet", result["risk_flags"])
        self.assertIn("no_transactions", result["risk_flags"])

    def test_penalizes_contract_address(self):
        features = {
            "data_quality": "live_provider",
            "balance_level": "funded",
            "activity_level": "high",
            "wallet_age_days": 500,
            "unique_counterparty_count": 15,
            "transaction_count": 100,
            "activity_frequency_per_day": 2,
            "is_contract": True,
            "feature_flags": [],
        }

        result = score_wallet_features(features, [])

        self.assertIn("contract_address", result["risk_flags"])
        rule_names = [
            rule["rule"] for rule in result["score_breakdown"]["rules"]
        ]
        self.assertIn("contract_address", rule_names)


if __name__ == "__main__":
    unittest.main()
