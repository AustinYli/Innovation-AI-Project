import unittest

from fastapi import HTTPException

from app.core.rate_limit import InMemoryRateLimiter


class RateLimitTests(unittest.TestCase):
    def test_allows_requests_under_limit(self):
        limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60)

        limiter.check("test-key")
        limiter.check("test-key")

    def test_rejects_requests_over_limit(self):
        limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60)
        limiter.check("test-key")

        with self.assertRaises(HTTPException) as context:
            limiter.check("test-key")

        self.assertEqual(context.exception.status_code, 429)
        self.assertEqual(
            context.exception.detail,
            "Rate limit exceeded. Try again later.",
        )
        self.assertIn("Retry-After", context.exception.headers)

    def test_separates_rate_limit_keys(self):
        limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60)

        limiter.check("first-key")
        limiter.check("second-key")

        with self.assertRaises(HTTPException):
            limiter.check("first-key")


if __name__ == "__main__":
    unittest.main()
