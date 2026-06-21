# Architecture — Market Regime Oracle

> Scope note: this document reflects the **actual implementation** in `src/`. The
> task brief referenced on-chain DEX data, a voting ensemble, a 4-state
> Bull/Bear/Sideways/Risk-Off output, and a BSC smart-contract integration —
> **none of those exist in the codebase.** The diagram below documents what is
> really shipped. See [§ Reconciliation](#-reconciliation-task-brief-vs-actual) for
> the itemized diff.

---

## System Overview

```mermaid
flowchart TD
    %% ---------- Data sources ----------
    CG["CoinGecko API<br/>BTC daily OHLCV<br/>(close, volume) — no key"]
    AM["alternative.me API<br/>Fear &amp; Greed Index — no key"]

    CG --> LOAD["data/loader.py<br/>aligned daily features"]
    AM --> LOAD

    %% ---------- Cache ----------
    CACHE[("data_cache/<br/>parquet + json")]
    LOAD <--> CACHE

    %% ---------- 5 signal generators ----------
    LOAD --> S1["momentum.py<br/>RSI + MACD<br/>weight 0.30"]
    LOAD --> S2["fear_greed.py<br/>sentiment map<br/>weight 0.25"]
    LOAD --> S3["volatility.py<br/>realized-vol regime<br/>weight 0.15"]
    LOAD --> S4["funding.py<br/>funding-rate PROXY<br/>(price-derived) 0.15"]
    LOAD --> S5["exchange_flows.py<br/>flow PROXY<br/>(volume-derived) 0.15"]

    %% ---------- scores ----------
    S1 --> SC["score in [-1, +1]<br/>per signal"]
    S2 --> SC
    S3 --> SC
    S4 --> SC
    S5 --> SC

    %% ---------- Fusion + classifier ----------
    SC --> FUSE["classifier/fusion.py<br/>WEIGHTED fusion → composite<br/>(not a voting ensemble)"]
    FUSE --> RULES["priority-ordered rule hierarchy<br/>deterministic, no look-ahead<br/>CAPITULATION &gt; EUPHORIA &gt;<br/>RISK_OFF &gt; RISK_ON &gt; RANGE_BOUND"]
    RULES --> REGIME["5-state regime label per day"]

    %% ---------- Outputs ----------
    REGIME --> POSTURE["config.POSTURES<br/>target_exposure + action"]
    POSTURE --> O1["🟢 RISK_ON 100%"]
    POSTURE --> O2["🟡 RANGE_BOUND 40%"]
    POSTURE --> O3["🔵 RISK_OFF 20%"]
    POSTURE --> O4["🔴 CAPITULATION 10%"]
    POSTURE --> O5["🟣 EUPHORIA 30%"]

    %% ---------- Integration: MCP + backtest ----------
    REGIME --> MCP["mcp_server.py — FastMCP / stdio<br/>tool: get_market_regime<br/>CMC Agent Hub Skill"]
    MCP --> CLIENT["MCP clients<br/>Claude Desktop · Cursor ·<br/>CMC Agent Hub"]
    REGIME --> BT["backtest/engine.py<br/>vectorized, w/ costs<br/>vs buy &amp; hold"]
    BT --> VIZ["viz/charts.py<br/>equity · drawdown ·<br/>regime overlay · summary"]
    BT --> RESULTS[("results/<br/>CSVs · metrics.json · PNG")]
    VIZ --> RESULTS

    %% ---------- styling ----------
    classDef src   fill:#e8f4fd,stroke:#2b7cd6,stroke-width:1px,color:#0b3d66;
    classDef sig   fill:#fff4e6,stroke:#e8932b,stroke-width:1px,color:#663d00;
    classDef cls   fill:#eef9f0,stroke:#2e9e4f,stroke-width:1px,color:#0e4a1e;
    classDef out   fill:#fdecea,stroke:#d23b3b,stroke-width:1px,color:#5c1212;
    classDef ext   fill:#f1ecfb,stroke:#7b3fb5,stroke-width:1px,color:#2e1450;

    class CG,AM,LOAD,CACHE src;
    class S1,S2,S3,S4,S5,SC sig;
    class FUSE,RULES,REGIME,POSTURE cls;
    class O1,O2,O3,O4,O5 out;
    class MCP,CLIENT,BT,VIZ,RESULTS ext;
```

---

## The 5 Signals

| # | Module | Signal | Source | Weight |
|---|---|---|---|:---:|
| 1 | `signals/momentum.py` | RSI + MACD momentum | CoinGecko price | **0.30** |
| 2 | `signals/fear_greed.py` | Fear & Greed Index | alternative.me | **0.25** |
| 3 | `signals/volatility.py` | Realized-vol regime | CoinGecko price | 0.15 |
| 4 | `signals/funding.py` | Funding-rate **proxy** (price-derived) | derived | 0.15 |
| 5 | `signals/exchange_flows.py` | Exchange-flow **proxy** (volume-derived) | derived | 0.15 |

Each signal normalizes to a bullishness score in `[-1, +1]`. Signals 4 and 5 are
clearly labeled **proxies** — there is no free public funding/flow feed, so they
are reconstructed from price/volume. The fusion layer is signal-agnostic, so real
feeds can be dropped in without touching the classifier.

---

## Classifier: Fusion + Priority Rules (not voting)

```
composite = Σ(weight_i × score_i)
```

The composite is then mapped to **exactly one** regime via a deterministic,
priority-ordered rule hierarchy (no look-ahead, no randomness):

1. **CAPITULATION** — highest priority (extreme fear + crash)
2. **EUPHORIA** — extreme greed + blow-off
3. **RISK_OFF** — composite strongly negative
4. **RISK_ON** — composite strongly positive
5. **RANGE_BOUND** — default (neutral / sideways)

---

## 5 Regimes → Posture Map

| Regime | Target Exposure | Posture |
|---|:---:|---|
| 🟢 `RISK_ON` | 100% | Uptrend / accumulation — full exposure |
| 🟡 `RANGE_BOUND` | 40% | Sideways — light exposure, hold core |
| 🔵 `RISK_OFF` | 20% | Downtrend / defensive — raise cash to 80% |
| 🔴 `CAPITULATION` | 10% | Panic / max defensive — near-full cash |
| 🟣 `EUPHORIA` | 30% | Blow-off top — take profit, fade strength |

---

## Integration Surface

- **MCP Strategy Skill** — `mcp_server.py` exposes `get_market_regime` over stdio
  via FastMCP. Any MCP client (Claude Desktop, Cursor, the CoinMarketCap Agent
  Hub) gets a deterministic regime + posture snapshot for the latest day.
- **Vectorized backtest** — `backtest/engine.py` replays the regime labels with
  realistic costs (10 bps/turnover) against buy-and-hold.
- **Visualization** — `viz/charts.py` emits equity curve, drawdown, regime
  overlay, and regime-summary PNGs to `results/`.

---

## 🔁 Reconciliation: Task Brief vs. Actual

| Task brief said | Actual implementation |
|---|---|
| Data source: on-chain DEX data | ❌ Not present. Only CoinGecko + alternative.me |
| Signal: `volume` (standalone) | ⚠️ Replaced by `volatility` + volume-derived `exchange_flows` proxy |
| Signal: `on-chain flow` | ⚠️ `exchange_flows` is a volume-derived **proxy**, not on-chain |
| Classifier: ensemble **voting** | ❌ Weighted **fusion** + deterministic priority rules |
| Output: Bull / Bear / Sideways / Risk-Off (4) | ❌ 5 states: RISK_ON / RANGE_BOUND / RISK_OFF / CAPITULATION / EUPHORIA |
| Integration: BSC smart contract | ❌ **Not implemented.** MCP stdio + backtest only — no on-chain contract, no auto-execution |
| Integration: automated trading signals | ⚠️ Regime + posture is *advisory* (target exposure); no order execution layer |

If the on-chain/BSC piece is required for submission, it is a **new build**,
not documentation of existing code.
