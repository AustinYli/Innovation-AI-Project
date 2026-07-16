# Proof-of-Human Trust API

This project is an 8-week AI Developer Internship MVP for a Web3 Reputation-as-a-Service system.

The API will eventually allow external applications to check whether a wallet looks human-like, trustworthy, bot-like, or Sybil-risky.

## Current MVP Status

Current implementation:

- FastAPI backend skeleton
- `/` health check endpoint
- `/check_wallet` wallet ingestion endpoint
- Etherscan-backed feature extraction and heuristic scoring
- Reusable proof generation and verification
- Supabase/Postgres snapshot storage
- API key authentication, rate limiting, logging, and error handling
- Advanced bot-detection scoring features for transaction diversity, entropy, burst activity, repeated contract loops, short lifespan wallets, contract interaction ratio, NFT activity, and Alchemy enrichment
- Sybil relationship modeling, wallet clustering, behavior fingerprints, and network risk scoring
- Async score jobs, cache stats, request metrics, and production monitoring endpoints
- Python SDK, Node.js SDK, Postman collection, and creator-platform integration demo
- React internal dashboard
- Railway backend and frontend deployment configuration
- Developer usage simulation and performance benchmark scripts
- Production readiness endpoints: `/health` and `/debug/env`
- Initial project structure
- Architecture documentation

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Pydantic
- Postgres/Supabase
- Etherscan API
- Optional future upgrade: Redis/Celery for distributed background jobs
- React dashboard

## Run Locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Week 4 Verification

Simulate an external developer using the complete API workflow:

```bash
venv/bin/python scripts/simulate_developer_usage.py \
  --base-url "https://innovation-ai-project-production.up.railway.app"
```

Run the deployed API benchmark:

```bash
venv/bin/python scripts/benchmark_api.py \
  --base-url "https://innovation-ai-project-production.up.railway.app" \
  --requests 5 \
  --output docs/week4-performance-results.json
```

## Week 5 Verification

Check deployed service readiness:

```bash
curl -X GET "https://innovation-ai-project-production.up.railway.app/health"
```

Check deployed configuration without exposing secrets:

```bash
curl -X GET "https://innovation-ai-project-production.up.railway.app/debug/env" \
  -H "X-API-Key: YOUR_TRUST_API_KEY"
```

## Week 6 Verification

Analyze wallet relationships and Sybil risk:

```bash
curl -X POST "https://innovation-ai-project-production.up.railway.app/analyze_sybil" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"wallet_address":"0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}'
```

## Week 7 Verification

Submit an async scoring job:

```bash
curl -X POST "https://innovation-ai-project-production.up.railway.app/jobs/score_wallet" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"wallet_address":"0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}'
```

Check metrics:

```bash
curl -X GET "https://innovation-ai-project-production.up.railway.app/metrics" \
  -H "X-API-Key: YOUR_TRUST_API_KEY"
```

Check cache stats:

```bash
curl -X GET "https://innovation-ai-project-production.up.railway.app/cache/stats" \
  -H "X-API-Key: YOUR_TRUST_API_KEY"
```

Run the production benchmark:

```bash
venv/bin/python scripts/benchmark_api.py \
  --base-url "https://innovation-ai-project-production.up.railway.app" \
  --requests 5 \
  --include-wallet-check \
  --output docs/week7-performance-results.json
```

## Week 8 Deliverables

- Python SDK: `sdk/python`
- Node.js SDK: `sdk/node`
- Postman collection: `postman/trustapi.postman_collection.json`
- Creator platform demo app: `examples/creator-platform-verification`
- Final demo notes: `docs/final-demo-presentation.md`
