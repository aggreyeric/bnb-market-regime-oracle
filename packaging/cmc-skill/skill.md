# Market Regime Oracle — CMC Strategy Skill

> A CoinMarketCap Agent Hub **Strategy Skill** (Track 2). Fuses 5 market signals
> into a 5-state regime classifier with an explicit trading posture per regime,
> backtested against buy-and-hold.

| field | value |
|---|---|
| **name** | `market-regime-oracle` |
| **category** | `research` / `risk` |
| **type** | Strategy Skill |
| **tags** | `market`, `BTC`, `regime`, `risk`, `sentiment-data`, `market-data`, `derivatives-market-data`, `daily`, `strategy`, `backtest` |
| **track** | BNB Chain AI Trading Agent Edition — Track 2 (Strategy Skills) |
| **transport** | MCP over stdio (Model Context Protocol) |

## What it does

Reviews the daily crypto backdrop across **momentum** (RSI/MACD), **sentiment**
(Fear & Greed), **realized volatility**, **perp funding pressure**, and
**exchange-flow pressure**, then returns a **conclusion-first market-regime read**
with a documented trading posture (target exposure + action) and a backtested
context vs buy-and-hold.

**Use it when** you need a single, explainable answer to *"what kind of market is
this right now, and how much risk should I take?"* — for daily risk-budgeting,
sizing a BTC allocation, or layering a regime gate on top of other CMC skills
(e.g. before acting on `daily market overview` or `perp contract analysis`).

**Do not use it for** live trade execution, order routing, wallet actions, or
token launches. It is a **research / backtest** signal, not a trade instruction.

## Inputs

| name | type | default | notes |
|---|---|---|---|
| `symbol` | string | `bitcoin` | CoinGecko coin id |
| `days` | string | `365` | lookback window (CoinGecko free tier ≤ 365 days daily) |
| `force_refresh` | bool | `false` | bypass the local data cache |

## Outputs (structured JSON)

- `regime` — one of `RISK_ON`, `RANGE_BOUND`, `RISK_OFF`, `CAPITULATION`, `EUPHORIA`
- `recommended_posture` — `{target_exposure, action}` for the latest day
- `composite_score` — fused signal score in `[-1, +1]`
- `signal_scores` — per-signal breakdown (5 signals)
- `regime_distribution_12m` — how often each regime occurred
- `backtest_vs_buy_hold` — total return, max drawdown, Sharpe, Sortino, vol
- `posture_table` — the full regime → exposure → action map

## Regime → posture mapping

| Regime | Target exposure | Action |
|---|---|---|
| `RISK_ON` | 100% | Uptrend / accumulation — full exposure |
| `RANGE_BOUND` | 40% | Sideways — light exposure, hold core |
| `RISK_OFF` | 20% | Downtrend — defensive, raise cash to 80% |
| `CAPITULATION` | 10% | Panic sell-off — max defensive, near-full cash |
| `EUPHORIA` | 30% | Blow-off top — take profit, fade strength |

## Limits

- **Research-only.** Output is a market-structure aid, not a standalone trade
  trigger or financial advice.
- **Two of the five signals are documented proxies.** Public, free feeds for
  perp funding rates and exchange on-chain flows are not available from the
  authorized sources (CoinGecko, alternative.me), so those two signals are
  *clearly-labeled proxies* reconstructed from price/volume. They are not fake
  "real" data. See the repo README → *Assumptions & proxies*.
- **History depth.** CoinGecko's free public tier returns ≤ 365 days of daily
  history without a demo API key, so the default backtest window is ~1 year.
- Returns a blocked data-availability error only if the authorized data sources
  are unreachable; it never fabricates market data.

## How it integrates with the CMC Agent Hub

The CMC MCP already exposes the raw ingredients this skill consumes
(`get_crypto_technical_analysis` for RSI/MACD, `get_global_metrics_latest` for
Fear & Greed, `get_global_crypto_derivatives_metrics` for funding, on-chain
metrics for flows). This skill is the higher-order **fusion + posture** layer on
top of those primitives.
