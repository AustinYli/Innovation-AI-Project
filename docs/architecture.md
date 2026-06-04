# Week 1 Architecture

## Project Goal

This project builds a Proof-of-Human Trust API for Web3 wallets. Given a wallet address, the system will eventually return human likelihood, trust tier, confidence score, risk flags, and proof information.

## MVP Architecture

User / Developer App
→ Trust API
→ Wallet Ingestion Service
→ Blockchain Data Provider
→ Feature Extraction Pipeline
→ Scoring Service
→ Database
→ API Response

## Week 1 Components

### 1. Trust API

Built with FastAPI. Provides endpoints such as:

- GET /
- POST /check_wallet

### 2. Wallet Ingestion Service

Receives a wallet address and returns a placeholder response. In later weeks, this service will connect to Alchemy or Etherscan.

### 3. Database

Planned database: Postgres or Supabase.

Initial planned tables:

- wallets
- wallet_features
- wallet_scores
- proofs

### 4. Future Scoring Pipeline

The scoring system will use features such as:

- wallet age
- activity frequency
- transaction count
- burst behavior
- transaction diversity
- contract interaction ratio
- shared funding sources
- Sybil risk signals

week 2:
