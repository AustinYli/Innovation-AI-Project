import React, { useMemo, useState } from "https://esm.sh/react@18.3.1";
import { createRoot } from "https://esm.sh/react-dom@18.3.1/client";

const h = React.createElement;

const DEFAULT_WALLET = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e";
const DEFAULT_API_BASE = "http://127.0.0.1:8000";

function compactAddress(value) {
  if (!value || value.length < 16) return value || "None";
  return `${value.slice(0, 8)}...${value.slice(-6)}`;
}

function formatPercent(score) {
  if (typeof score !== "number") return "None";
  return `${Math.round(score * 100)}%`;
}

function formatNumber(value) {
  if (typeof value !== "number") return "0";
  return new Intl.NumberFormat("en-US").format(value);
}

function formatDate(value) {
  if (!value) return "None";
  return new Date(value).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function tierClass(tier) {
  return `tier tier-${String(tier || "unknown").toLowerCase()}`;
}

function DashboardApp() {
  const [apiBaseUrl, setApiBaseUrl] = useState(DEFAULT_API_BASE);
  const [apiKey, setApiKey] = useState("");
  const [walletAddress, setWalletAddress] = useState(DEFAULT_WALLET);
  const [proofId, setProofId] = useState("");
  const [checkResult, setCheckResult] = useState(null);
  const [proofResult, setProofResult] = useState(null);
  const [verifyResult, setVerifyResult] = useState(null);
  const [dashboardSummary, setDashboardSummary] = useState(null);
  const [recentWallets, setRecentWallets] = useState([]);
  const [flaggedWallets, setFlaggedWallets] = useState([]);
  const [rawResult, setRawResult] = useState(null);
  const [activeView, setActiveView] = useState("empty");
  const [loadingAction, setLoadingAction] = useState("");
  const [error, setError] = useState("");

  const latestTrust = useMemo(() => {
    if (activeView === "check") return checkResult;
    if (activeView === "proof") return proofResult;
    if (activeView === "verify") return verifyResult;
    return null;
  }, [activeView, checkResult, proofResult, verifyResult]);
  const healthLabel = useMemo(() => {
    if (!latestTrust) return "Ready";
    if (latestTrust.is_valid === false) return "Review";
    return latestTrust.trust_tier ? `${latestTrust.trust_tier} tier` : "Ready";
  }, [latestTrust]);

  async function callApi(path, payload, actionName, method = "POST") {
    setError("");
    setLoadingAction(actionName);

    try {
      const request = {
        method,
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": apiKey,
        },
      };
      if (method !== "GET") {
        request.body = JSON.stringify(payload);
      }

      const response = await fetch(`${apiBaseUrl}${path}`, request);
      const data = await response.json();
      setRawResult(data);

      if (!response.ok) {
        const message = data.detail || data.message || data.error || "Request failed";
        throw new Error(message);
      }

      return data;
    } catch (requestError) {
      setError(requestError.message);
      return null;
    } finally {
      setLoadingAction("");
    }
  }

  async function loadDashboard() {
    setError("");
    setLoadingAction("dashboard");

    try {
      const headers = {
        "Content-Type": "application/json",
        "X-API-Key": apiKey,
      };
      const [summaryResponse, recentResponse, flaggedResponse] = await Promise.all([
        fetch(`${apiBaseUrl}/dashboard/summary`, { method: "GET", headers }),
        fetch(`${apiBaseUrl}/dashboard/recent_wallets?limit=8`, { method: "GET", headers }),
        fetch(`${apiBaseUrl}/dashboard/flagged_wallets?limit=8`, { method: "GET", headers }),
      ]);

      const [summaryData, recentData, flaggedData] = await Promise.all([
        summaryResponse.json(),
        recentResponse.json(),
        flaggedResponse.json(),
      ]);

      const failedResponse = [summaryResponse, recentResponse, flaggedResponse].find(
        (response) => !response.ok,
      );
      if (failedResponse) {
        const failedData = [summaryData, recentData, flaggedData].find(
          (data) => data.detail || data.message || data.error,
        );
        throw new Error(
          failedData?.detail || failedData?.message || failedData?.error || "Dashboard request failed",
        );
      }

      setDashboardSummary(summaryData);
      setRecentWallets(recentData.wallets || []);
      setFlaggedWallets(flaggedData.wallets || []);
      setRawResult({
        summary: summaryData,
        recent_wallets: recentData,
        flagged_wallets: flaggedData,
      });
      setActiveView("dashboard");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoadingAction("");
    }
  }

  async function checkWallet() {
    const data = await callApi(
      "/check_wallet",
      { wallet_address: walletAddress },
      "check",
    );
    if (data) {
      setCheckResult(data);
      setActiveView("check");
    }
  }

  async function generateProof() {
    const data = await callApi(
      "/generate_proof",
      { wallet_address: walletAddress },
      "proof",
    );
    if (data) {
      setProofResult(data);
      setProofId(data.proof?.proof_id || "");
      setActiveView("proof");
    }
  }

  async function verifyProof() {
    const data = await callApi(
      "/verify_proof",
      { proof_id: proofId },
      "verify",
    );
    if (data) {
      setVerifyResult(data);
      setActiveView("verify");
    }
  }

  return h("div", { className: "shell" },
    h("header", { className: "topbar" },
      h("div", null,
        h("p", { className: "eyebrow" }, "Trust API Dashboard"),
        h("h1", null, "Wallet reputation control panel"),
      ),
      h("div", { className: "statusPill" },
        h("span", { className: "statusDot" }),
        healthLabel,
      ),
    ),

    h("main", { className: "layout" },
      h("section", { className: "panel controlPanel", "aria-label": "Wallet controls" },
        h("div", { className: "sectionHeader" },
          h("h2", null, "Lookup"),
          h("span", null, "Local FastAPI backend"),
        ),
        h("label", null,
          h("span", null, "API base URL"),
          h("input", {
            value: apiBaseUrl,
            onChange: (event) => setApiBaseUrl(event.target.value),
            spellCheck: "false",
          }),
        ),
        h("label", null,
          h("span", null, "X-API-Key"),
          h("input", {
            value: apiKey,
            onChange: (event) => setApiKey(event.target.value),
            placeholder: "Your TRUST_API_KEY",
            type: "password",
          }),
        ),
        h("label", null,
          h("span", null, "Wallet address"),
          h("input", {
            value: walletAddress,
            onChange: (event) => setWalletAddress(event.target.value),
            spellCheck: "false",
          }),
        ),
        h("div", { className: "buttonGrid" },
          h("button", { onClick: checkWallet, disabled: loadingAction !== "" },
            loadingAction === "check" ? "Checking..." : "Check Wallet",
          ),
          h("button", { onClick: generateProof, disabled: loadingAction !== "" },
            loadingAction === "proof" ? "Generating..." : "Generate Proof",
          ),
        ),
        h("label", null,
          h("span", null, "Proof ID"),
          h("input", {
            value: proofId,
            onChange: (event) => setProofId(event.target.value),
            placeholder: "proof_...",
            spellCheck: "false",
          }),
        ),
        h("button", {
          className: "secondaryButton",
          onClick: verifyProof,
          disabled: loadingAction !== "" || !proofId,
        }, loadingAction === "verify" ? "Verifying..." : "Verify Proof"),
        h("button", {
          className: "secondaryButton dashboardButton",
          onClick: loadDashboard,
          disabled: loadingAction !== "",
        }, loadingAction === "dashboard" ? "Loading..." : "Load Dashboard"),
        error && h("div", { className: "errorBox" }, error),
      ),

      h("section", { className: "results" },
        activeView === "empty" && h(EmptyState),
        activeView === "check" && h(CheckWalletResult, { result: checkResult }),
        activeView === "proof" && h(ProofCard, { proofResult }),
        activeView === "verify" && h(VerifyProofResult, { result: verifyResult }),
        activeView === "dashboard" && h(DashboardOverview, {
          summary: dashboardSummary,
          recentWallets,
          flaggedWallets,
        }),
      ),
    ),
  );
}

