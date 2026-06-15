import argparse
from pathlib import Path
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.session import init_db
from app.services.etherscan_client import EtherscanClient
from app.services.wallet_service import ingest_wallet


def discover_recent_addresses(limit: int, max_blocks: int) -> list[str]:
    client = EtherscanClient(timeout_seconds=20)
    latest_block = client.get_latest_block_number()
    if latest_block is None:
        raise RuntimeError("Could not fetch latest block number from Etherscan.")

    addresses = []
    seen = set()

    for block_number in range(latest_block, latest_block - max_blocks, -1):
        block = client.get_block_by_number(block_number)
        if not block:
            continue

        for transaction in block.get("transactions", []):
            for key in ("from", "to"):
                address = transaction.get(key)
                if not address:
                    continue

                normalized = address.lower()
                if normalized in seen:
                    continue

                seen.add(normalized)
                addresses.append(address)

                if len(addresses) >= limit:
                    return addresses

    return addresses


def seed_wallets(limit: int, max_blocks: int, sleep_seconds: float) -> dict:
    init_db()
    addresses = discover_recent_addresses(limit=limit, max_blocks=max_blocks)

    summary = {
        "requested": limit,
        "discovered": len(addresses),
        "stored": 0,
        "failed": 0,
        "wallet_ids": [],
        "failures": [],
    }

    for index, address in enumerate(addresses, start=1):
        try:
            result = ingest_wallet(address)
            summary["stored"] += 1
            summary["wallet_ids"].append(result["wallet_id"])
            print(
                f"[{index}/{len(addresses)}] stored wallet_id={result['wallet_id']} "
                f"tier={result['trust_tier']} likelihood={result['human_likelihood']} "
                f"address={address}"
            )
        except Exception as error:
            summary["failed"] += 1
            summary["failures"].append({
                "address": address,
                "error": str(error),
            })
            print(f"[{index}/{len(addresses)}] failed address={address} error={error}")

        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    summary["wallet_ids"] = sorted(
        value for value in set(summary["wallet_ids"]) if value is not None
    )
    return summary


def parse_args():
    parser = argparse.ArgumentParser(
        description="Seed Supabase/Postgres with real Ethereum addresses from recent blocks."
    )
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--max-blocks", type=int, default=25)
    parser.add_argument("--sleep", type=float, default=0.25)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    final_summary = seed_wallets(
        limit=args.limit,
        max_blocks=args.max_blocks,
        sleep_seconds=args.sleep,
    )

    print("\nSeed summary")
    for key, value in final_summary.items():
        if key != "failures":
            print(f"{key}: {value}")

    if final_summary["failures"]:
        print("failures:")
        for failure in final_summary["failures"]:
            print(f"- {failure['address']}: {failure['error']}")
