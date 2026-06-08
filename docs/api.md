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
X-API-Key: ihvTVHSFofSflJ364BzdSHyfS3KjABzg5BXOlseGzCM
```

If the header is missing or wrong, the API returns:

```json
{
  "detail": "Invalid or missing API key"
}
```
g
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
    "behavior_fingerprint_hash": "hash...",
    "issued_at": "2026-06-07T12:00:00+00:00",
    "expires_at": "2026-06-08T12:00:00+00:00",
    "valid_for_hours": 24
  },
  "storage_status": "stored",
  "message": "Reusable wallet trust proof generated."
}
```

## Error Responses

Invalid wallet format:

```json
{
  "detail": "wallet_address must be 42 characters long"
}
```

Missing or invalid API key:

```json
{
  "detail": "Invalid or missing API key"
}
```
