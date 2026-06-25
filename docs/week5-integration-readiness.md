# Week 5 Integration Readiness

Week 5 focuses on making the deployed MVP easier for another developer or manager to test without reading the codebase.

## Added

- `GET /health`
  - Checks whether the API is running and whether required dependencies are configured.
  - Reports database, Etherscan, and API auth readiness.

- `GET /debug/env`
  - Confirms important environment variables exist.
  - Does not print secret values.
  - Requires `X-API-Key`.

- Updated developer simulation
  - `scripts/simulate_developer_usage.py` now checks `/health`, `/debug/env`, wallet scoring, proof generation, proof verification, and dashboard summary.

- Updated benchmark script
  - `scripts/benchmark_api.py` now includes `/health` and `/debug/env`.

- Added tests
  - Health/debug service tests.
  - Updated simulation/benchmark tests.

## Commands

Run local tests:

```bash
venv/bin/python -m unittest discover -s tests -v
```

Check deployed health:

```bash
curl -X GET "https://innovation-ai-project-production.up.railway.app/health"
```

Check deployed environment configuration safely:

```bash
curl -X GET "https://innovation-ai-project-production.up.railway.app/debug/env" \
  -H "X-API-Key: YOUR_TRUST_API_KEY"
```

Run full developer simulation:

```bash
venv/bin/python scripts/simulate_developer_usage.py \
  --base-url "https://innovation-ai-project-production.up.railway.app"
```

Run performance benchmark:

```bash
venv/bin/python scripts/benchmark_api.py \
  --base-url "https://innovation-ai-project-production.up.railway.app" \
  --requests 5 \
  --output docs/week4-performance-results.json
```

## Manager Summary

Week 5 turns the project from a working demo into a more integration-ready API. A developer can now check whether the deployed service is healthy, confirm configuration safely, run one script that exercises the full API workflow, and benchmark the deployed endpoints.
