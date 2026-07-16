# TrustAPI Python SDK

Minimal Python client for the Proof-of-Human Trust API.

```python
from trustapi import TrustApiClient

client = TrustApiClient(api_key="YOUR_TRUST_API_KEY")

wallet = client.check_wallet("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
print(wallet["human_likelihood"], wallet["trust_tier"])

proof = client.generate_proof("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
verified = client.verify_proof(proof["proof"]["proof_id"])
print(verified["status"])
```

For local development:

```python
client = TrustApiClient(
    api_key="test-secret",
    base_url="http://127.0.0.1:8000",
)
```
