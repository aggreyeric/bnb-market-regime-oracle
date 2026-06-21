# 🎬 Market Regime Oracle — Demo Video Script (3 min)

> **Title:** Market Regime Oracle — 5 Signals → 5 Regimes → One Risk Posture
> **Hackathon:** BNB AI Trading (Track 2 — Strategy Skills)
> **Runtime:** ~3:00 (180s)
> **Format:** Screen-capture + voiceover (Eric presenting). One terminal window,
> the README's result charts shown full-screen, plus brief code-viewer cuts to the
> signal modules and the MCP server.
>
> **Recording tip:** the whole demo runs **offline-first** — no API keys, no
> network required for the classifier/backtest. Prereq:
> ```bash
> cd bnb-market-regime-oracle && pip install -r requirements.txt
> PYTHONPATH=src python -m pytest tests/        # warm the cache, confirm green
> python main.py                                # pre-generate results/*.png
> ```
> Pre-run `main.py` once so the charts in `results/` are freshly rendered and the
> on-camera `demo.sh` is snappy. Both data sources (CoinGecko + alternative.me)
> are public/free — no secrets on screen.

---

## SEGMENT 1 — Intro: "What kind of market is this?" (0:00 – 0:30)

**On screen:** Title card →

> **Market Regime Oracle**
> *Five signals → five regimes → one explainable risk posture.*

Then the architecture diagram from the README (data loaders → 5 signal modules →
fusion → 5-state classifier → backtest + MCP tool).

**Eric (voiceover):**
> "Ask any trader the hardest question in crypto: *what kind of market is this,
> and how much risk should I take right now?* RSI says one thing, funding says
> another, sentiment is screaming. There's no single explainable answer — and worse,
> no map from that answer to an actual exposure. **Market Regime Oracle** fixes both.
> It fuses five independent signals into one of five regimes, each with a documented
> risk posture — and ships as an MCP Strategy Skill so any agent can call it."

**Cut to:** terminal, prompt ready in `bnb-market-regime-oracle/`.

---

## SEGMENT 2 — Run the demo: a live MCP round-trip (0:30 – 1:10)

**On screen:** Run the 30-second live demo:

```bash
./scripts/demo.sh
```

**What appears, step by step** (the core ~40 seconds — let each step land):

### Step 1 — MCP server starts (stdio)
Console prints the MCP handshake — the server advertising the `get_market_regime`
tool over stdio.

**Eric:**
> "This is a real MCP server, stdio transport — the same protocol the CoinMarketCap
> Agent Hub speaks. No HTTP, no API key. Any MCP client — Claude Desktop, Cursor,
> the CMC Agent Hub — can mount it as a skill."

### Step 2 — A client calls `get_market_regime`
The demo client sends a `tools/call` for `get_market_regime`. The server fetches
today's BTC data, runs all five signals, fuses, classifies.

**Eric:**
> "One call: `get_market_regime`. Behind it, the oracle pulls today's BTC data,
> runs all five signals, fuses them, and classifies — deterministically, zero
> look-ahead."

### Step 3 — The response: regime + posture
Console prints a JSON-like payload — e.g.:

```
regime:        RISK_OFF
exposure:      20%
posture:       Downtrend — defensive
composite:     -0.41
signals:       momentum -0.62  fear_greed -0.30  vol +0.10  funding -0.55  flows -0.20
```

**Eric:**
> "The answer: today is `RISK_OFF`, 20% exposure, defensive. But notice what comes
> back with it — the composite score **and every signal's contribution**. That's
> the explainability: a trader, or a judge, can ask *why RISK_OFF today?* and get a
> real answer, not a mystery score."

---

## SEGMENT 3 — The 5 signals, briefly (1:10 – 1:50)

**On screen:** Cut to a code viewer. Open the signals package:

```bash
ls src/market_regime_oracle/signals/
```

Then show one flagship signal module, e.g.:

```bash
cat src/market_regime_oracle/signals/momentum.py
```

*(Show ~15 lines — RSI/MACD computed, normalized to a `[-1, +1]` score.)*

**Eric:**
> "Five signals, each independently unit-tested, each outputting a normalized
> bullishness score from minus one to plus one. **Momentum** — RSI and MACD off
> CoinGecko price, weighted thirty percent. **Fear & Greed** from alternative.me,
> twenty-five percent — the only sentiment feed we trust enough to weight that
> high. Then **volatility regime**, a **funding-rate proxy**, and an
> **exchange-flow proxy** — fifteen percent each."

*(On-screen lower-third: the weights table from the README.)*

