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

### Activity Frequency

- `+0.05` if the wallet has steady activity frequency between `0.1` and `10` transactions per day.
- `-0.18` if the wallet has more than `20` transactions per day and fewer than `5` unique counterparties.
- `-0.08` if the wallet has more than `100` transactions per day.

### Contract Address

- `-0.30` if the address has contract code.

## Current Limitations

This is a heuristic scoring model, not a trained machine learning model. The rules are intentionally transparent so they can be reviewed, tested, and adjusted as the project adds more blockchain signals.
