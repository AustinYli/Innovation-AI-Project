# Manager Demo Runbook

Author: Austin Li  
Project: Web3 Proof-of-Human Trust API  
Demo Date: June 11, 2026

## Demo Goal

Show that the project now has a working backend trust API, proof generation and verification flow, Supabase/Postgres storage, seeded wallet data, and a React dashboard for internal testing.

## What To Show First

Briefly explain the product in one sentence:

> This API checks an Ethereum wallet, extracts wallet behavior features, scores human likelihood, generates a reusable trust proof, and verifies that proof later.

Then show the system pieces:

- FastAPI backend
- Etherscan data source
- Supabase/Postgres database
- React dashboard
- API documentation

## 1. Start The Backend API

Open Terminal 1:

```bash
cd "/Users/austinlilyx1/Downloads/Innovation AI bot detection"
venv/bin/uvicorn app.main:app --reload
```

Expected:

```text
Uvicorn running on http://127.0.0.1:8000
```

What this proves:

- FastAPI server is running locally.
- Backend endpoints are ready to receive requests.

## 2. Open FastAPI Auto Docs

Open in browser:

```text
http://127.0.0.1:8000/docs
```

Show these endpoints:

- `POST /check_wallet`
- `POST /extract_features`
- `POST /score_wallet`
- `POST /generate_proof`
- `POST /verify_proof`

What this proves:

- FastAPI automatically generated interactive API documentation.
- The backend exposes the Week 3 trust and proof endpoints.

## 3. Start The React Dashboard

Open Terminal 2:

```bash
cd "/Users/austinlilyx1/Downloads/Innovation AI bot detection"
venv/bin/python -m http.server 5173
```

Open:

```text
http://127.0.0.1:5173/frontend/
```

Dashboard fields:

```text
API base URL: http://127.0.0.1:8000
X-API-Key: use TRUST_API_KEY from .env
Wallet address: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e
```

What this proves:

- Week 4 internal dashboard has started.
- The dashboard calls the FastAPI backend.

## 4. Dashboard Demo Flow

### A. Click Check Wallet

Expected screen:

```text
Wallet checked!
Human likelihood
Trust tier
Confidence
Wallet ID
Risk flags
```

Say:

> This calls `/check_wallet`, which validates the wallet, calls Etherscan, extracts features, computes a score, stores the result in Supabase, and returns a compact summary.

### B. Click Generate Proof

Expected screen:

```text
Your Trust Proof
Proof ID
Status: active
Issued
Valid Until
Revocable: Yes
```

Say:

> This calls `/generate_proof`, creates a reusable trust proof, stores it in the database, and returns a proof ID that another app can use later.

### C. Click Verify Proof

Expected screen:

```text
Proof is active
Status: active
Valid Right Now: Yes
Proof ID
Trust Tier
Valid Until
```

Say:

> This calls `/verify_proof`, looks up the proof in Supabase/Postgres, and checks whether it is active, expired, not found, or unavailable.

## 5. Curl Tests To Run

Use these if the manager wants to see the API directly without the dashboard.

Replace `YOUR_TRUST_API_KEY` with the value from `.env`.

### Health Check

```bash
curl http://127.0.0.1:8000/
```

Expected:

```json
{
  "message": "Proof-of-Human Trust API is running",
  "status": "ok"
}
```

### Check Wallet

```bash
curl -X POST "http://127.0.0.1:8000/check_wallet" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"wallet_address":"0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}'
```

Expected fields:

```text
wallet_id
human_likelihood
trust_tier
confidence_score
risk_flags
storage_status
```

### Generate Proof

```bash
curl -X POST "http://127.0.0.1:8000/generate_proof" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"wallet_address":"0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}'
```

Expected fields:

```text
proof.proof_id
proof.status
proof.revocable
proof.issued_at
proof.valid_until
human_likelihood
trust_tier
confidence_score
```

Copy the returned `proof.proof_id`.

### Verify Proof

```bash
curl -X POST "http://127.0.0.1:8000/verify_proof" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"proof_id":"PASTE_PROOF_ID_HERE"}'
```

Expected:

```text
is_valid: true
status: active
message: Proof is valid and active.
```

## 6. Show Error Handling

Run:

```bash
curl -i -X POST "http://127.0.0.1:8000/check_wallet" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"wallet_address":"bad"}'
```

