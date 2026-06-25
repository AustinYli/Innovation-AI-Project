import argparse
import json
import os
from pathlib import Path
import statistics
import sys
import time

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


def percentile(values: list[float], percentile_value: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, round((len(ordered) - 1) * percentile_value))
    return ordered[index]


def summarize_latencies(latencies: list[float]) -> dict:
    return {
        "requests": len(latencies),
        "min_ms": round(min(latencies), 2),
        "mean_ms": round(statistics.mean(latencies), 2),
        "p50_ms": round(statistics.median(latencies), 2),
        "p95_ms": round(percentile(latencies, 0.95), 2),
        "max_ms": round(max(latencies), 2),
    }


def benchmark_endpoint(
    client: TrustApiClient,
    name: str,
    method: str,
    path: str,
    request_count: int,
    delay_seconds: float,
    payload: dict | None = None,
) -> dict:
    latencies = []
    failures = []

    for request_number in range(1, request_count + 1):
        try:
            result = client.request(method, path, payload)
            latencies.append(result.elapsed_ms)
            print(
                f"[{name}] {request_number}/{request_count} "
                f"status={result.status_code} elapsed_ms={result.elapsed_ms}",
                flush=True,
            )
        except ApiRequestError as error:
            failures.append(str(error))
            print(f"[{name}] {request_number}/{request_count} failed: {error}")

        if delay_seconds > 0 and request_number < request_count:
            time.sleep(delay_seconds)

    result = {
        "name": name,
        "method": method,
        "path": path,
        "successes": len(latencies),
        "failures": len(failures),
        "failure_details": failures,
    }
    if latencies:
        result.update(summarize_latencies(latencies))
    return result


def run_benchmark(
    client: TrustApiClient,
    request_count: int,
    delay_seconds: float,
    include_wallet_check: bool,
    wallet_address: str,
) -> dict:
    endpoints = [
        ("health", "GET", "/health", None),
        ("debug env", "GET", "/debug/env", None),
        ("dashboard summary", "GET", "/dashboard/summary", None),
        ("recent wallets", "GET", "/dashboard/recent_wallets?limit=8", None),
        ("flagged wallets", "GET", "/dashboard/flagged_wallets?limit=8", None),
    ]
    if include_wallet_check:
        endpoints.append((
            "check wallet",
            "POST",
            "/check_wallet",
            {"wallet_address": wallet_address},
        ))

    results = [
        benchmark_endpoint(
            client=client,
            name=name,
            method=method,
            path=path,
            request_count=request_count,
            delay_seconds=delay_seconds,
            payload=payload,
        )
        for name, method, path, payload in endpoints
    ]
    total_failures = sum(result["failures"] for result in results)
    return {
        "benchmark_status": "passed" if total_failures == 0 else "failed",
        "base_url": client.base_url,
        "requests_per_endpoint": request_count,
        "total_failures": total_failures,
        "results": results,
    }


def parse_args():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Measure sequential response latency for Trust API endpoints."
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("TRUST_API_BASE_URL", "http://127.0.0.1:8000"),
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("TRUST_API_KEY") or os.getenv("API_KEY"),
    )
    parser.add_argument("--requests", type=int, default=5)
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--include-wallet-check", action="store_true")
    parser.add_argument("--wallet", default=DEFAULT_WALLET)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.api_key:
        print("Missing API key. Set TRUST_API_KEY or pass --api-key.")
        return 2
    if args.requests < 1:
        print("--requests must be at least 1.")
        return 2

    client = TrustApiClient(
        base_url=args.base_url,
        api_key=args.api_key,
        timeout_seconds=args.timeout,
    )
    report = run_benchmark(
        client=client,
        request_count=args.requests,
        delay_seconds=args.delay,
        include_wallet_check=args.include_wallet_check,
        wallet_address=args.wallet,
    )

    rendered_report = json.dumps(report, indent=2)
    print("\nPerformance report")
    print(rendered_report)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(f"{rendered_report}\n", encoding="utf-8")
        print(f"\nSaved report to {args.output}")

    return 0 if report["benchmark_status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
