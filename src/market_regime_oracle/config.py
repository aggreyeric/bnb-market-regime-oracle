"""Central configuration & posture definitions for the Market Regime Oracle."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


# ---------------------------------------------------------------------------
# Trading posture per regime.
# Each regime maps to an explicit target exposure (fraction of capital deployed
# in BTC) plus documented action guidance. These are *strategy* parameters for
# the backtest, NOT live-trade signals.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Posture:
    regime: str
    target_exposure: float          # fraction of portfolio in BTC [0, 1]
    action: str                     # human-readable posture / action guidance

POSTURES: Dict[str, Posture] = {
    "RISK_ON": Posture(
        regime="RISK_ON",
        target_exposure=1.00,
        action="Uptrend / accumulation — full exposure to BTC.",
    ),
    "RANGE_BOUND": Posture(
        regime="RANGE_BOUND",
        target_exposure=0.40,
        action="Sideways / choppy — light exposure, hold core, avoid adding.",
    ),
    "RISK_OFF": Posture(
        regime="RISK_OFF",
        target_exposure=0.20,
        action="Downtrend / defensive — reduce risk, raise cash to 80%.",
    ),
    "CAPITULATION": Posture(
        regime="CAPITULATION",
        target_exposure=0.10,
        action="Panic sell-off / max defensive — near-full cash, wait for stabilization.",
    ),
    "EUPHORIA": Posture(
        regime="EUPHORIA",
        target_exposure=0.30,
        action="Blow-off top — take profit, reduce to 30%, fade strength.",
    ),
}

REGIMES = tuple(POSTURES.keys())


# ---------------------------------------------------------------------------
# Data source configuration (public, free, authorized sources only).
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DataConfig:
    coingecko_base: str = "https://api.coingecko.com/api/v3"
    coin_id: str = "bitcoin"
    vs_currency: str = "usd"
    days: str = "365"             # CoinGecko free public tier caps daily history at 365 days
    interval: str = "daily"
    fng_base: str = "https://api.alternative.me/fng/"
    fng_limit: int = 0            # 0 == all available history
    request_timeout: int = 40
    request_retries: int = 6
    user_agent: str = "market-regime-oracle/1.0 (research backtest)"


# ---------------------------------------------------------------------------
# Backtest configuration.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BacktestConfig:
    initial_capital: float = 10_000.0
    transaction_cost_bps: float = 10.0   # 0.10% per unit of turnover (round-trip ~20bps)
    risk_free_rate_annual: float = 0.04  # for Sharpe approximation
    trading_days_per_year: int = 365     # crypto trades every day


# ---------------------------------------------------------------------------
# Classifier thresholds (see classifier/fusion.py for the full rule hierarchy).
# ---------------------------------------------------------------------------

@dataclass
class ClassifierConfig:
    # composite (fusion) weights for the 5 signals — must sum to 1.0
    weights: Dict[str, float] = field(default_factory=lambda: {
        "momentum": 0.30,
        "fear_greed": 0.25,
        "funding": 0.15,
        "exchange_flows": 0.15,
        "volatility": 0.15,
    })
    # EUPHORIA: greed + overbought + strength (blow-off top region)
    euphoria_fg: float = 72.0
    euphoria_rsi: float = 70.0
    # CAPITULATION: acute panic — extreme fear + sharp recent flush or vol spike
    capitulation_fg: float = 14.0
    capitulation_recent: float = -0.10   # 7-day return <= this (acute flush)
    capitulation_vol_z: float = 2.5      # or realized-vol z-score spike
    # composite (fusion) magnitude used to split RISK_ON / RISK_OFF from RANGE
    range_abs_score: float = 0.18
    # trend regime split
    trend_lookback: int = 30
