# DoraHacks Submission Form Fields — Market Regime Oracle

> Copy-paste-ready text for each field of the BNB AI Trading Hackathon submission form.
> **Status: SUBMITTED ✅ — submitted without video. Recorded here for completeness, so all 5 projects have form fields on file.**

---

## 1. Project Name

```
Market Regime Oracle
```

---

## 2. One-line tagline (max 255 chars)

```
A 5-signal → 5-state BTC market-regime classifier that fuses momentum, sentiment, volatility, funding and flow into one explainable regime with a documented risk posture — shipped as an MCP Strategy Skill for the CMC Agent Hub.
```

*(~225 chars)*

---

## 3. Description (≈660 words)

```
Ask any trader the hardest question in crypto: "What kind of market is this, and how much risk should I take right now?" The Market Regime Oracle answers it — not with a single indicator, but by fusing five independent signals into one explainable, five-state regime, each mapped to a documented risk posture. It is shipped as an MCP Strategy Skill for the CoinMarketCap Agent Hub (BNB AI Trading — Track 2), so any MCP-compatible client — Claude Desktop, Cursor, the CMC Agent Hub — can call `get_market_regime` and receive a deterministic, no-look-ahead risk posture in a single round-trip.

THE PROBLEM
Crypto traders drown in indicators. RSI says one thing, funding says another, sentiment is screaming, and volatility is doing its own dance. There is no single, explainable answer to "what regime am I in?" — and more dangerously, no mapping from that answer to "what should my exposure be?" Most tools either throw raw indicators at you (you decide) or hide everything behind a black-box score (you trust). We wanted neither.

THE SOLUTION
The Market Regime Oracle classifies every day into exactly one of five regimes, each with a target exposure and a posture:

- 🟢 RISK_ON — 100% exposure. Uptrend; full position.
- 🟡 RANGE_BOUND — 40%. Sideways; light exposure.
- 🔵 RISK_OFF — 20%. Downtrend; defensive.
- 🔴 CAPITULATION — 10%. Panic; maximum defensive.
- 🟣 EUPHORIA — 30%. Blow-off; take profit.

To get there, five independent signals each produce a normalized bullishness score in [-1, +1]: RSI/MACD momentum (weight 0.30), the Fear & Greed Index from alternative.me (0.25), a volatility-regime signal (0.15), a funding-rate proxy reconstructed from price (0.15), and an exchange-flow proxy reconstructed from volume (0.15). These fuse into a weighted composite, which then passes through priority rules that enforce the asymmetry traders actually feel — CAPITULATION dominates EUPHORIA, which both dominate a plain RISK_OFF, and so on. The classifier is deterministic and has zero look-ahead: today's regime uses only today's and prior data.

THE RESULT
In a down year for BTC (−37.4%), the regime strategy returned −12.7%. It halved the drawdown (−24.2% vs −51.2%) and halved the volatility (19.3% vs 43.1%), outperforming buy-and-hold by roughly 25 points while still going long during genuine uptrends. Sharpe moved from −0.97 to −0.82 and Sortino from −1.32 to −1.01. The backtest is vectorized, costed at 10 bps/turnover, and produces equity-curve, drawdown, regime-overlay and distribution charts out of the box.

WHAT MAKES IT UNIQUE
Three things. First, it is explainable by construction — every regime decision decomposes back into five weighted signals, so a judge or a trader can ask "why RISK_OFF today?" and get a real answer, not a mystery score. Second, it is an MCP-native Strategy Skill, not a notebook: it runs as a stdio MCP server exposing `get_market_regime`, so it plugs directly into the CoinMarketCap Agent Hub and any MCP client. Third, it is honest about its data — funding rates and exchange flows have no free public feed, so we reconstruct them from price and volume as clearly-labeled proxies, and the fusion layer is signal-agnostic: drop in real feeds anytime and the regime improves without a code change.

THE BUILD
Pure Python 3.11, organized into data loaders (CoinGecko + alternative.me), five unit-tested signal modules, the fusion + regime classifier, a vectorized no-look-ahead backtest, a viz layer, and the MCP server. It ships 24/24 passing tests — all offline and deterministic, no network needed — plus `docker compose up` for the full pipeline or the MCP server. No API keys are required; both data sources are public and free. A `scripts/demo.sh` drives a 30-second live MCP round-trip for judges.

The Market Regime Oracle turns five noisy indicators into one decision you can actually act on.
```

*(~655 words — within the 500–800 target)*

---

## 4. Demo video URL

```
Submitted without video.
```

> This project was submitted to the BNB AI Trading Hackathon without a demo video recording. The README's visual results section (equity curve, drawdown, regime overlay, regime summary) plus `scripts/demo.sh` (30-second live MCP round-trip) serve as the in-repo demo artifacts.

---

## 5. GitHub repo URL

```
https://github.com/aggreyeric/bnb-market-regime-oracle
```

---

## 6. Category / Track selection

**Track: `Strategy Skills`** (BNB AI Trading — Track 2)

```
Strategy Skills
```

**Why Strategy Skills:**

| Track | Fit? | Reasoning |
|---|---|---|
| **Strategy Skills** | ✅ **Exact fit** | The project is built explicitly as an MCP Strategy Skill for the CoinMarketCap Agent Hub. It exposes `get_market_regime` over MCP stdio — a callable, composable strategy tool that any MCP client (CMC Agent Hub, Claude Desktop, Cursor) invokes to get a risk posture. Five fused signals → five states → one actionable exposure decision. This is the textbook definition of a Strategy Skill. |
| Trading Agents | ❌ | The oracle is a regime/posture classifier and decision input, not an autonomous agent that places trades or manages a portfolio end-to-end. |
| Alpha / Signal | ❌ | While it produces signals, it is packaged as a reusable MCP skill with posture mapping and backtest, not a raw signal feed. Strategy Skills is the better home. |

---

## ✅ Submission status

- [x] **SUBMITTED ✅** to the BNB AI Trading Hackathon (deadline Jun 21, 2026)
- [x] Submitted **without** a demo video (README charts + `scripts/demo.sh` serve as in-repo demo)
- [x] GitHub repo public: https://github.com/aggreyeric/bnb-market-regime-oracle
- [x] Track: Strategy Skills (BNB AI Trading — Track 2)
- [x] No further action required — this file exists only to complete the set of 5 projects' form fields

---

_Prepared by hack_3. For record-keeping only — already submitted. Not submitted again anywhere._
