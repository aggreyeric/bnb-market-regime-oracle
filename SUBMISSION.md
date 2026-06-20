# DoraHacks Submission Draft — Market Regime Oracle

> **Hackathon:** BNB AI Trading — https://dorahacks.io/hackathon/bnb-ai-trading
> **Track:** Track 2 — Strategy Skills
> **Prize pool:** $36,000
> **Status:** DRAFT — ⛔ do NOT submit until Eric approves.

Paste the blocks below into the DoraHacks submission form.

---

## 📌 Project Name

**Market Regime Oracle** — a 5-signal → 5-state BTC market-regime classifier

## 🏷️ One-line tagline

Ask *"what kind of market is this, and how much risk should I take?"* — get one explainable regime
plus a documented trading posture, backtested against buy-and-hold.

## 📝 Description

**Market Regime Oracle** is a research/backtest **Strategy Skill** (Track 2) that fuses **five market
signals** into a single composite score, then maps every day to exactly one of **five market regimes** —
`RISK_ON`, `RANGE_BOUND`, `RISK_OFF`, `CAPITULATION`, `EUPHORIA` — each carrying an explicit
**target exposure** and **action**.

**The 5 signals** (each independently unit-tested, normalized to `[-1, +1]`):
1. **RSI / MACD momentum** — CoinGecko price *(real)*
2. **Fear & Greed Index** — alternative.me *(real)*
3. **Volatility regime** — CoinGecko price *(real)*
4. **Funding rate** *(proxy from price)* — clearly labeled, no fabricated data
5. **Exchange flows** *(proxy from signed volume)* — clearly labeled, no fabricated data

**Why it works:** instead of a single buy/sell trigger, the classifier is a **priority-ordered,
deterministic rule hierarchy**. Extreme regimes (`CAPITULATION`, `EUPHORIA`) override the trend
regimes, so the model de-risks fast in panics and takes profit into blow-offs — while staying fully
long in clear uptrends.

**Backtested on real BTC data (~1 year):**

| Metric | Regime Strategy | Buy & Hold |
|---|:---:|:---:|
| Total return | **−12.7%** | −37.4% |
| Max drawdown | **−24.2%** | −51.2% |
| Volatility | **19.3%** | 43.1% |
| Final equity ($10k) | **$8,733** | $6,264 |

In a year BTC was down ~37%, the regime strategy **halved the drawdown and more than halved
volatility**, outperforming buy-and-hold by ~25 points — by simply taking less risk in `RISK_OFF` /
`CAPITULATION`. Decision model is strictly **no look-ahead** (regime at day *t* from data up to *t*;
position earns the *t → t+1* return; 10 bps turnover cost).

**Packaged as an MCP server** (the same protocol the CMC Agent Hub uses to route prompts to cloud
Skills). Any MCP-compatible client — Claude Desktop, Cursor, the CMC Agent Hub — can call the
`get_market_regime` tool and receive a structured regime + posture read plus full backtest context.
The CMC MCP already exposes the raw primitives this skill fuses; **this skill is the fusion +
posture layer on top**.

---

## 🏗️ Architecture (how a regime is decided)

A deterministic, **no-look-ahead** pipeline — every signal, weight, and rule is auditable:

```
 CoinGecko (BTC OHLCV)        alternative.me (Fear & Greed)
        │                              │
        ▼                              ▼
   data/loader.py  →  aligned daily feature frame
        ▼
 ┌──────────────────────────────────────────────┐
 │  5 independent signal modules → [-1, +1]     │
 │  momentum 0.30 · fear_greed 0.25 · vol 0.15  │   +1 = risk-on
 │  funding-proxy 0.15 · flow-proxy 0.15        │   -1 = risk-off
 └──────────────────┬───────────────────────────┘
                    ▼ weighted fusion → composite score
                    ▼ priority rule hierarchy (deterministic)
 ┌──────────────────────────────────────────────┐
 │  5-state classifier                          │   CAPITULATION > EUPHORIA >
 │  (extreme regimes override trend regimes)    │   RISK_OFF > RISK_ON >
 │                                              │   RANGE_BOUND (default)
 └──────────────────┬───────────────────────────┘
                    ▼ regime → posture map
            target exposure + action
        ┌─────────────┴──────────────┐
        ▼                            ▼
  vectorized backtest        MCP tool: get_market_regime
  (no look-ahead, w/ costs)  (stdio → CMC Agent Hub skill)
```

