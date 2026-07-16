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

    def test_week5_bot_detection_rules_lower_score(self):
        features = {
            "data_quality": "live_provider",
            "balance_level": "low",
            "activity_level": "high",
            "wallet_age_days": 1,
            "unique_counterparty_count": 2,
            "transaction_count": 120,
            "activity_frequency_per_day": 120,
            "transaction_diversity_ratio": 0.02,
            "contract_interaction_ratio": 0.92,
            "transaction_entropy": 0.1,
            "max_transactions_per_hour": 30,
            "max_transactions_per_day": 100,
            "repeated_contract_loop_count": 80,
            "has_nft_activity": False,
            "is_contract": False,
            "feature_flags": [
                "short_lifespan_wallet",
                "low_transaction_diversity",
                "high_contract_interaction_ratio",
                "hourly_burst_activity",
                "daily_burst_activity",
                "repeated_contract_loops",
            ],
        }

        result = score_wallet_features(features, [])
        rule_names = [
            rule["rule"] for rule in result["score_breakdown"]["rules"]
        ]

        self.assertEqual(result["human_likelihood"], "low")
        self.assertEqual(result["trust_tier"], "bronze")
        self.assertIn("low_transaction_diversity", result["risk_flags"])
        self.assertIn("low_transaction_entropy", result["risk_flags"])
        self.assertIn("high_contract_interaction_ratio", result["risk_flags"])
        self.assertIn("hourly_burst_activity", result["risk_flags"])
        self.assertIn("repeated_contract_loops", result["risk_flags"])
        self.assertIn("short_lifespan_wallet", result["risk_flags"])
        self.assertIn("repeated_contract_loops", rule_names)
        self.assertIn("low_transaction_entropy", rule_names)

    def test_nft_and_alchemy_activity_can_improve_established_wallet(self):
        features = {
            "data_quality": "live_provider",
            "balance_level": "funded",
            "activity_level": "moderate",
            "wallet_age_days": 180,
            "unique_counterparty_count": 12,
            "transaction_count": 40,
            "activity_frequency_per_day": 1.2,
            "transaction_diversity_ratio": 0.5,
            "contract_interaction_ratio": 0.25,
            "transaction_entropy": 0.85,
            "alchemy_transfer_sample_size": 12,
            "has_nft_activity": True,
            "is_contract": False,
            "feature_flags": [],
        }

        result = score_wallet_features(features, [])
        rule_names = [
            rule["rule"] for rule in result["score_breakdown"]["rules"]
        ]

        self.assertEqual(result["human_likelihood"], "high")
        self.assertIn("alchemy_enrichment_available", rule_names)
        self.assertIn("nft_activity_present", rule_names)
        self.assertIn("high_transaction_entropy", rule_names)

    def test_high_sybil_risk_lowers_trust_score(self):
        features = {
            "data_quality": "live_provider",
            "balance_level": "funded",
            "activity_level": "moderate",
            "wallet_age_days": 180,
            "unique_counterparty_count": 8,
            "transaction_count": 40,
            "activity_frequency_per_day": 1.2,
            "is_contract": False,
            "feature_flags": [],
            "sybil_risk_level": "high",
            "sybil_risk_score": 0.82,
            "sybil_signals": [
                "shared_funding_source",
                "matching_behavior_fingerprint",
            ],
        }

        result = score_wallet_features(features, [])
        rule_names = [
            rule["rule"] for rule in result["score_breakdown"]["rules"]
        ]

        self.assertIn("high_sybil_risk", rule_names)
        self.assertIn("high_sybil_risk", result["risk_flags"])
        self.assertIn("shared_funding_source", result["risk_flags"])
        self.assertLess(result["confidence_score"], 0.75)


if __name__ == "__main__":
    unittest.main()
