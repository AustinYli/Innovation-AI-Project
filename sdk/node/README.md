# TrustAPI Node.js SDK

Minimal Node.js client for the Proof-of-Human Trust API.

```js
import { TrustApiClient } from "./index.js";

const client = new TrustApiClient({
  apiKey: process.env.TRUST_API_KEY,
});

const wallet = await client.checkWallet(
  "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
);

console.log(wallet.human_likelihood, wallet.trust_tier);
```

For local development:

```js
const client = new TrustApiClient({
  apiKey: "test-secret",
  baseUrl: "http://127.0.0.1:8000",
});
```
