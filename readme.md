# Proof-of-Human Trust API

This project is an 8-week AI Developer Internship MVP for a Web3 Reputation-as-a-Service system.

The API will eventually allow external applications to check whether a wallet looks human-like, trustworthy, bot-like, or Sybil-risky.

## Week 1 Status

Current implementation:

- FastAPI backend skeleton
- `/` health check endpoint
- `/check_wallet` wallet ingestion endpoint
- Placeholder wallet scoring response
- Initial project structure
- Architecture documentation

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Pydantic
- Planned: Postgres/Supabase
- Planned: Alchemy/Etherscan API
- Planned: Redis/Celery
- Planned: Streamlit or React dashboard

## Run Locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload