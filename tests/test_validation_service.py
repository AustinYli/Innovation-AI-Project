import unittest

from app.services.validation_service import (
    WalletValidationError,
    validate_wallet_address,
)


class WalletValidationServiceTests(unittest.TestCase):
    def test_accepts_valid_lowercase_wallet(self):
        result = validate_wallet_address(
            "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        )

        self.assertEqual(
            result.normalized_address,
            "0x742d35cc6634c0532925a3b844bc454e4438f44e",
        )
        self.assertEqual(result.validation_level, "layer_1")

    def test_rejects_missing_0x_prefix(self):
        with self.assertRaisesRegex(WalletValidationError, "must start with 0x"):
            validate_wallet_address("742d35cc6634c0532925a3b844bc454e4438f44e")

    def test_rejects_short_wallet(self):
        with self.assertRaisesRegex(WalletValidationError, "42 characters"):
            validate_wallet_address("0x123")

    def test_rejects_non_hex_wallet(self):
        with self.assertRaisesRegex(WalletValidationError, "hexadecimal"):
            validate_wallet_address("0x742d35cc6634c0532925a3b844bc454e4438f44z")

    def test_rejects_zero_address(self):
        with self.assertRaisesRegex(WalletValidationError, "zero address"):
            validate_wallet_address("0x0000000000000000000000000000000000000000")

    def test_flags_burn_address(self):
        result = validate_wallet_address(
            "0x000000000000000000000000000000000000dead"
        )

        self.assertIn("burn_address", result.risk_flags)


if __name__ == "__main__":
    unittest.main()
