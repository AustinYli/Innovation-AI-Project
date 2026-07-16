# Week 6 - Sybil Detection and Behavior Clustering

## Delivered

- Wallet relationship modeling from shared funding sources
- Compact transaction graph connections from sampled Etherscan transactions
- Database comparison against the latest snapshot for each known wallet
- Heuristic wallet clustering
- Deterministic SHA-256 behavior fingerprints
- A separate `0.00` to `1.00` Sybil risk score
- Sybil risk penalties in the main trust scoring engine
- `POST /analyze_sybil` for focused relationship analysis
- Interactive dashboard graph with wallet, funder, and related-wallet nodes

## Workflow

```text
Wallet address
  -> Etherscan transaction samples
  -> Identify early inbound funding sources
  -> Build unique directed transaction connections
  -> Compute behavior fingerprint
  -> Compare with stored wallet snapshots
  -> Group related wallets
  -> Compute Sybil risk
  -> Update trust score and risk flags
```

## Relationship Rules

A stored wallet is related to the analyzed wallet when at least one rule matches:

- Both wallets received funds from the same sampled funding source.
- Both wallets have the same behavior fingerprint.
- They share at least three counterparties and their counterparty Jaccard overlap is at least `0.50`.

The implementation uses transparent heuristic grouping. NetworkX is not required for the current MVP.

## Visual Relationship Map

The React dashboard includes an **Analyze Sybil Cluster** action. Its graph displays:

- The analyzed wallet as the center node
- Early inbound funding sources above the wallet
- Related stored wallets as peer nodes
- Shared-funding, behavior-fingerprint, and graph-overlap edges
- Cluster size, Sybil risk, graph overlap, active signals, and clustering methods

Clicking a node reveals its full address and connection explanation. When no related wallets are stored yet, the graph still displays the analyzed wallet and known funding sources.

## Behavior Fingerprint

The fingerprint is a deterministic SHA-256 hash of behavior buckets:

- Balance and activity level
- Transaction count range
- Wallet age range
- Activity frequency range
- Transaction diversity range
- Contract interaction range
- Transaction entropy range
- NFT and contract status
- Advanced bot behavior flags

The wallet address is excluded, allowing different wallets with similar behavior to produce the same fingerprint.

## Sybil Risk Rules

- Shared funding source: `+0.35`, plus `+0.05` for each additional matching wallet, capped at `0.50`
- Matching behavior fingerprint: `+0.20`, plus `+0.05` for each additional match, capped at `0.30`
- Counterparty overlap at least `0.75`: `+0.25`
- Counterparty overlap at least `0.50`: `+0.15`
- Burst pattern: `+0.12`
- Repeated contract pattern: `+0.12`
- Short lifespan pattern: `+0.10`
- Low diversity and low entropy together: `+0.10`

The final Sybil score is capped at `1.00`.

```text
0.00 - 0.2999  low
0.30 - 0.5999  medium
0.60 - 1.00    high
```

## Main Trust Score Updates

- Medium Sybil risk subtracts `0.15` from the trust score.
- High Sybil risk subtracts `0.30` from the trust score.
- Sybil signals are included in `risk_flags`.

## Storage

Week 6 fields are stored in the existing `wallet_feature_snapshots.features` JSON column. Raw relationship inputs are stored in `provider_profile`. No new Supabase table or database migration is required.

## Test

```bash
curl -X POST "http://127.0.0.1:8000/analyze_sybil" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_TRUST_API_KEY" \
  -d '{"wallet_address":"0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}'
```

For deployed Railway testing, replace the local base URL with:

```text
https://innovation-ai-project-production.up.railway.app
```

Run multiple wallets through `/check_wallet` first so the database contains peers that can be compared and clustered.

## MVP Limitation

The relationship graph is built from sampled Etherscan normal transactions and the wallet snapshots already stored by this application. A low Sybil score means no strong signal was found in the available sample; it does not prove that a wallet is not part of a Sybil network.
