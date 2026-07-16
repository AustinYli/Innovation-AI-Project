import unittest

from app.services.sybil_service import (
    analyze_sybil_risk,
    generate_behavior_fingerprint,
)


class SybilServiceTests(unittest.TestCase):
    def setUp(self):
        self.features = {
            "activity_level": "high",
            "balance_level": "low",
            "is_contract": False,
            "has_nft_activity": False,
            "transaction_count": 120,
            "wallet_age_days": 2,
            "activity_frequency_per_day": 60,
            "transaction_diversity_ratio": 0.05,
            "contract_interaction_ratio": 0.9,
            "transaction_entropy": 0.1,
            "feature_flags": [
                "hourly_burst_activity",
                "low_transaction_diversity",
                "low_transaction_entropy",
                "repeated_contract_loops",
                "short_lifespan_wallet",
            ],
        }

    def test_behavior_fingerprint_is_deterministic(self):
        first = generate_behavior_fingerprint(self.features)
        second = generate_behavior_fingerprint(dict(self.features))

        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_shared_funding_and_behavior_match_create_high_risk_cluster(self):
        provider_profile = {
            "funding_sources": ["0xfunder"],
            "transaction_graph_connections": [
                {
                    "source": "0xfunder",
                    "target": "0xwallet",
                    "transaction_count": 2,
                }
            ],
        }
        relationship_context = {
            "database_status": "connected",
            "related_wallets": [
                {
                    "normalized_wallet_address": "0xpeer",
                    "shared_funding_sources": ["0xfunder"],
                    "same_behavior_fingerprint": True,
                    "counterparty_overlap_ratio": 0.8,
                    "connection_reasons": [
                        "shared_funding_source",
                        "behavior_fingerprint",
                        "transaction_graph_overlap",
                    ],
                }
            ],
        }

        result = analyze_sybil_risk(
            "0xwallet",
            provider_profile,
            self.features,
            relationship_context,
        )

        self.assertEqual(result["cluster_size"], 2)
        self.assertEqual(result["related_wallet_addresses"], ["0xpeer"])
        self.assertEqual(result["relationship_edges"][0]["source"], "0xwallet")
        self.assertEqual(result["relationship_edges"][0]["target"], "0xpeer")
        self.assertEqual(result["shared_funding_wallet_count"], 1)
        self.assertEqual(result["behavior_match_wallet_count"], 1)
        self.assertEqual(result["sybil_risk_level"], "high")
        self.assertGreaterEqual(result["sybil_risk_score"], 0.6)
        self.assertIn("shared_funding_source", result["sybil_signals"])
        self.assertIn("very_high_graph_overlap", result["sybil_signals"])


if __name__ == "__main__":
    unittest.main()
