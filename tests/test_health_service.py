import unittest
from unittest.mock import Mock, patch

from app.services.health_service import (
    get_debug_env_response,
    get_health_response,
)


class HealthServiceTests(unittest.TestCase):
    @patch("app.services.health_service.get_session_factory", return_value=None)
    @patch("app.services.health_service.get_database_error", return_value=None)
    @patch("app.services.health_service.config.TRUST_API_KEY", "test-secret")
    @patch("app.services.health_service.config.ETHERSCAN_API_KEY", "etherscan-secret")
    @patch("app.services.health_service.config.DATABASE_URL", None)
    def test_health_reports_degraded_when_database_is_not_configured(
        self,
        _database_error,
        _session_factory,
    ):
        result = get_health_response()

        self.assertEqual(result["status"], "degraded")
        self.assertEqual(result["checks"]["database"]["status"], "not_configured")
        self.assertTrue(result["checks"]["auth"]["configured"])
        self.assertTrue(result["checks"]["etherscan"]["configured"])

    @patch("app.services.health_service.get_session_factory")
    @patch("app.services.health_service.config.TRUST_API_KEY", "test-secret")
    @patch("app.services.health_service.config.ETHERSCAN_API_KEY", "etherscan-secret")
    @patch("app.services.health_service.config.DATABASE_URL", "postgresql://example")
    def test_health_reports_ok_when_required_checks_pass(self, session_factory):
        session = Mock()
        session_context = Mock()
        session_context.__enter__ = Mock(return_value=session)
        session_context.__exit__ = Mock(return_value=None)
        session_factory.return_value.return_value = session_context

        result = get_health_response()

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["checks"]["database"]["status"], "connected")
        session.execute.assert_called_once()

    @patch("app.services.health_service.config.ALCHEMY_API_KEY", "alchemy-secret")
    @patch("app.services.health_service.config.ETHERSCAN_API_KEY", "etherscan-secret")
    @patch("app.services.health_service.config.DATABASE_URL", "postgresql://secret")
    @patch("app.services.health_service.config.TRUST_API_KEY", "trust-secret")
    @patch("app.services.health_service.config.PROOF_SECRET", "proof-secret")
    @patch("app.services.health_service.config.CORS_ORIGINS", ["http://localhost:5173"])
    @patch("app.services.health_service.config.RATE_LIMIT_REQUESTS", 60)
    @patch("app.services.health_service.config.RATE_LIMIT_WINDOW_SECONDS", 60)
    @patch("app.services.health_service.config.PROOF_VALID_FOR_HOURS", 24)
    @patch("app.services.health_service.config.LOG_LEVEL", "INFO")
    def test_debug_env_reports_presence_without_secret_values(self):
        result = get_debug_env_response()
        rendered = str(result)

        self.assertTrue(result["environment"]["trust_api_key"]["configured"])
        self.assertTrue(result["environment"]["database_url"]["configured"])
        self.assertEqual(result["runtime"]["rate_limit_requests"], 60)
        self.assertNotIn("trust-secret", rendered)
        self.assertNotIn("postgresql://secret", rendered)
        self.assertNotIn("etherscan-secret", rendered)


if __name__ == "__main__":
    unittest.main()
