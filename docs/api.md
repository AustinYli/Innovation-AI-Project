# Proof-of-Human Trust API

Base URL for local development:

```text
http://127.0.0.1:8000
```

Interactive FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

## Authentication

Protected endpoints require an API key header:

```text
X-API-Key: YOUR_TRUST_API_KEY
```

If the header is missing or wrong, the API returns:

```json
{
  "detail": "Invalid or missing API key"
}
```

## Week 5 Readiness Endpoints

These endpoints make the deployed API easier to monitor and integrate.

### Health check

```bash
curl -X GET "http://127.0.0.1:8000/health"
```

Use this for Railway checks, uptime checks, and quick deployment verification.

Example response:

```json
{
  "service": "wallet_trust_api",
  "version": "0.1.0",
  "status": "ok",
  "checks": {
    "database": {
      "status": "connected",
      "configured": true
    },
    "etherscan": {
      "status": "configured",
      "configured": true
    },
    "auth": {
      "status": "configured",
      "configured": true
    }
  },
  "message": "Service is ready."
}
```

### Safe environment debug

```bash
curl -X GET "http://127.0.0.1:8000/debug/env" \
  -H "X-API-Key: YOUR_TRUST_API_KEY"
```

Use this to confirm required environment variables exist without printing secret values.

Example response:

```json
{
  "service": "wallet_trust_api",
  "version": "0.1.0",
  "environment": {
    "alchemy_api_key": {
      "configured": true
    },
    "etherscan_api_key": {
      "configured": true
    },
    "database_url": {
      "configured": true
    },
    "trust_api_key": {
      "configured": true
    },
    "proof_secret": {
      "configured": true
    }
  },
  "runtime": {
    "cors_origins_count": 3,
    "rate_limit_requests": 60,
    "rate_limit_window_seconds": 60,
    "proof_valid_for_hours": 24,
    "log_level": "INFO"
  },
  "message": "Environment check loaded without exposing secret values."
}
```

## Rate Limiting

Protected endpoints are rate limited per API key, client host, and endpoint path.

Default local settings:

```text
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=60
```

If a client sends too many requests, the API returns:

```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

The response also includes a `Retry-After` header telling the client how many seconds to wait.

## Week 3 Proof Flow

This is the main trust-proof workflow for an external app or developer integration.

### 1. Check wallet trust

```bash
curl -X POST "http://127.0.0.1:8000/check_wallet" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"wallet_address":"0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}'
```

Use this when an app only needs a compact wallet trust result.

### 2. Generate reusable proof

```bash
curl -X POST "http://127.0.0.1:8000/generate_proof" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"wallet_address":"0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}'
```

Copy the returned `proof.proof_id`.

### 3. Verify proof later

```bash
curl -X POST "http://127.0.0.1:8000/verify_proof" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"proof_id":"proof_abc123..."}'
```

Use this when another app needs to check whether a saved proof is still `active`, `expired`, or `not_found`.

### Endpoint Roles

```text
/check_wallet      High-level wallet trust summary
/extract_features  Internal/debug feature extraction view
/score_wallet      Detailed scoring view with rule breakdown
/analyze_sybil     Focused wallet relationships, clustering, and Sybil risk
/generate_proof    Creates and stores a reusable trust proof
/verify_proof      Checks whether a proof is valid right now
/jobs/score_wallet Submits scoring to a background worker
/jobs/{job_id}     Checks background scoring job status
/jobs/{job_id}/events Streams near real-time job status updates
/metrics           Runtime request, latency, error, and job metrics
/cache/stats       Wallet pipeline cache health
/health            Production readiness check
/debug/env         Safe environment configuration check
/dashboard/summary          Dashboard totals from Supabase/Postgres
/dashboard/recent_wallets   Latest stored wallets and scores
/dashboard/flagged_wallets  Latest wallets with risk flags
```

## Week 6 Sybil Analysis

Analyze wallet relationships, behavior clustering, and Sybil risk:

```bash
curl -X POST "http://127.0.0.1:8000/analyze_sybil" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"wallet_address":"0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}'
```

Important response fields:

```text
behavior_fingerprint_hash
funding_sources
transaction_graph_connection_count
cluster_id
cluster_size
cluster_methods
related_wallet_count
related_wallet_addresses
relationship_edges
shared_funding_wallet_count
behavior_match_wallet_count
max_counterparty_overlap_ratio
sybil_risk_score
sybil_risk_level
sybil_signals
```

The endpoint compares the wallet with the latest stored feature snapshot for other wallets. Analyze and store multiple wallets through `/check_wallet` to populate useful peer data.

## Week 7 Production Hardening

### Submit async score job

```bash
curl -X POST "http://127.0.0.1:8000/jobs/score_wallet" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"wallet_address":"0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}'
```

Example response:

```json
{
  "job_id": "job_abc123",
  "job_type": "score_wallet",
  "status": "queued",
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
  "created_at": "2026-07-15T12:00:00+00:00",
  "started_at": null,
  "completed_at": null,
  "found": true,
  "message": "Background job is queued."
}
```

### Check async job status

```bash
curl -X GET "http://127.0.0.1:8000/jobs/job_abc123" \
  -H "X-API-Key: YOUR_TRUST_API_KEY"
