# Week 5 Advanced Bot Detection

Focus: smarter scoring through data enrichment and transparent bot-detection heuristics.

## Data Sources

- Etherscan
  - Native balance
  - Transaction count
  - Contract code check
  - Normal transaction samples
  - ERC721 transfer samples
  - ERC1155 transfer samples

- Alchemy
  - Asset transfer samples
  - Incoming/outgoing transfer activity
  - Transfer categories
  - NFT transfer activity
  - Additional counterparty enrichment

Alchemy is optional. If `ALCHEMY_API_KEY` is missing or the API call fails, the wallet pipeline still runs using Etherscan data.

## Advanced Features Added

- `transaction_diversity_ratio`
  - Unique counterparties divided by sampled transaction count.

- `contract_interaction_ratio`
  - Contract-style transaction calls divided by sampled transaction count.

- `transaction_entropy`
  - Normalized entropy score for counterparty distribution.

- `max_transactions_per_hour`
  - Largest sampled one-hour transaction burst.

- `max_transactions_per_day`
  - Largest sampled one-day transaction burst.

- `repeated_contract_loop_count`
  - Repeated contract interactions beyond unique contract counterparties.

- `nft_transfer_sample_size`
  - ERC721/ERC1155 activity from Etherscan or Alchemy samples.

- `has_nft_activity`
  - Boolean flag for sampled NFT activity.

## Bot Detection Heuristics Added

- Burst activity
  - Flags wallets with many transactions in a short time window.

- Repeated contract loops
  - Flags wallets that repeatedly call the same contract pattern.

- Short lifespan wallets
  - Flags very new wallets with meaningful activity.

- Low transaction diversity
  - Flags wallets whose activity concentrates around very few counterparties.

- Low transaction entropy
  - Flags wallets whose transaction pattern is highly repetitive.

- High contract interaction ratio
  - Flags wallets whose sampled activity is dominated by contract calls.

## New Risk Flags

- `low_transaction_diversity`
- `low_transaction_entropy`
- `high_contract_interaction_ratio`
- `hourly_burst_activity`
- `daily_burst_activity`
- `repeated_contract_loops`
- `short_lifespan_wallet`

## Deliverables Completed

- Enhanced scoring engine
- Bot detection rules
- NFT activity enrichment
- Alchemy enrichment layer
- Updated risk flags
- Updated scoring documentation
- Tests for advanced feature extraction and scoring behavior
