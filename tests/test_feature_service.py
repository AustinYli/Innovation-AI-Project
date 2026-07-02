import unittest

from app.services.feature_service import extract_wallet_features


class FeatureServiceTests(unittest.TestCase):
    def test_extracts_week5_advanced_bot_features(self):
        provider_profile = {
            "provider_configured": True,
            "message": None,
            "native_balance_wei": 100000000000000000,
            "transaction_count": 120,
            "first_transaction_timestamp": 1704067200,
            "last_transaction_timestamp": 1704153600,
            "unique_counterparty_count": 2,
            "normal_transaction_sample_size": 100,
            "has_contract_code": False,
            "contract_interaction_count": 90,
            "unique_contract_counterparty_count": 1,
            "counterparty_sequence": ["0xaaa"] * 90 + ["0xbbb"] * 10,
            "transaction_timestamps": [1704067200 + index for index in range(25)],
            "nft_transfer_sample_size": 3,
            "alchemy_transfer_sample_size": 20,
            "alchemy_unique_counterparty_count": 2,
            "alchemy_transfer_categories": ["erc20", "erc721"],
        }

        features = extract_wallet_features(provider_profile)

        self.assertEqual(features["transaction_diversity_ratio"], 0.02)
        self.assertEqual(features["contract_interaction_ratio"], 0.9)
        self.assertLess(features["transaction_entropy"], 0.5)
        self.assertEqual(features["max_transactions_per_hour"], 25)
        self.assertEqual(features["repeated_contract_loop_count"], 89)
        self.assertTrue(features["has_nft_activity"])
        self.assertIn("low_transaction_diversity", features["feature_flags"])
        self.assertIn("high_contract_interaction_ratio", features["feature_flags"])
        self.assertIn("hourly_burst_activity", features["feature_flags"])
        self.assertIn("repeated_contract_loops", features["feature_flags"])


if __name__ == "__main__":
    unittest.main()
