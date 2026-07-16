# Wallet Trust Dashboard

The dashboard includes an interactive Week 6 Sybil relationship map. Enter a wallet and select **Analyze Sybil Cluster** to visualize funding sources, related wallets, cluster evidence, and network risk.

React dashboard for the FastAPI wallet trust backend.

## Run locally

Start the FastAPI backend from the project root:

```bash
venv/bin/uvicorn app.main:app --reload
```

Start the dashboard from the `frontend` folder:

```bash
cd frontend
../venv/bin/python -m http.server 5173
```

Open:

```text
http://127.0.0.1:5173
```

The dashboard calls:

```text
POST /check_wallet
POST /generate_proof
POST /verify_proof
```

Use the same `TRUST_API_KEY` value from your `.env` in the dashboard's `X-API-Key` input.
