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
- Planned: Redis/Celery
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