**Eric (continue):**
> "Here's the honest part: funding rates and exchange flows have no free public
> feed. So we reconstruct them from price and volume as **clearly-labeled proxies**.
> The fusion layer is signal-agnostic — drop in a real funding feed tomorrow and
> the regime improves without a code change."

---

## SEGMENT 4 — The 5 regimes & the backtest (1:50 – 2:35)

**On screen:** Full-screen the four result charts in sequence —
`results/equity_curve.png`, `results/drawdown.png`, `results/regime_overlay.png`,
`results/regime_summary.png`. Linger ~5s each.

**Eric:**
> "Five regimes, five postures. `RISK_ON` — full exposure, uptrend.
> `RANGE_BOUND` — forty percent, sideways. `RISK_OFF` — twenty, defensive.
> `CAPITULATION` — ten, max defensive. `EUPHORIA` — thirty, take profit. Priority
> rules enforce the asymmetry traders actually feel: capitulation dominates
> euphoria, which dominates a plain risk-off."

*(Cut to the equity curve.)*

**Eric:**
> "The backtest is vectorized, costed at ten basis points per turnover, zero
> look-ahead. Headline: in a down year for BTC — **minus thirty-seven percent** —
> the regime strategy did **minus twelve point seven**. It halved the drawdown
> — twenty-four percent vs fifty-one — and halved volatility — nineteen vs
> forty-three. Outperformed buy-and-hold by about twenty-five points, **while still
> going long during genuine uptrends.** This isn't just going to cash — it's
> posture-aware."

---

## SEGMENT 5 — MCP integration & closing (2:35 – 3:00)

**On screen:** Cut to the MCP server source, briefly:

```bash
cat src/market_regime_oracle/mcp_server.py
```

*(Highlight the `@mcp.tool()` decorator on `get_market_regime` and the stdio
entrypoint — ~10 lines.)*

**Eric:**
> "This is the whole integration story. One file, one tool, stdio transport. Mount
> it in the CoinMarketCap Agent Hub, or any MCP client, and your agent gets a
> deterministic, no-look-ahead risk posture in a single round-trip. Twenty-four of
> twenty-four tests pass, all offline. `docker compose up` runs the full pipeline
> or the server."

**On screen:** End card →

> **Market Regime Oracle**
> 5 signals → 5 regimes → one explainable risk posture
> MCP Strategy Skill for the CMC Agent Hub · BNB AI Trading — Track 2
> −12.7% vs −37.4% in a down year · MIT

**Eric (closing):**
> "Market Regime Oracle — five noisy indicators, one decision you can actually act
> on. Explainable by construction, MCP-native by design, honest about its data."

**End card:** repo URL · `./scripts/demo.sh` · `PYTHONPATH=src python -m pytest tests/`

---

## 🎬 Shot list / recording checklist

| # | Segment | Window | Command / action | Duration |
|---|---------|--------|------------------|----------|
| 1 | Intro | — | Title card + architecture diagram | 30s |
| 2 | Live MCP demo | Terminal | `./scripts/demo.sh` (server start → `get_market_regime` → JSON regime/posture) | 40s |
| 3 | The 5 signals | Code viewer | `ls signals/` + `cat signals/momentum.py` (+ weights lower-third) | 40s |
| 4 | Regimes + backtest | Image viewer | `results/equity_curve.png`, `drawdown.png`, `regime_overlay.png`, `regime_summary.png` | 45s |
| 5 | MCP integration + close | Code viewer → end card | `cat mcp_server.py` (highlight `@mcp.tool`) → end card | 25s |

**If you need to save 20s:** in Segment 3 show only `momentum.py` (skip `ls`),
and in Segment 4 show only the equity curve + regime overlay (drop drawdown &
summary). Story stays intact.

**If you have 30s more:** in Segment 2, after the clean call, show a second
`get_market_regime` call where you **flip the data** to a euphoric/capitulation
day so the regime visibly changes — strongest visual proof the classifier reacts.

**Captions / lower-thirds to prepare:**
- "5 signals → 5 regimes → 1 risk posture"
- "MCP stdio · mounts in CMC Agent Hub, Claude Desktop, Cursor"
- "Deterministic · zero look-ahead · costed at 10 bps/turnover"
- "−12.7% vs −37.4% · drawdown halved · volatility halved"
- "24/24 tests passing · offline · no API keys"
- "MIT · BNB AI Trading — Track 2 (Strategy Skills)"

**Quiet on set notes:**
- Speak the numbers deliberately — "minus twelve point seven" lands better than
  racing through "negative twelve point seven percent."
- On the equity-curve shot, gesture (or arrow) to the gap between the two lines
  in the drawdown trough — that's the visual punchline.
- If recording live data, run `demo.sh` once off-camera first to warm any cache;
  the on-camera take should be the second run for snappiness.
