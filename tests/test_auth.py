import unittest
from unittest.mock import patch

from fastapi import HTTPException

from app.core.auth import require_api_key


class AuthTests(unittest.TestCase):
    @patch("app.core.auth.TRUST_API_KEY", "test-secret")
    def test_accepts_matching_api_key(self):
        self.assertIsNone(require_api_key("test-secret"))

    @patch("app.core.auth.TRUST_API_KEY", "test-secret")
    def test_rejects_missing_api_key(self):
        with self.assertRaises(HTTPException) as context:
            require_api_key(None)

        self.assertEqual(context.exception.status_code, 401)

    @patch("app.core.auth.TRUST_API_KEY", "test-secret")
    def test_rejects_wrong_api_key(self):
        with self.assertRaises(HTTPException) as context:
            require_api_key("wrong-secret")

        self.assertEqual(context.exception.status_code, 401)

    @patch("app.core.auth.TRUST_API_KEY", None)
    def test_rejects_when_server_key_is_not_configured(self):
        with self.assertRaises(HTTPException) as context:
            require_api_key("test-secret")

        self.assertEqual(context.exception.status_code, 500)


if __name__ == "__main__":
    unittest.main()
