import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import (
    Base,
    Wallet,
    WalletFeatureSnapshot,
    WalletScoreSnapshot,
)
from app.db.repository import (
    _latest_scores_by_wallet,
    find_wallet_relationships,
)


class DashboardRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)

    def tearDown(self):
        self.engine.dispose()

    def test_latest_scores_returns_only_newest_snapshot_per_wallet(self):
        with self.session_factory() as session:
            first_wallet = Wallet(
                wallet_address="0x1111111111111111111111111111111111111111",
                normalized_wallet_address="0x1111111111111111111111111111111111111111",
            )
            second_wallet = Wallet(
                wallet_address="0x2222222222222222222222222222222222222222",
                normalized_wallet_address="0x2222222222222222222222222222222222222222",
            )
            session.add_all([first_wallet, second_wallet])
            session.flush()

            session.add_all([
                self._score(first_wallet.id, "bronze", 0.3),
                self._score(first_wallet.id, "gold", 0.9),
                self._score(second_wallet.id, "silver", 0.6),
            ])
            session.commit()

            latest_scores = _latest_scores_by_wallet(session)

            self.assertEqual(len(latest_scores), 2)
            self.assertEqual(latest_scores[first_wallet.id].trust_tier, "gold")
            self.assertEqual(latest_scores[second_wallet.id].trust_tier, "silver")

    def test_latest_scores_can_limit_wallet_ids(self):
        with self.session_factory() as session:
            first_wallet = Wallet(
                wallet_address="0x1111111111111111111111111111111111111111",
                normalized_wallet_address="0x1111111111111111111111111111111111111111",
            )
            second_wallet = Wallet(
                wallet_address="0x2222222222222222222222222222222222222222",
                normalized_wallet_address="0x2222222222222222222222222222222222222222",
            )
            session.add_all([first_wallet, second_wallet])
            session.flush()
            session.add_all([
                self._score(first_wallet.id, "gold", 0.9),
                self._score(second_wallet.id, "silver", 0.6),
            ])
            session.commit()

            latest_scores = _latest_scores_by_wallet(
                session,
                wallet_ids=[second_wallet.id],
            )

            self.assertEqual(list(latest_scores), [second_wallet.id])

    def test_finds_wallets_connected_by_funder_and_graph(self):
        peer_address = "0x2222222222222222222222222222222222222222"
        with self.session_factory() as session:
            peer_wallet = Wallet(
                wallet_address=peer_address,
                normalized_wallet_address=peer_address,
            )
            session.add(peer_wallet)
            session.flush()
            session.add(
                WalletFeatureSnapshot(
                    wallet_id=peer_wallet.id,
                    provider_profile={
                        "funding_sources": ["0xfunder"],
                        "direct_counterparties": [
                            "0xaaa",
                            "0xbbb",
                            "0xccc",
                        ],
                    },
                    features={
                        "behavior_fingerprint_hash": "fingerprint"
                    },
                )
            )
            session.commit()

        with patch(
            "app.db.repository.get_session_factory",
            return_value=self.session_factory,
        ):
            result = find_wallet_relationships(
                normalized_wallet_address=(
                    "0x1111111111111111111111111111111111111111"
                ),
                funding_sources=["0xfunder"],
                direct_counterparties=["0xaaa", "0xbbb", "0xccc"],
                behavior_fingerprint_hash="fingerprint",
            )

        self.assertEqual(result["database_status"], "connected")
        self.assertEqual(len(result["related_wallets"]), 1)
        relationship = result["related_wallets"][0]
        self.assertEqual(
            relationship["shared_funding_sources"],
            ["0xfunder"],
        )
        self.assertTrue(relationship["same_behavior_fingerprint"])
        self.assertEqual(relationship["counterparty_overlap_ratio"], 1.0)
        self.assertIn(
            "transaction_graph_overlap",
            relationship["connection_reasons"],
        )

    @staticmethod
    def _score(wallet_id: int, tier: str, confidence: float):
        return WalletScoreSnapshot(
            wallet_id=wallet_id,
            human_likelihood="medium",
            trust_tier=tier,
            confidence_score=confidence,
            risk_flags=[],
            score_breakdown={"base_score": 0.5, "final_score": confidence, "rules": []},
        )


if __name__ == "__main__":
    unittest.main()
