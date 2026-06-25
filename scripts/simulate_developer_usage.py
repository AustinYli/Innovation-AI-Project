import argparse
import json
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return None

from scripts.api_client import ApiRequestError, TrustApiClient

DEFAULT_WALLET = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"


def run_simulation(client: TrustApiClient, wallet_address: str) -> dict:
    steps = []

    def run_step(name: str, method: str, path: str, payload: dict | None = None):
        result = client.request(method, path, payload)
        steps.append({
            "name": name,
            "status_code": result.status_code,
            "elapsed_ms": result.elapsed_ms,
        })
        print(
            f"[PASS] {name:<22} status={result.status_code} "
            f"elapsed_ms={result.elapsed_ms}",
            flush=True,
        )
        return result.data

    health = run_step("health check", "GET", "/health")
    debug_env = run_step("debug env", "GET", "/debug/env")
    wallet = run_step(
        "check wallet",
        "POST",
        "/check_wallet",
        {"wallet_address": wallet_address},
    )
    proof_response = run_step(
        "generate proof",
        "POST",
        "/generate_proof",
        {"wallet_address": wallet_address},
    )
    proof_id = proof_response["proof"]["proof_id"]
    verification = run_step(
        "verify proof",
        "POST",
        "/verify_proof",
        {"proof_id": proof_id},
    )
    dashboard = run_step("dashboard summary", "GET", "/dashboard/summary")

    return {
        "simulation_status": "passed",
        "base_url": client.base_url,
        "wallet_address": wallet_address,
        "health_status": health.get("status"),
        "configured_environment_keys": [
            key
            for key, value in debug_env.get("environment", {}).items()
            if value.get("configured")
        ],
        "human_likelihood": wallet.get("human_likelihood"),
        "trust_tier": wallet.get("trust_tier"),
        "confidence_score": wallet.get("confidence_score"),
        "proof_id": proof_id,
        "proof_status": verification.get("status"),
        "dashboard_total_wallets": dashboard.get("total_wallets"),
        "steps": steps,
    }


def parse_args():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Simulate an external developer using the Trust API end to end."
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("TRUST_API_BASE_URL", "http://127.0.0.1:8000"),
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("TRUST_API_KEY") or os.getenv("API_KEY"),
    )
    parser.add_argument("--wallet", default=DEFAULT_WALLET)
    parser.add_argument("--timeout", type=float, default=45)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.api_key:
        print("Missing API key. Set TRUST_API_KEY or pass --api-key.")
        return 2

    client = TrustApiClient(
        base_url=args.base_url,
        api_key=args.api_key,
        timeout_seconds=args.timeout,
    )

    print(f"Simulating developer usage against {client.base_url}\n", flush=True)
    try:
        summary = run_simulation(client, args.wallet)
    except (ApiRequestError, KeyError) as error:
        print(f"\n[FAIL] Simulation stopped: {error}")
        return 1

    print("\nSimulation summary")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