**Why deterministic over ML:** an explainable, frozen rule hierarchy is what a risk-averse AI agent
should call to *size* risk — no retraining drift, no black box, every decision reproducible. The
fusion layer is feed-agnostic, so a real funding/on-chain feed can drop in as a new `Signal`
subclass without touching the classifier or backtest.

---

## 🛠️ Tech Stack

- **Python 3.11+**, `pandas` / `numpy` for the vectorized, no-look-ahead backtest engine
- **matplotlib** (headless `Agg`) for equity/drawdown/regime-overlay charts
- **CoinGecko** + **alternative.me** public free APIs (no keys, no paid data)
- **MCP** (`mcp` SDK, FastMCP) over stdio — CMC Agent Hub skill packaging
- **pytest** — 24/24 tests (signals, classifier, backtest, MCP round-trip), fully offline
- **Docker / docker compose** — one-command reproducible run

## 🤖 AI / Agent angle

A regime classifier is the natural **risk-budgeting brain** for an AI trading agent: rather than an
LLM guessing position size, the agent calls one deterministic, explainable, backtested tool
(`get_market_regime`) to decide *how much* risk to take, then layers its own alpha on top. The skill
is composable with other CMC Agent Hub skills — it's a **gate/sizing layer**, not a black-box model.

## 👀 What judges should look at

1. **The result.** `results/metrics.json` + the **equity-curve & drawdown charts** in `results/` —
   strategy −12.7% / maxDD −24% vs buy-and-hold −37% / maxDD −51% on real BTC.
2. **The architecture** (README 🏗️ diagram): 5 independent signals → weighted fusion → composite →
   priority rule hierarchy → 5 regimes → posture. Clean, explainable, deterministic.
3. **No look-ahead backtest.** `src/market_regime_oracle/backtest/engine.py` — strict causal
   decision model with transaction costs.
4. **The MCP skill.** `src/market_regime_oracle/mcp_server.py` + `packaging/cmc-skill/` — run
   `PYTHONPATH=src MRO_HOME=. python tests/_mcp_smoke.py` to see a real `initialize` → `tools/list`
   → `tools/call` round-trip returning today's regime + posture.
5. **Honesty/transparency.** The two proxy signals are clearly labeled (not fabricated "real" data),
   and it's strictly Track 2 (no live trading / wallet / token launch).
6. **Test coverage.** `PYTHONPATH=src:tests python -m pytest tests/` → **24 passed**, offline.

## ▶️ How to run / reproduce

```bash
pip install -r requirements.txt
python main.py                     # reproduces all results/ artifacts (offline via cache)
PYTHONPATH=src:tests python -m pytest tests/     # 24/24 pass
./scripts/demo.sh                  # ⭐ LIVE DEMO — MCP round-trip over stdio (offline)
```

**Best way to judge the skill in 30 seconds:** run `./scripts/demo.sh`. It launches the MCP
server and performs a real JSON-RPC handshake → `tools/list` → `tools/call` round trip
(`list_regimes` + `get_market_regime`), pretty-printing today's regime, the per-signal scores,
and the backtest-vs-buy-&-hold summary — exactly the call an MCP client (Claude Desktop, Cursor,
the CMC Agent Hub) makes. Fully offline using the shipped `data_cache/`.

Or one command with Docker: `docker compose up --build run` (or `docker compose run --rm tests`
for the 24/24 suite).

## 🔗 Links

- **Repo:** _(Eric: paste the GitHub URL after push)_
- **Docker:** `docker compose up --build run`
- **Demo video:** _(Eric: link after recording — see `docs/DEMO_SCRIPT.md`)_

## ⚖️ Compliance / hard rules

- ✅ Track 2 only — research / backtest, no live trading, no wallet, no token launch.
- ✅ Only public/free authorized sources (CoinGecko, alternative.me); proxies clearly labeled.
- ✅ Not financial advice.

---

**⛔ APPROVAL GATE:** This is a draft. Eric must approve wording + repo link + demo video before
anything is submitted to DoraHacks.
