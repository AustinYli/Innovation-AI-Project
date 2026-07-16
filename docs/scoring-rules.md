# Wallet Scoring Rules

This document explains the first heuristic scoring system used by the Proof-of-Human Trust API.

The score starts at `0.50`, then adds or subtracts points based on wallet features. The final score is clamped between `0.00` and `1.00`.

## Output Mapping

### Human Likelihood

- `0.75` to `1.00`: `high`
- `0.45` to `0.7499`: `medium`
- `0.00` to `0.4499`: `low`

### Trust Tier

- `0.80` to `1.00`: `gold`
- `0.55` to `0.7999`: `silver`
- `0.00` to `0.5499`: `bronze`

## Point Rules

### Data Quality

- `+0.05` if live provider data is available.
- `-0.05` if live provider data is unavailable.

### Native Balance

- `+0.12` if the wallet is `funded`.
- `+0.03` if the wallet has a `low` balance.
- `-0.05` if the wallet has only `dust` balance.
- `-0.15` if the wallet is `empty`.

### Transaction Activity

- `+0.12` for `high` activity.
- `+0.08` for `moderate` activity.
- `-0.05` for `low` activity.
- `-0.20` for `none`.

### Wallet Age

- `+0.12` if the wallet is at least 365 days old.
- `+0.08` if the wallet is at least 90 days old.
- `+0.03` if the wallet is at least 30 days old.
- `-0.05` if the wallet is less than 30 days old.
- `-0.15` if the wallet is less than 7 days old.

### Counterparty Diversity

- `+0.08` if the wallet has at least 10 unique counterparties.
- `+0.04` if the wallet has at least 3 unique counterparties.
- `-0.08` if the wallet has more than 10 transactions but fewer than 3 unique counterparties.
- `+0.05` if transaction diversity ratio is at least `0.35`.
- `-0.12` if transaction diversity ratio is below `0.10` after at least 20 transactions.

### Transaction Entropy

- `+0.04` if normalized transaction entropy is at least `0.70`.
- `-0.12` if normalized transaction entropy is below `0.25` after at least 20 transactions.

### Activity Frequency

- `+0.05` if the wallet has steady activity frequency between `0.1` and `10` transactions per day.
- `-0.18` if the wallet has more than `20` transactions per day and fewer than `5` unique counterparties.
- `-0.08` if the wallet has more than `100` transactions per day.

### Burst Activity

- `-0.15` if at least 20 sampled transactions happen inside a one-hour window.
- `-0.10` if at least 80 sampled transactions happen inside a one-day window.

### Contract Interaction Behavior

- `+0.02` if contract interaction ratio is at most `0.50`.
- `-0.12` if contract interaction ratio is at least `0.80` after at least 20 transactions.
- `-0.18` if repeated contract loop count is at least `10`.

### Contract Address

- `-0.30` if the address has contract code.

### Short Lifespan Wallets

- `-0.15` if the wallet is less than 3 days old and already has at least 10 transactions.

### NFT and Alchemy Enrichment

- `+0.03` if Alchemy transfer enrichment is available.
- `+0.04` if sampled ERC721 or ERC1155 NFT activity is present.

### Week 6 Sybil Risk

- `-0.15` if network analysis reports `medium` Sybil risk.
- `-0.30` if network analysis reports `high` Sybil risk.
- Individual Sybil signals are copied into the final `risk_flags`.

## Week 5 Advanced Feature Inputs

Week 5 adds the following computed features:

- `transaction_diversity_ratio`
- `contract_interaction_ratio`
- `transaction_entropy`
- `max_transactions_per_hour`
- `max_transactions_per_day`
- `repeated_contract_loop_count`
- `nft_transfer_sample_size`
- `has_nft_activity`
- `alchemy_transfer_sample_size`
- `alchemy_unique_counterparty_count`
- `alchemy_transfer_categories`

## Week 5 Risk Flags

- `low_transaction_diversity`
- `low_transaction_entropy`
- `high_contract_interaction_ratio`
- `hourly_burst_activity`
- `daily_burst_activity`
- `repeated_contract_loops`
- `short_lifespan_wallet`

## Week 6 Relationship and Sybil Features

- `behavior_fingerprint_hash`
- `funding_sources`
- `transaction_graph_connection_count`
- `cluster_id`
- `cluster_size`
- `cluster_methods`
- `related_wallet_count`
- `shared_funding_wallet_count`
- `behavior_match_wallet_count`
- `max_counterparty_overlap_ratio`
- `sybil_risk_score`
- `sybil_risk_level`
- `sybil_signals`

## Week 6 Risk Flags

- `medium_sybil_risk`
- `high_sybil_risk`
- `shared_funding_source`
- `matching_behavior_fingerprint`
- `high_graph_overlap`
- `very_high_graph_overlap`
- `coordinated_burst_pattern`
- `repeated_contract_pattern`
- `short_lifespan_pattern`
- `low_behavior_diversity`

## Current Limitations

This is a heuristic scoring model, not a trained machine learning model. The rules are intentionally transparent so they can be reviewed, tested, and adjusted as the project adds more blockchain signals.
