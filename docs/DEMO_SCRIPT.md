# 🎬 Demo Script — Market Regime Oracle (2–3 min walkthrough)

Target length: **~2:30**. Tone: confident builder, numbers-forward. Record at 1920×1080.

> Suggested on-screen layout: **terminal left**, **VS Code / file tree right**, **charts popping up
> as they're generated**. Keep the README open in a browser tab for the architecture + results.

---

### 0:00–0:20 — Hook & one-liner *(terminal, already in repo)*

> "This is **Market Regime Oracle** — for the BNB AI Trading hack, Track 2. One question it answers
> really well: *'what kind of BTC market is this, and how much risk should I take?'*
> It fuses **five signals** into **five regimes**, each with a documented trading posture, and then
> **backtests** the whole thing against buy-and-hold."

Type the headline result so it's on screen:

```bash
echo "Strategy −12.7% / maxDD −24%   vs   Buy&Hold −37% / maxDD −51%"
```

### 0:20–0:45 — The architecture *(README in browser)*

Scroll the README to the **🏗️ Architecture** diagram. Narrate the flow, left to right:

> "Two public free sources — CoinGecko for BTC price, alternative.me for Fear & Greed. Five
> independent signal modules each emit a normalized score in minus-one to plus-one. We **fuse**
> them with fixed weights — momentum 0.30, sentiment 0.25, the rest 0.15 each — into one composite,
> then a **priority rule hierarchy** maps each day to exactly one of five regimes."

Point at the priority line: **CAPITULATION > EUPHORIA > RISK_OFF > RISK_ON > RANGE_BOUND**.

### 0:45–1:20 — Live: run the full pipeline *(terminal)*

```bash
python main.py
```

Narrate while it prints:

> "Fetch → classify → backtest → charts, all in one command. No look-ahead — the regime on day *t*
> is decided from data up to day *t*, and earns the *t → t+1* return. Costs are 10 bps per unit of
> turnover."

Read the printed summary aloud: **strategy −12.7% / maxDD −24.2% / Sharpe −0.82**, **buy&hold −37.4%
/ maxDD −51.2%**. Land the punchline:

> "In a year BTC was down thirty-seven percent, staying defensive halved our drawdown."

### 1:20–1:50 — The charts *(open the PNGs from results/)*

Open `results/equity_curve.png` then `results/drawdown.png` then `results/regime_overlay.png`.

> "Equity curve — the blue regime line stays well above grey buy-and-hold. Drawdown — we never went
> below minus twenty-four percent while buy-and-hold lost half. And the **regime overlay** shows the
> classifier shading red CAPITULATION on the acute panic flushes and blue RISK_OFF through the
> downtrend — it's actually reading the market."

### 1:50–2:15 — Tests + MCP skill *(terminal)*

Run the suite:

```bash
PYTHONPATH=src:tests python -m pytest tests/ -q
```

> "Twenty-four tests, all passing — signals, classifier, backtest, fully offline."

Then the MCP round-trip:

```bash
PYTHONPATH=src MRO_HOME=. python tests/_mcp_smoke.py
```

> "And it's packaged as an **MCP server** — the same protocol the CMC Agent Hub uses. This does a
> real `initialize`, `tools/list`, `tools/call` round-trip and returns today's regime plus posture."

### 2:15–2:30 — Wrap-up

> "Five signals, five regimes, one explainable answer — and a backtest that proves it. Public free
> data only, Track 2, no live trading. That's Market Regime Oracle."

*(optional on-screen: `cat results/metrics.json` for the full metric set.)*

---

### 🎬 Cut list / b-roll
- [ ] Typing the headline `echo` line for the thumbnail.
- [ ] The `python main.py` console output scrolling (good cover shot).
- [ ] `24 passed` pytest line — freeze-frame.
- [ ] Equity-curve PNG — strongest visual, use as cover image.
- [ ] Regime-overlay PNG — most "it's actually smart" shot.

### 📝 Speaker notes
- **Lead with the numbers**, not the stack. Judges skim; −37% → −12.7% is the whole pitch.
- If a live API call is risky on the network, `python main.py` runs fully offline from the
  `data_cache/` in your local build dir — say so ("running offline from cache").
- Keep posture table visible during the overlay shot so the colors map to exposures.
