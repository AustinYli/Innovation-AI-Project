# Final Demo Presentation

## Slide 1 - Project

Proof-of-Human Trust API for Web3 wallet reputation.

## Slide 2 - Problem

Apps need a way to detect bot-like, low-trust, or Sybil-risky wallets before giving access to rewards, creator tools, or community features.

## Slide 3 - Solution

TrustAPI analyzes wallet behavior, computes trust features, scores risk, and generates reusable trust proofs.

## Slide 4 - Architecture

```text
User / App
  -> Frontend Dashboard or SDK
  -> FastAPI Backend on Railway
  -> Etherscan + Alchemy
  -> Supabase/Postgres
  -> Trust score + proof + Sybil analysis
```

## Slide 5 - Core Endpoints

```text
POST /check_wallet
POST /score_wallet
POST /analyze_sybil
POST /generate_proof
POST /verify_proof
POST /jobs/score_wallet
GET  /metrics
GET  /cache/stats
```

## Slide 6 - Scoring Features

- wallet age
- activity frequency
- transaction diversity
- entropy
- contract interaction ratio
- NFT activity
- burst behavior
- repeated contract loops
- short lifespan wallets
- Sybil cluster signals

## Slide 7 - Sybil Detection

The system models wallet relationships using:

- shared funding sources
- behavior fingerprints
- transaction graph overlap
- related wallet clustering

## Slide 8 - Proof Flow

1. Analyze wallet.
2. Generate proof.
3. Store proof in Supabase.
4. Another app verifies proof by proof ID.

## Slide 9 - Production Hardening

- Railway deployment
- API key auth
- rate limiting
- logs
- metrics
- cache
- background jobs
- health/debug endpoints

## Slide 10 - Developer Adoption

- Python SDK
- Node.js SDK
- Postman collection
- sample creator verification app
- API docs

## Slide 11 - Demo

Run:

```bash
curl -X GET "https://innovation-ai-project-production.up.railway.app/health"
```

Then show the frontend dashboard and sample creator platform verification app.

## Slide 12 - Next Steps

- Replace in-process jobs with Redis/Celery.
- Add more labeled wallet datasets.
- Add model-based scoring after enough training data exists.
- Improve frontend analytics and admin views.
