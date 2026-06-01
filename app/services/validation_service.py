import re
from dataclasses import dataclass

try:
    from eth_utils import is_checksum_address
except ImportError:
    is_checksum_address = None


ETHEREUM_ADDRESS_PATTERN = re.compile(r"^0x[a-fA-F0-9]{40}$")
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
BURN_ADDRESS = "0x000000000000000000000000000000000000dead"


class WalletValidationError(ValueError):
    pass


@dataclass
class WalletValidationResult:
    original_address: str
    normalized_address: str
    validation_level: str
    risk_flags: list[str]
    notes: list[str]


def validate_wallet_address(wallet_address: str) -> WalletValidationResult:
    if not isinstance(wallet_address, str):
        raise WalletValidationError("wallet_address must be a string")

    original_address = wallet_address
    cleaned_address = wallet_address.strip()

    if not cleaned_address:
        raise WalletValidationError("wallet_address is required")

    if not cleaned_address.startswith("0x"):
        raise WalletValidationError("wallet_address must start with 0x")

    if len(cleaned_address) != 42:
        raise WalletValidationError("wallet_address must be 42 characters long")

    if not ETHEREUM_ADDRESS_PATTERN.fullmatch(cleaned_address):
        raise WalletValidationError(
            "wallet_address must contain only hexadecimal characters"
        )

    normalized_address = cleaned_address.lower()

    if normalized_address == ZERO_ADDRESS:
        raise WalletValidationError("zero address is not a usable wallet address")

    risk_flags = []
    notes = []

    if normalized_address == BURN_ADDRESS:
        risk_flags.append("burn_address")
        notes.append("Address is a known burn address, not a normal user wallet.")

    has_mixed_case = (
        cleaned_address != cleaned_address.lower()
        and cleaned_address != cleaned_address.upper()
    )
    if has_mixed_case and is_checksum_address:
        if not is_checksum_address(cleaned_address):
            raise WalletValidationError(
                "mixed-case wallet_address has an invalid EIP-55 checksum"
            )
        notes.append("Mixed-case address passed EIP-55 checksum validation.")
    elif has_mixed_case:
        notes.append(
            "Mixed-case address accepted; install eth-utils to enforce EIP-55 checksum validation."
        )

    return WalletValidationResult(
        original_address=original_address,
        normalized_address=normalized_address,
        validation_level="layer_1",
        risk_flags=risk_flags,
        notes=notes,
    )
