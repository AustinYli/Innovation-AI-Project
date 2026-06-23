# Week 4 Simulation and Performance

## Developer Usage Simulation

The simulation behaves like an external API customer. It performs this flow:

```text
GET /
POST /check_wallet
POST /generate_proof
POST /verify_proof
GET /dashboard/summary
```

Run against the local backend:

```bash
venv/bin/python scripts/simulate_developer_usage.py
```

Run against Railway:

```bash
venv/bin/python scripts/simulate_developer_usage.py \
  --base-url "https://innovation-ai-project-production.up.railway.app"
```

The script reads `TRUST_API_KEY` from `.env`. It never prints the key.

## Performance Benchmark

The default benchmark sends five sequential requests to each safe read endpoint:

```text
GET /
GET /dashboard/summary
GET /dashboard/recent_wallets?limit=8
GET /dashboard/flagged_wallets?limit=8
```

Run locally:

```bash
venv/bin/python scripts/benchmark_api.py
```

Run against Railway and save the JSON report:

```bash
venv/bin/python scripts/benchmark_api.py \
  --base-url "https://innovation-ai-project-production.up.railway.app" \
  --requests 5 \
  --output docs/week4-performance-results.json
```

To include `/check_wallet`, which calls Etherscan and stores new snapshots:

```bash
venv/bin/python scripts/benchmark_api.py --include-wallet-check
```

The report contains success/failure counts and minimum, mean, p50, p95, and maximum response times.

## Optimization Completed

The dashboard repository previously loaded every historical score snapshot into Python and discarded older rows. It now asks Postgres for only the latest score ID per wallet. The recent-wallet endpoint further limits that query to the wallets displayed on the current dashboard page.

This reduces database-to-API data transfer and Python memory usage as score history grows.

## Latest Railway Benchmark Finding

The first deployed benchmark confirmed that Railway health checks are working:

```text
Health mean: 118.28 ms
Health p95: 151.22 ms
Health failures: 0/3
```

Database-backed dashboard requests returned `500`. The Supabase pooler reported that the configured tenant/user was not found. Refresh `DATABASE_URL` in both local `.env` and the Railway backend service using the current Supabase connection string, redeploy the backend, and rerun the benchmark.

The complete machine-readable result is stored in `docs/week4-performance-results.json`.
