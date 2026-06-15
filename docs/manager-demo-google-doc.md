# Manager Demo Commands

Author: Austin Li  
Date: June 11, 2026  
Project: Web3 Proof-of-Human Trust API

## 1. Start Backend

```bash
cd "/Users/austinlilyx1/Downloads/Innovation AI bot detection"
venv/bin/uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Show endpoints:

```text
GET  /
POST /check_wallet
POST /extract_features
POST /score_wallet
POST /generate_proof
POST /verify_proof
```

## 2. Start Dashboard

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
X-API-Key: value from TRUST_API_KEY in .env
Wallet address: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e
```

Click:

```text
Check Wallet
Generate Proof
Verify Proof
```

## 3. Health Check

```bash
curl http://127.0.0.1:8000/
```

## 4. Check Wallet

```bash
curl -X POST "http://127.0.0.1:8000/check_wallet" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"wallet_address":"0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}'
```

Show:

```text
human_likelihood
trust_tier
confidence_score
risk_flags
storage_status
```

## 5. Generate Proof

```bash
curl -X POST "http://127.0.0.1:8000/generate_proof" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"wallet_address":"0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}'
```

Copy:

```text
proof.proof_id
```

## 6. Verify Proof

```bash
curl -X POST "http://127.0.0.1:8000/verify_proof" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"proof_id":"PASTE_PROOF_ID_HERE"}'
```

Show:

```text
is_valid
status
message
```

## 7. Error Handling

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

## 8. Database Counts

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

Current seeded result:

```text
wallets 104
feature_snapshots 125
score_snapshots 125
proof_snapshots 10
```

## 9. Run Tests

```bash
venv/bin/python -m unittest discover -s tests -v
```

Expected:

```text
Ran 24 tests
OK
```

## 10. Seed 100 Real Wallets

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

## Demo Summary

```text
Week 3 completed:
- Authenticated trust API
- Feature extraction and scoring endpoints
- Proof generation
- Proof verification
- Supabase storage
- Rate limiting
- Logging and error handling
- API documentation

Week 4 started:
- React dashboard
- 100 real Ethereum addresses seeded into database
```