function MetricCard({ label, value, detail, tier }) {
  return h("article", { className: "metricCard" },
    h("span", { className: "metricLabel" }, label),
    h("strong", { className: tier ? tierClass(tier) : "" }, value),
    h("small", null, detail),
  );
}

function EmptyState() {
  return h("section", { className: "panel emptyPanel" },
    h("p", { className: "eyebrow" }, "Ready"),
    h("h2", null, "Choose an action"),
    h("p", null, "Check a wallet, generate a trust proof, or verify an existing proof ID."),
  );
}

function CheckWalletResult({ result }) {
  if (!result) return h(EmptyState);

  return h("section", { className: "walletResult" },
    h("div", { className: "panel resultHero" },
      h("p", { className: "eyebrow" }, "Wallet checked"),
      h("h2", null, "Wallet checked!"),
      h("p", null, result.summary || "Wallet trust summary is ready."),
    ),
    h("div", { className: "metricGrid" },
      h(MetricCard, {
        label: "Human likelihood",
        value: result.human_likelihood,
        detail: formatPercent(result.confidence_score),
      }),
      h(MetricCard, {
        label: "Trust tier",
        value: result.trust_tier,
        detail: "Current score tier",
        tier: result.trust_tier,
      }),
      h(MetricCard, {
        label: "Confidence",
        value: formatPercent(result.confidence_score),
        detail: `Score ${result.confidence_score}`,
      }),
      h(MetricCard, {
        label: "Wallet ID",
        value: result.wallet_id || "None",
        detail: result.storage_status || "Not stored",
      }),
    ),
    h("section", { className: "panel detailsPanel" },
      h("dl", { className: "proofList" },
        h("div", null,
          h("dt", null, "Wallet"),
          h("dd", null, result.wallet_address),
        ),
        h("div", null,
          h("dt", null, "Normalized"),
          h("dd", null, result.normalized_wallet_address),
        ),
        h("div", null,
          h("dt", null, "Valid Format"),
          h("dd", null, result.is_valid ? "Yes" : "No"),
        ),
        h("div", null,
          h("dt", null, "Risk Flags"),
          h("dd", null, result.risk_flags?.length ? result.risk_flags.join(", ") : "None"),
        ),
      ),
    ),
  );
}

