# Week 8 - Developer SDK, Integration & Final Demo

## What Was Added

Week 8 focuses on developer adoption and final presentation polish.

## SDKs

Python SDK:

```text
sdk/python/trustapi/client.py
```

Node.js SDK:

```text
sdk/node/index.js
```

Both SDKs support:

- check wallet
- score wallet
- analyze Sybil risk
- generate proof
- verify proof
- submit async score job
- get async job status

## Sample Integration App

Example app:

```text
examples/creator-platform-verification/index.html
```

This demonstrates a creator platform using TrustAPI to approve, review, or block a creator wallet.

Run locally:

```bash
venv/bin/python -m http.server 5180 --directory examples/creator-platform-verification
```

Open:

```text
http://127.0.0.1:5180
```

## Postman Collection

Postman collection:

```text
postman/trustapi.postman_collection.json
```

Import it into Postman and set:

```text
base_url
trust_api_key
wallet_address
```

## Final Demo Flow

1. Open deployed frontend dashboard.
2. Check a wallet.
3. Generate a proof.
4. Verify the proof.
5. Analyze Sybil cluster graph.
6. Submit async scoring job.
7. Show `/metrics` and `/cache/stats`.
8. Show SDK files and sample creator platform integration.

## Final Talking Points

- The API validates wallets and extracts live blockchain features.
- The scoring engine includes human likelihood, trust tiers, risk flags, and Sybil risk.
- The proof flow lets other apps verify trust without rerunning the full analysis every time.
- Supabase stores wallet, feature, score, and proof snapshots.
- Railway hosts the backend and frontend so users do not need Austin's local computer.
- SDKs, Postman, and the sample app make the system easier for developers to integrate.
