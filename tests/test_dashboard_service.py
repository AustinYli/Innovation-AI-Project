import unittest
from unittest.mock import patch

from app.services.dashboard_service import (
    get_dashboard_summary_response,
    get_flagged_wallets_response,
    get_recent_wallets_response,
)


class DashboardServiceTests(unittest.TestCase):
    @patch(
        "app.services.dashboard_service.get_dashboard_summary",
        return_value={
            "database_status": "connected",
            "total_wallets": 104,
            "total_feature_snapshots": 125,
            "total_score_snapshots": 125,
            "total_proofs": 10,
            "tier_distribution": {"gold": 4, "silver": 66, "bronze": 55},
            "human_likelihood_distribution": {
                "high": 4,
                "medium": 78,
                "low": 43,
            },
            "flagged_wallet_count": 6,
        },
    )
    def test_dashboard_summary_response_adds_message(self, _summary):
        result = get_dashboard_summary_response()

        self.assertEqual(result["database_status"], "connected")
        self.assertEqual(result["total_wallets"], 104)
        self.assertEqual(result["tier_distribution"]["silver"], 66)
        self.assertEqual(result["message"], "Dashboard summary loaded.")

    @patch(
        "app.services.dashboard_service.list_recent_wallets",
        return_value={
            "database_status": "connected",
            "wallets": [
                {
                    "wallet_id": 1,
                    "wallet_address": "0xabc",
                    "normalized_wallet_address": "0xabc",
                    "created_at": "2026-06-08T04:15:50",
                    "human_likelihood": "medium",
                    "trust_tier": "silver",
                    "confidence_score": 0.7,
                    "risk_flags": [],
                    "scored_at": "2026-06-08T04:15:51",
                },
            ],
        },
    )
    def test_recent_wallets_response_adds_count(self, recent_wallets):
        result = get_recent_wallets_response(limit=8)

        recent_wallets.assert_called_once_with(limit=8)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["message"], "Recent wallets loaded.")

    @patch(
        "app.services.dashboard_service.list_flagged_wallets",
        return_value={
            "database_status": "connected",
            "wallets": [],
        },
    )
    def test_flagged_wallets_response_adds_count(self, flagged_wallets):
        result = get_flagged_wallets_response(limit=8)

        flagged_wallets.assert_called_once_with(limit=8)
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["message"], "Flagged wallets loaded.")


if __name__ == "__main__":
    unittest.main()
