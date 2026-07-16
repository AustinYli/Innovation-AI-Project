export class TrustApiError extends Error {
  constructor(message, statusCode = null, body = null) {
    super(message);
    this.name = "TrustApiError";
    this.statusCode = statusCode;
    this.body = body;
  }
}

export class TrustApiClient {
  constructor({
    apiKey,
    baseUrl = "https://innovation-ai-project-production.up.railway.app",
  }) {
    if (!apiKey) {
      throw new TrustApiError("apiKey is required");
    }
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async request(method, path, payload = null) {
    const response = await fetch(`${this.baseUrl}/${path.replace(/^\//, "")}`, {
      method,
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-API-Key": this.apiKey,
      },
      body: payload ? JSON.stringify(payload) : undefined,
    });
    const body = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new TrustApiError(
        body.detail || body.error || "TrustAPI request failed",
        response.status,
        body,
      );
    }

    return body;
  }

  checkWallet(walletAddress) {
    return this.request("POST", "/check_wallet", {
      wallet_address: walletAddress,
    });
  }

  scoreWallet(walletAddress) {
    return this.request("POST", "/score_wallet", {
      wallet_address: walletAddress,
    });
  }

  analyzeSybil(walletAddress) {
    return this.request("POST", "/analyze_sybil", {
      wallet_address: walletAddress,
    });
  }

  generateProof(walletAddress) {
    return this.request("POST", "/generate_proof", {
      wallet_address: walletAddress,
    });
  }

  verifyProof(proofId) {
    return this.request("POST", "/verify_proof", {
      proof_id: proofId,
    });
  }

  submitScoreJob(walletAddress) {
    return this.request("POST", "/jobs/score_wallet", {
      wallet_address: walletAddress,
    });
  }

  getJob(jobId) {
    return this.request("GET", `/jobs/${jobId}`);
  }
}
