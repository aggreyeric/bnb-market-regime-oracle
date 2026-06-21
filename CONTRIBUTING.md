# Contributing to Market Regime Oracle

Thanks for your interest in improving **Market Regime Oracle** — the 5-signal → 5-state BTC market-regime classifier.

We welcome contributions of all sizes: bug reports, signal improvements, new backtest features, MCP integrations, docs, and demos. This guide gets you from clone to PR in a few minutes.

---

## 🧭 Prerequisites — Read the README First

Before anything else, **read [`README.md`](./README.md)**. It explains:

- What the oracle does (5 regimes, posture mapping)
- The architecture (signals → fusion → classifier → backtest / MCP)
- The headline backtest result and data sources
- Why funding rate and exchange flows are *proxxies* (not real feeds)

You don't need to fully understand the backtest math to contribute, but you should know which regime maps to which posture. The README is the source of truth for project intent.

**Also required:**

- Python **3.11+**
- `git`
- Basic familiarity with `pip` and `pytest`
- No API keys needed (CoinGecko + alternative.me are free & public)

---

## 🛠️ Setup

```bash
git clone https://github.com/aggreyeric/bnb-market-regime-oracle.git
cd bnb-market-regime-oracle

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pip install -e ".[dev]"            # pulls in pytest
```

Verify the install runs end-to-end:

```bash
python main.py                     # fetch → classify → backtest → charts
```

A `results/` directory with CSVs, `metrics.json`, and PNG charts should appear.

---

## 🧪 Running Tests

Tests are **fully offline** — no network calls, deterministic fixtures.

```bash
PYTHONPATH=src python -m pytest tests/
```

You should see **24 passed**. If you see fewer, something in your branch is broken — fix it before opening a PR.

Run a single signal's tests while iterating:

```bash
PYTHONPATH=src python -m pytest tests/test_signals.py -k momentum
```

### Smoke-testing the MCP server

```bash
PYTHONPATH=src python -m market_regime_oracle.mcp_server   # stdio server
./scripts/demo.sh                                          # 30-second live round-trip
```

---

## 💻 Code Style

This project is Pythonic-first. No formatter is enforced yet, but please:

- **Type hints** on all public functions (`def foo(x: float) -> int:`).
- **Docstrings** on every signal/classifier function — what it scores, why.
- **No look-ahead** in signals or the backtest. Regime decisions for day *t* may use only data up to and including day *t*. This is non-negotiable; it's the entire thesis of the project.
- **One signal per file** under `src/market_regime_oracle/signals/`. Each returns a normalized score in `[-1, +1]`.
- **Pure functions** for the data pipeline wherever possible. Side effects (caching, plotting) belong at the edges.
- Keep dependencies minimal — every new `pip` requirement needs a justification in the PR description.

### Adding a new signal

1. Create `src/market_regime_oracle/signals/<your_signal>.py` returning `(-1.0, +1.0)`.
2. Add a unit test in `tests/test_signals.py`.
3. Wire it into the fusion layer with a weight that sums to **1.0** with the others.
4. Re-run the full backtest and report the new Sharpe / drawdown in your PR.

---

## 🐛 Reporting Issues

Open a GitHub Issue with:

1. **What you expected** (e.g. "regime = RISK_ON")
2. **What happened** (e.g. "classified as CAPITULATION")
3. **Reproduction**: the exact command and (if relevant) the date range or fixture
4. **Logs / traceback** — paste in a code block
5. **Your Python version and OS**

Screenshots of charts help a lot. Mark the issue with the appropriate label (`bug`, `enhancement`, `signal`, `docs`).

---

## 🔀 Pull Requests

1. **Fork & branch** from `main`: `feat/short-description`, `fix/...`, `docs/...`.
2. **Write tests first** where possible (TDD-friendly: signals are pure functions).
3. **Make sure `PYTHONPATH=src python -m pytest tests/` is green** — all 24 must pass.
4. **Don't regenerate committed `results/*.png` or `data_cache/`** unless your change is explicitly about the backtest output. (Stale diffs make review painful.)
5. **Keep PRs small and focused.** One signal, one fix, or one doc page per PR.
6. **Fill in the PR template** — what changed, why, test output, and any backtest impact.

A maintainer will review within a few days. Expect at least one round of feedback — that's normal and good.

---

## 🤝 Community

- Be kind. Disagree about code, not people.
- Crypto trading involves real money for real people — claims about performance must be **backed by the committed backtest**, not vibes. No "this signal prints money" without a Sharpe number.
- If you're unsure whether an idea fits the project, open a **Discussion** or an issue tagged `question` before writing code.

---

## 📜 License

By contributing, you agree that your contributions are licensed under the **MIT License** — see [`LICENSE`](./LICENSE). All merged PRs are MIT-licensed as part of this repository.

© 2026 Market Regime Oracle contributors.