```

When complete, `result` contains the same detailed output as `/score_wallet`.

### Stream async job events

```bash
curl -N -X GET "http://127.0.0.1:8000/jobs/job_abc123/events" \
  -H "X-API-Key: YOUR_TRUST_API_KEY"
```

This uses server-sent events so a frontend can update as the job moves through queued, running, completed, or failed states.

### Metrics

```bash
curl -X GET "http://127.0.0.1:8000/metrics" \
  -H "X-API-Key: YOUR_TRUST_API_KEY"
```

Returns uptime, request count, error rate, latency, status-code counts, path counts, and background job counts.

### Cache stats

```bash
curl -X GET "http://127.0.0.1:8000/cache/stats" \
  -H "X-API-Key: YOUR_TRUST_API_KEY"
```

Returns cache enabled status, TTL, entry count, hits, misses, and hit rate.

## Week 8 Developer Assets

Developer-facing assets:

```text
sdk/python
sdk/node
postman/trustapi.postman_collection.json
examples/creator-platform-verification
docs/final-demo-presentation.md
```

## Week 4 Dashboard Flow

These endpoints power the internal React dashboard.

### Dashboard summary

```bash
curl -X GET "http://127.0.0.1:8000/dashboard/summary" \
  -H "X-API-Key: YOUR_TRUST_API_KEY"
```

Example response:

```json
{
  "database_status": "connected",
  "total_wallets": 104,
  "total_feature_snapshots": 125,
  "total_score_snapshots": 125,
  "total_proofs": 10,
  "tier_distribution": {
    "gold": 4,
    "silver": 66,
    "bronze": 55
  },
  "human_likelihood_distribution": {
    "high": 4,
    "medium": 78,
    "low": 43
  },
  "flagged_wallet_count": 6,
  "message": "Dashboard summary loaded."
}
```

### Recent wallets

```bash
curl -X GET "http://127.0.0.1:8000/dashboard/recent_wallets?limit=8" \
  -H "X-API-Key: YOUR_TRUST_API_KEY"
```

Returns the newest wallet rows stored in the database with the latest score summary for each wallet.

### Flagged wallets

```bash
curl -X GET "http://127.0.0.1:8000/dashboard/flagged_wallets?limit=8" \
  -H "X-API-Key: YOUR_TRUST_API_KEY"