function ProofCard({ proofResult }) {
  const proof = proofResult?.proof;

  return h("section", { className: "panel proofPanel", "aria-label": "Trust proof" },
    h("div", { className: "proofTitleRow" },
      h("div", null,
        h("p", { className: "eyebrow" }, "Your Trust Proof"),
        h("h2", null, proof ? "Proof generated" : "No proof yet"),
      ),
      h("span", { className: tierClass(proofResult?.trust_tier) },
        proofResult?.trust_tier || "No tier",
      ),
    ),
    h("dl", { className: "proofList" },
      h("div", null,
        h("dt", null, "Human Likelihood"),
        h("dd", null, proofResult?.human_likelihood || "Unknown"),
      ),
      h("div", null,
        h("dt", null, "Confidence"),
        h("dd", null, formatPercent(proofResult?.confidence_score)),
      ),
      h("div", null,
        h("dt", null, "Proof ID"),
        h("dd", null, compactAddress(proof?.proof_id)),
      ),
      h("div", null,
        h("dt", null, "Status"),
        h("dd", null, proof?.status || "not generated"),
      ),
      h("div", null,
        h("dt", null, "Issued"),
        h("dd", null, proof?.issued_at || "None"),
      ),
      h("div", null,
        h("dt", null, "Valid Until"),
        h("dd", null, proof?.valid_until || "None"),
      ),
      h("div", null,
        h("dt", null, "Revocable"),
        h("dd", null, proof?.revocable ? "Yes" : "No"),
      ),
    ),
  );
}

function VerifyProofResult({ result }) {
  if (!result) return h(EmptyState);

  const statusText = result.status || "unknown";
  const isActive = result.is_valid && result.status === "active";

  return h("section", { className: "panel verifyPanel" },
    h("div", { className: "proofTitleRow" },
      h("div", null,
        h("p", { className: "eyebrow" }, "Proof verification"),
        h("h2", null, isActive ? "Proof is active" : "Proof is not active"),
      ),
      h("span", { className: `statusBadge status-${statusText}` }, statusText),
    ),
    h("dl", { className: "proofList" },
      h("div", null,
        h("dt", null, "Valid Right Now"),
        h("dd", null, result.is_valid ? "Yes" : "No"),
      ),
      h("div", null,
        h("dt", null, "Proof ID"),
        h("dd", null, compactAddress(result.proof_id)),
      ),
      h("div", null,
        h("dt", null, "Human Likelihood"),
        h("dd", null, result.human_likelihood || "None"),
      ),
      h("div", null,
        h("dt", null, "Trust Tier"),
        h("dd", null, result.trust_tier || "None"),
      ),
      h("div", null,
        h("dt", null, "Valid Until"),
        h("dd", null, result.valid_until || "None"),
      ),
      h("div", null,
        h("dt", null, "Message"),
        h("dd", null, result.message),
      ),
    ),
  );
}

