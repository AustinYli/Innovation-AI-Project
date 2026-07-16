# Week 7 - Streaming, Performance & Production Hardening

## What Was Added

Week 7 adds reliability and production-readiness features around the existing wallet scoring pipeline.

## Async Pipeline

New endpoint:

```text
POST /jobs/score_wallet
```

This submits wallet scoring to an in-process background worker queue and immediately returns a `job_id`.

Check job state:

```text
GET /jobs/{job_id}
```

Stream near real-time job updates:

```text
GET /jobs/{job_id}/events
```

The current implementation uses Python `ThreadPoolExecutor` so it works locally and on Railway without Redis. In production, the same endpoint contract can be backed by Redis/Celery or another managed queue.

## Near Real-Time Scoring Updates

`/jobs/{job_id}/events` uses server-sent events. A client can subscribe to job status changes and update the UI when scoring moves from `queued` to `running` to `completed` or `failed`.

## Latency Optimization & Caching

The wallet feature pipeline now uses a TTL cache.

Default:

```text
CACHE_TTL_SECONDS=120
```

Monitoring endpoint:

```text
GET /cache/stats
```

The cache prevents repeated calls for the same wallet from immediately refetching Etherscan/Alchemy data.

## Monitoring

New endpoint:

```text
GET /metrics
```

Returns:

- uptime
- request count
- error count
- error rate
- average latency
- p95 latency
- max latency
- status code counts
- endpoint path counts
- background job counts

## Fault Tolerance

Existing hardening remains in place:

- API key authentication
- rate limiting
- structured request logs
- validation errors return HTTP 400
- unexpected errors return HTTP 500 with server logs
- provider/database failures degrade gracefully instead of crashing the API

## Commands

Submit a background scoring job:

```bash
curl -X POST "https://innovation-ai-project-production.up.railway.app/jobs/score_wallet" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"wallet_address":"0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}'
```

Check job status:

```bash
curl -X GET "https://innovation-ai-project-production.up.railway.app/jobs/JOB_ID" \
  -H "X-API-Key: YOUR_TRUST_API_KEY"
```

View metrics:

```bash
curl -X GET "https://innovation-ai-project-production.up.railway.app/metrics" \
  -H "X-API-Key: YOUR_TRUST_API_KEY"
```

View cache stats:

```bash
curl -X GET "https://innovation-ai-project-production.up.railway.app/cache/stats" \
  -H "X-API-Key: YOUR_TRUST_API_KEY"
```

Run benchmark:

```bash
venv/bin/python scripts/benchmark_api.py \
  --base-url "https://innovation-ai-project-production.up.railway.app" \
  --requests 5 \
  --include-wallet-check \
  --output docs/week7-performance-results.json
```
