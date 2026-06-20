# 🎬 DEMO VIDEO SCRIPT — Market Regime Oracle (3:00)

**Hackathon:** BNB AI Trading — Track 2 (Strategy Skills)
**Target length:** exactly 3 minutes (180 s)
**Format:** screen recording, 1920×1080, narration voiceover
**Tone:** confident builder, **numbers-forward** — judges skim, so the −37% → −12.7% result is the hook.

> **Layout during recording:** terminal on the **left**, VS Code / file tree on the **right**,
> charts from `results/` opened full-screen as b-roll. Keep the README open in a browser tab.

All narration below matches **real, verified** output (tests 24/24 pass; `scripts/demo.sh` ran
clean offline; backtest numbers from `results/metrics.json`). Read the **🗣 NARRATION** lines aloud;
the **🖥 ON SCREEN** lines are what you type/show.

---

## 0:00 – 0:20 · Hook & headline result  *(terminal, already in repo)*

🖥 **ON SCREEN** — repo already open, type the headline so it lands on screen:
```bash
echo "Strategy −12.7% / maxDD −24%   vs   Buy&Hold −37% / maxDD −51%"
```

🗣 **NARRATION**
> "This is **Market Regime Oracle**, built for the BNB AI Trading hack, Track 2. It answers the one
> question every trader actually asks — *'what kind of BTC market is this, and how much risk should
> I take?'* In a year BTC fell thirty-seven percent, this classifier **halved the drawdown** — minus
> twenty-four versus buy-and-hold's minus fifty-one. Here's how it works."

---

## 0:20 – 0:50 · The architecture  *(README open in browser, 🏗️ diagram)*

🖥 **ON SCREEN** — scroll the README to the **🏗️ Architecture** diagram; point at the priority line.

🗣 **NARRATION**
> "Two public, free sources — CoinGecko for BTC price, alternative.me for Fear & Greed — feed
> **five independent signal modules**. Each emits a normalized score from minus-one to plus-one.
> We **fuse** them with fixed weights — momentum thirty percent, sentiment twenty-five, the rest
> fifteen each — into one composite score. Then a **deterministic, no-look-ahead priority rule
> hierarchy** maps every day to exactly one of five regimes." *(point at the priority line)*
> "Capitulation outranks euphoria, which outranks risk-off, risk-on — and everything else defaults
> to range-bound. Extreme regimes override trends, so it de-risks fast in panics."

---

## 0:50 – 1:30 · Live: run the full pipeline  *(terminal)*

🖥 **ON SCREEN** — run the one-command pipeline:
```bash
python main.py
```

🗣 **NARRATION** *(read the printed summary as it appears)*
> "Fetch, classify, backtest, charts — one command. **Strictly no look-ahead**: the regime on day T
> is decided from data up to day T, and earns the T-to-T-plus-one return, with ten basis points of
> turnover cost."
>
> "Strategy total return **minus twelve-point-seven percent**, max drawdown **minus twenty-four**,
> volatility nineteen percent — versus buy-and-hold **minus thirty-seven percent**, drawdown
> **minus fifty-one**, volatility forty-three. **Halved the drawdown, more than halved the
> volatility — by simply taking less risk when the market said risk-off.**"

---

## 1:30 – 2:10 · The charts  *(open PNGs from results/)*

🖥 **ON SCREEN** — open, in order:
1. `results/equity_curve.png`
2. `results/drawdown.png`
3. `results/regime_overlay.png`

🗣 **NARRATION**
> *(equity curve)* "Equity curve — the regime line stays well above grey buy-and-hold the whole way
> down."
> *(drawdown)* "Drawdown — we never broke minus twenty-four percent. Buy-and-hold lost **half**."
> *(regime overlay)* "And this is the proof it's actually reading the market: the overlay shades
> **red capitulation** on the acute panic flushes and **blue risk-off** through the sustained
> downtrend — each color maps to a documented target exposure, from ten percent in capitulation to
> one hundred in risk-on."

---

## 2:10 – 2:45 · Live MCP skill  *(terminal — the ⭐ demo)*

🖥 **ON SCREEN** — run the packaged MCP skill round-trip:
```bash
./scripts/demo.sh
```

🗣 **NARRATION** *(as the sections print)*
> "And it's not a notebook — it's packaged as an **MCP server**, the same protocol the CMC Agent Hub
> uses to route prompts to skills. This launches the server and does a real **JSON-RPC handshake**,
> **lists the tools**, then **calls** `get_market_regime`."
>
> *(when the regime box prints)* "Right now, as of June seventeenth — regime **range-bound**, BTC
> at sixty-five-five-nine-eight, target exposure **forty percent**. It shows the composite score and
> every per-signal contribution, plus the backtest summary. This is the exact call Claude Desktop,
> Cursor, or the CMC Agent Hub would make to **size risk before entering a position**."

---

## 2:45 – 2:55 · Tests  *(terminal)*

🖥 **ON SCREEN** — run the suite:
```bash
PYTHONPATH=src:tests python -m pytest tests/ -q
```

🗣 **NARRATION**
> "Twenty-four tests — signals, classifier, backtest, and the MCP round-trip — **all passing,
> fully offline.**"

---

## 2:55 – 3:00 · Wrap-up  *(equity curve PNG as backdrop)*

🖥 **ON SCREEN** — freeze on `results/equity_curve.png`.

🗣 **NARRATION**
> "Five signals, five regimes, one explainable answer — and a backtest that proves it. Public free
> data only, Track 2, no live trading. That's **Market Regime Oracle**."

---

## 🎬 Cut list / b-roll (record these as separate clips)
- [ ] Typing the headline `echo` line → **thumbnail candidate**.
- [ ] `python main.py` console scrolling — good cover shot.
- [ ] `24 passed` pytest line — **freeze-frame**.
- [ ] `equity_curve.png` — strongest visual, **use as cover image**.
- [ ] `regime_overlay.png` — the most "it's actually smart" shot (red/blue shading).
- [ ] The `get_market_regime` regime box from `scripts/demo.sh` (🎯 RANGE_BOUND, exposure 0.4).

## 📝 Speaker notes
- **Lead with numbers, not the stack.** −37% → −12.7% / maxDD −51% → −24% is the whole pitch.
- Every run here works **fully offline** from the shipped `data_cache/`. If the recording
  environment is shaky, say *"running offline from cache"* — no live API risk on camera.
- Keep the **posture table** (`results/posture_mapping.csv`) visible during the overlay shot so the
  overlay colors map to target exposures for the viewer.
- Pace the three chart beats to ~13 s each; don't rush the drawdown comparison — it's the payoff.
- Total is tight at 180 s; if you're long, trim the architecture beat, never the numbers.

## ✅ Verified before this script was written
- `24/24` pytest tests pass (offline).
- `./scripts/demo.sh` runs clean: handshake → `tools/list` (2 tools) → `list_regimes` →
  `get_market_regime` → regime **RANGE_BOUND** (as of 2026-06-17, BTC $65,598.94, composite −0.154).
- Backtest (`results/metrics.json`): strategy −12.7% / maxDD −24.2% / vol 19.3% / Sharpe −0.82 /
  $8,733 on $10k — vs buy-and-hold −37.4% / maxDD −51.2% / vol 43.1% / $6,264.

> ⛔ **APPROVAL GATE:** do not publish the video or submit anywhere until Eric approves.
