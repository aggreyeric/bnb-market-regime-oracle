"""MCP server: expose the Market Regime Oracle as a CMC Agent Hub skill.

Runs the Model Context Protocol over stdio so any MCP-compatible client
(Claude Desktop, Cursor, OpenClaw, the CMC Agent Hub, …) can call the
``get_market_regime`` tool and receive a structured regime + posture read.

Connect (see ``packaging/cmc-skill/mcp_config.json``)::

    {
      "mcpServers": {
        "market-regime-oracle": {
          "command": "python",
          "args": ["-m", "market_regime_oracle.mcp_server"]
        }
      }
    }

Run standalone for debugging::

    python -m market_regime_oracle.mcp_server
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .classifier import RegimeClassifier, regime_to_posture
from .config import POSTURES, REGIMES, BacktestConfig, ClassifierConfig, DataConfig
from .data.loader import build_dataset
from .backtest import run_backtest


def _dirs() -> tuple[Path, Path]:
    base = Path(os.environ.get("MRO_HOME", "."))
    return base / "data_cache", base / "results"


def _run(symbol: str = "bitcoin", days: str = "365", force_refresh: bool = False) -> dict[str, Any]:
    cfg = DataConfig(coin_id=symbol, days=days)
    cache_dir, results_dir = _dirs()
    df = build_dataset(cfg, cache_dir, force_refresh=force_refresh)

    regime_df = RegimeClassifier(cfg=ClassifierConfig()).predict(df)
    bt = run_backtest(regime_df, BacktestConfig())

    last = regime_df.iloc[-1]
    regime = str(last["regime"])
    posture = regime_to_posture(regime)
    s, b = bt.metrics_strategy, bt.metrics_buy_hold

    snapshot = {
        "regime": regime,
        "regime_definition": {
            "RISK_ON": "uptrend — accumulate",
            "RANGE_BOUND": "sideways — hold/light",
            "RISK_OFF": "downtrend — defensive/reduce",
            "CAPITULATION": "panic sell-off — max defensive",
            "EUPHORIA": "blow-off top — take profit/reduce",
        }[regime],
        "recommended_posture": {
            "target_exposure": posture.target_exposure,
            "action": posture.action,
        },
        "as_of": str(regime_df.index[-1].date()),
        "btc_close": round(float(last["close"]), 2),
        "composite_score": round(float(last["composite"]), 3),
        "signal_scores": {
            "momentum": round(float(last.get("score_momentum", 0.0)), 3),
            "fear_greed": round(float(last.get("score_fear_greed", 0.0)), 3),
            "volatility": round(float(last.get("score_volatility", 0.0)), 3),
            "funding_proxy": round(float(last.get("score_funding", 0.0)), 3),
            "exchange_flows_proxy": round(float(last.get("score_exchange_flows", 0.0)), 3),
        },
        "regime_distribution_12m": {
            str(k): int(v) for k, v in regime_df["regime"].astype(str).value_counts().items()
        },
        "backtest_vs_buy_hold": {
            "window": [str(df.index.min().date()), str(df.index.max().date())],
            "strategy": {k: round(v, 4) for k, v in s.items()},
            "buy_hold": {k: round(v, 4) for k, v in b.items()},
        },
        "posture_table": {r: {"exposure": POSTURES[r].target_exposure,
                              "action": POSTURES[r].action} for r in REGIMES},
        "notes": (
            "Research/backtest output only — NOT a trade instruction. Funding and "
            "exchange-flow signals are documented proxies (no free public feed); "
            "see README 'Assumptions & proxies'."
        ),
    }
    return snapshot


mcp = FastMCP("market-regime-oracle")


@mcp.tool()
def get_market_regime(symbol: str = "bitcoin", days: str = "365",
                      force_refresh: bool = False) -> str:
    """Classify the current BTC market regime and return a trading posture read.

    Fuses 5 signals (momentum RSI/MACD, Fear & Greed, volatility, funding-rate
    proxy, exchange-flow proxy) into one of 5 regimes — RISK_ON, RANGE_BOUND,
    RISK_OFF, CAPITULATION, EUPHORIA — each mapped to a documented target
    exposure. Includes a backtest vs buy-and-hold for context.

    Args:
        symbol: CoinGecko coin id (default "bitcoin").
        days: lookback window, <=365 for CoinGecko free tier (default "365").
        force_refresh: re-fetch data ignoring the local cache.

    Returns:
        JSON string with regime, posture, signal scores, distribution, and
        backtest metrics.
    """
    snapshot = _run(symbol=symbol, days=days, force_refresh=force_refresh)
    return json.dumps(snapshot, indent=2)


@mcp.tool()
def list_regimes() -> str:
    """Return the 5 regimes with their documented trading postures."""
    return json.dumps(
        {r: {"target_exposure": POSTURES[r].target_exposure, "action": POSTURES[r].action}
         for r in REGIMES}, indent=2
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
