# CLAUDE.md

Guidance for AI coding assistants (Claude, Cursor, etc.) working on this repo.

## Overview

**Market Regime Oracle** — a 5-signal → 5-state BTC market-regime classifier with
posture mapping, backtested vs buy-and-hold. Built as an MCP Strategy Skill for the
CoinMarketCap Agent Hub (BNB AI Trading — Track 2). Deterministic, no look-ahead.

Regimes: `RISK_ON` · `RANGE_BOUND` · `RISK_OFF` · `CAPITULATION` · `EUPHORIA`,
each with a fixed target exposure.

## Tech Stack

- **Python 3.11+** (pure Python — no TypeScript in this repo)
- `requests` · `numpy` · `pandas` · `matplotlib` · `mcp` (stdio) · `pytest`
- Data: **CoinGecko** v3 free API (BTC OHLCV) + **alternative.me** (Fear & Greed)
- **No API keys required.** All sources are public/free.

## Commands

```bash
pip install -r requirements.txt
python main.py                          # fetch → classify → backtest → charts
PYTHONPATH=src python -m pytest tests/  # run tests (offline, no network)
PYTHONPATH=src python -m market_regime_oracle.mcp_server   # MCP stdio server
./scripts/demo.sh                       # 30s live MCP round-trip demo
docker compose up --build run           # full pipeline via Docker
docker compose up --build server        # MCP server via Docker
```

## Architecture

```
src/market_regime_oracle/
├── data/        # CoinGecko + alternative.me loaders → aligned daily features
├── signals/     # 5 signal modules: momentum(.30) fear_greed(.25)
│                #   funding(.15) flows(.15) vol(.15) — each → score [-1,+1]
├── classifier/  # weighted fusion → composite → priority rules → regime
├── backtest/    # vectorized engine, no look-ahead, incl. costs
├── viz/         # equity / drawdown / regime overlay charts
└── mcp_server.py  # MCP stdio server exposing the `get_market_regime` tool
```

The 5 signals are independent and unit-tested. The classifier is **deterministic**
with a fixed priority order: CAPITULATION > EUPHORIA > RISK_OFF > RISK_ON > RANGE_BOUND.
Funding rate & exchange flows have no free public feed — they're reconstructed from
price/volume as clearly-labeled **proxies**. The fusion layer is signal-agnostic,
so real feeds can be dropped in without touching the classifier.

## API / Transport

No HTTP API. Exposes a single MCP tool over **stdio**:
- `get_market_regime` → current regime, target exposure, posture, and per-signal breakdown.

Consumable by Claude Desktop, Cursor, or the CMC Agent Hub.

## Testing

- `PYTHONPATH=src python -m pytest tests/` — **24 tests, all offline** (no network needed).
- Signals, fusion, classifier rules, and backtest math are covered.
- After code changes, always run the full suite before committing.

## Important Notes

- **Never introduce look-ahead bias** in signals or backtest — features use only past data.
- Keep the classifier deterministic; priority order is load-bearing for posture mapping.
- Pin deps in `requirements.txt` (versions are already pinned — keep them pinned).
- Results land in `results/` (CSVs, `metrics.json`, PNG charts) — generated, don't hand-edit.
- This is a hackathon submission — **do not submit to any portal** without Eric's approval.