function DashboardOverview({ summary, recentWallets, flaggedWallets }) {
  if (!summary) return h(EmptyState);

  return h("section", { className: "dashboardOverview" },
    h("div", { className: "panel resultHero" },
      h("p", { className: "eyebrow" }, "Week 4 dashboard"),
      h("h2", null, "Database overview loaded"),
      h("p", null, "This view summarizes stored wallet checks, scores, proofs, and review flags from Supabase/Postgres."),
    ),
    h("div", { className: "metricGrid summaryGrid" },
      h(MetricCard, {
        label: "Wallets",
        value: formatNumber(summary.total_wallets),
        detail: summary.database_status,
      }),
      h(MetricCard, {
        label: "Feature Snapshots",
        value: formatNumber(summary.total_feature_snapshots),
        detail: "Stored feature runs",
      }),
      h(MetricCard, {
        label: "Score Snapshots",
        value: formatNumber(summary.total_score_snapshots),
        detail: "Stored scoring runs",
      }),
      h(MetricCard, {
        label: "Proofs",
        value: formatNumber(summary.total_proofs),
        detail: "Generated trust proofs",
      }),
    ),
    h("div", { className: "distributionGrid" },
      h(DistributionPanel, {
        title: "Trust tier distribution",
        rows: summary.tier_distribution,
      }),
      h(DistributionPanel, {
        title: "Human likelihood distribution",
        rows: summary.human_likelihood_distribution,
      }),
      h("section", { className: "panel tablePanel flagSummary" },
        h("p", { className: "eyebrow" }, "Review queue"),
        h("h2", null, formatNumber(summary.flagged_wallet_count)),
        h("p", null, "Wallets whose latest score contains at least one risk flag."),
      ),
    ),
    h(WalletTable, {
      title: "Recent wallets",
      wallets: recentWallets,
      emptyText: "No wallets have been stored yet.",
    }),
    h(WalletTable, {
      title: "Flagged wallets",
      wallets: flaggedWallets,
      emptyText: "No flagged wallets found.",
    }),
  );
}

function DistributionPanel({ title, rows }) {
  const entries = Object.entries(rows || {});
  const total = entries.reduce((sum, [, value]) => sum + value, 0);

  return h("section", { className: "panel tablePanel" },
    h("div", { className: "sectionHeader" },
      h("h2", null, title),
      h("span", null, `${formatNumber(total)} total`),
    ),
    entries.length === 0
      ? h("p", { className: "emptyTableText" }, "No scores available yet.")
      : h("div", { className: "barRows" },
        entries.map(([label, value]) => h("div", { className: "barRow", key: label },
          h("div", { className: "barLabel" },
            h("span", null, label),
            h("strong", null, formatNumber(value)),
          ),
          h("div", { className: "barTrack" },
            h("div", {
              className: "barFill",
              style: { width: `${Math.max(8, Math.round((value / total) * 100))}%` },
            }),
          ),
        )),
      ),
  );
}

function WalletTable({ title, wallets, emptyText }) {
  return h("section", { className: "panel tablePanel" },
    h("div", { className: "sectionHeader" },
      h("h2", null, title),
      h("span", null, `${formatNumber(wallets.length)} shown`),
    ),
    wallets.length === 0
      ? h("p", { className: "emptyTableText" }, emptyText)
      : h("div", { className: "tableScroller" },
        h("table", { className: "walletTable" },
          h("thead", null,
            h("tr", null,
              h("th", null, "Wallet"),
              h("th", null, "Likelihood"),
              h("th", null, "Tier"),
              h("th", null, "Confidence"),
              h("th", null, "Flags"),
              h("th", null, "Stored"),
            ),
          ),
          h("tbody", null,
            wallets.map((wallet) => h("tr", { key: `${title}-${wallet.wallet_id}` },
              h("td", null, compactAddress(wallet.wallet_address)),
              h("td", null, wallet.human_likelihood || "None"),
              h("td", null,
                h("span", { className: tierClass(wallet.trust_tier) },
                  wallet.trust_tier || "None",
                ),
              ),
              h("td", null, formatPercent(wallet.confidence_score)),
              h("td", null,
                wallet.risk_flags?.length
                  ? h("span", { className: "flagList" }, wallet.risk_flags.join(", "))
                  : "None",
              ),
              h("td", null, formatDate(wallet.created_at)),
            )),
          ),
        ),
      ),
  );
}

createRoot(document.getElementById("root")).render(h(DashboardApp));