```

Returns wallets whose latest score has at least one risk flag.

## GET /

Health check endpoint.

### Response

```json
{
  "message": "Proof-of-Human Trust API is running",
  "status": "ok"
}
```

## POST /check_wallet

Public high-level trust check. This endpoint validates the wallet, extracts features, computes a score, stores wallet/feature/score snapshots when the database is configured, and returns a compact summary.

### Request

```json
{
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
}
```

### Response

```json
{
  "wallet_id": 1,
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
  "normalized_wallet_address": "0x742d35cc6634c0532925a3b844bc454e4438f44e",
  "is_valid": true,
  "human_likelihood": "high",
  "trust_tier": "gold",
  "confidence_score": 0.87,
  "risk_flags": ["high_velocity_activity"],
  "storage_status": "stored",
  "summary": "Wallet is classified as high human likelihood with gold trust tier."
}
```

## POST /extract_features

Internal/debug endpoint for viewing validation, provider data, and computed features. It does not return a final score.

### Request

```json
{
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
}
```

### Response

Returns:

```text
wallet_address
normalized_wallet_address
is_valid
validation
provider_profile
features
message
```

## POST /score_wallet

Internal/debug endpoint for viewing features plus score details. It does not return the raw provider profile.

### Request

```json
{
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
}
```

### Response

Returns:

```text
wallet_address
normalized_wallet_address
is_valid
validation
features
human_likelihood
trust_tier
confidence_score
score_breakdown
risk_flags
message
```

## POST /generate_proof

Generates a reusable wallet trust proof. The proof includes a privacy-safe behavior fingerprint hash and does not expose raw provider data or raw feature details.

### Request

```json
{
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
}
```

### Response

```json
{
  "wallet_id": 1,
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
  "normalized_wallet_address": "0x742d35cc6634c0532925a3b844bc454e4438f44e",
  "human_likelihood": "high",
  "trust_tier": "gold",
  "confidence_score": 0.87,
  "risk_flags": ["high_velocity_activity"],
  "proof": {
    "proof_id": "proof_abc123...",
    "proof_version": "v1",
    "status": "active",
    "revocable": true,
    "behavior_fingerprint_hash": "hash...",
    "issued_at": "2026-06-07T12:00:00+00:00",
    "valid_until": "2026-06-08T12:00:00+00:00",
    "valid_for_hours": 24
  },
  "storage_status": "stored",
  "message": "Reusable wallet trust proof generated."
}
```

## POST /verify_proof

Verifies whether a previously generated proof is usable right now. This endpoint looks up the proof in Postgres/Supabase and returns `active`, `expired`, `not_found`, or `unavailable`.

### Request

```json
{
  "proof_id": "proof_abc123..."
}
```

### Active Response

```json
{
  "proof_id": "proof_abc123...",
  "is_valid": true,
  "status": "active",
  "wallet_id": 1,
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
  "normalized_wallet_address": "0x742d35cc6634c0532925a3b844bc454e4438f44e",
  "human_likelihood": "high",
  "trust_tier": "gold",
  "confidence_score": 0.87,
  "issued_at": "2026-06-07T12:00:00+00:00",
  "valid_until": "2026-06-08T12:00:00+00:00",
  "revocable": true,
  "message": "Proof is valid and active."
}
```

### Not Found Response

```json
{
  "proof_id": "proof_fake",
  "is_valid": false,
  "status": "not_found",
  "wallet_id": null,
  "wallet_address": null,
  "normalized_wallet_address": null,
  "human_likelihood": null,
  "trust_tier": null,
  "confidence_score": null,
  "issued_at": null,
  "valid_until": null,
  "revocable": null,
  "message": "Proof was not found."
}
```

## Error Responses

Invalid wallet format:

```json
{
  "error": "wallet_validation_error",
  "detail": "wallet_address must be 42 characters long"
}
```

Missing or invalid API key:

```json
{
  "detail": "Invalid or missing API key"
}
```

Too many requests:

```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

Unexpected server error:

```json
{
  "error": "internal_server_error",
  "detail": "Unexpected server error. Check server logs for details."
}
```
