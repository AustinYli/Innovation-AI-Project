# Creator Platform Verification Demo

This is a small browser-only sample integration app. It shows how a creator platform could gate features by wallet trust tier.

## Run locally

From the project root:

```bash
venv/bin/python -m http.server 5180 --directory examples/creator-platform-verification
```

Open:

```text
http://127.0.0.1:5180
```

Use:

- API base URL: `https://innovation-ai-project-production.up.railway.app`
- API key: your `TRUST_API_KEY`
- Wallet: an Ethereum wallet address

The app calls `/check_wallet` and displays whether the creator account should be approved, reviewed, or blocked.