Expected:

```json
{
  "error": "wallet_validation_error",
  "detail": "wallet_address must start with 0x"
}
```

What this proves:

- The API returns clean client-facing errors.
- Server logs still keep developer-side details.

## 7. Show Rate Limiting

Optional demo, only if there is time.

Start a test server with a tiny rate limit:

```bash
TRUST_API_KEY=test-secret RATE_LIMIT_REQUESTS=1 RATE_LIMIT_WINDOW_SECONDS=60 venv/bin/uvicorn app.main:app --reload --port 8007
```

Call the same request twice:

```bash
curl -i -X POST "http://127.0.0.1:8007/check_wallet" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-secret" \
  -d '{"wallet_address":"bad"}'
```

Expected first response:

```text
HTTP/1.1 400 Bad Request
```

Expected second response:

```text
HTTP/1.1 429 Too Many Requests
retry-after: ...
```

What this proves:

- Protected endpoints have API abuse protection.

## 8. Show Database Storage

Run:

```bash
venv/bin/python -c 'from collections import Counter; from sqlalchemy import select, func; from app.db.session import init_db, get_session_factory; from app.db.models import Wallet, WalletFeatureSnapshot, WalletScoreSnapshot, WalletProofSnapshot; init_db(); Session=get_session_factory();
with Session() as s:
 print("wallets", s.scalar(select(func.count()).select_from(Wallet)))
 print("feature_snapshots", s.scalar(select(func.count()).select_from(WalletFeatureSnapshot)))
 print("score_snapshots", s.scalar(select(func.count()).select_from(WalletScoreSnapshot)))
 print("proof_snapshots", s.scalar(select(func.count()).select_from(WalletProofSnapshot)))
 print("tiers", dict(Counter(s.scalars(select(WalletScoreSnapshot.trust_tier)).all())))
 print("human_likelihood", dict(Counter(s.scalars(select(WalletScoreSnapshot.human_likelihood)).all())))'
```

Expected based on current seeded data:

```text
wallets 104
feature_snapshots 125
score_snapshots 125
proof_snapshots 10
tiers {'gold': 4, 'silver': 66, 'bronze': 55}
human_likelihood {'high': 4, 'medium': 78, 'low': 43}
```

What this proves:

- Supabase/Postgres is connected.
- Wallets, features, scores, and proofs are being stored.
- The database has seeded real Ethereum wallet data.

## 9. Show Tests

Run:

```bash
venv/bin/python -m unittest discover -s tests -v
```

Expected:

```text
Ran 24 tests
OK
```

What this proves:

- Validation, auth, scoring, proof generation, proof verification, wallet service, and rate limiting tests pass.

## 10. Explain The 100 Wallet Seed

Say:

> I added a seed script that pulls real wallet addresses from recent Ethereum block transactions using Etherscan proxy endpoints. It processed 100 real addresses and stored all 100 successfully in Supabase.

Script:

```bash
venv/bin/python scripts/seed_wallets.py --limit 100 --max-blocks 60 --sleep 0.3
```

Result:

```text
requested: 100
discovered: 100
stored: 100
failed: 0
```

Important caveat:

> These are real Ethereum addresses, but they are not guaranteed to be real humans. They can include user wallets, exchanges, contracts, routers, bots, and service wallets. The current model returns heuristic human likelihood, not ground-truth identity.

## Best Demo Order

Use this order during the meeting:

1. Explain the product in one sentence.
2. Show FastAPI docs at `/docs`.
3. Show React dashboard.
4. Click `Check Wallet`.
5. Click `Generate Proof`.
6. Click `Verify Proof`.
7. Show Supabase table counts.
8. Run unit tests.
9. Explain what is done for Week 3 and what Week 4 adds.

## Current Status Summary

Week 3 completed:

- Trust API endpoints
- API key authentication
- Rate limiting
- Logging
- Error handling
- API documentation
- Proof generation
- Proof verification
- Supabase proof storage
- Backend tests

Week 4 started:

- React internal dashboard
- Seeded database with real Ethereum addresses

Next recommended work:

- Add dashboard views for recent wallets
- Add tier distribution chart
- Add flagged wallets table
- Add address label enrichment using Etherscan nametags or metadata
- Prepare deployment on Railway or another hosting service
