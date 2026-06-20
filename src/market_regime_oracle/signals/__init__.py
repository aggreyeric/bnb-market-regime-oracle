"""Signal modules — each of the 5 market signals, independently testable.

Convention
----------
Every signal exposes:

* ``name``                  — short identifier used by the classifier/weights.
* ``add_features(df) -> df``— pure feature engineering (adds columns, idempotent).
* ``score(df) -> Series``   — normalized bullishness in ``[-1, +1]`` where
                              ``+1`` = strong risk-on contribution and
                              ``-1`` = strong risk-off contribution.

Two signals (``funding``, ``exchange_flows``) have no free, authorized public
feed, so they are implemented as **clearly-labeled proxies** derived from the
available CoinGecko price/volume data. See each module's docstring.
"""

from .base import Signal
from .momentum import MomentumSignal
from .fear_greed import FearGreedSignal
from .volatility import VolatilitySignal
from .funding import FundingSignal
from .exchange_flows import ExchangeFlowSignal

ALL_SIGNALS = (
    MomentumSignal,
    FearGreedSignal,
    VolatilitySignal,
    FundingSignal,
    ExchangeFlowSignal,
)

__all__ = [
    "Signal",
    "MomentumSignal",
    "FearGreedSignal",
    "VolatilitySignal",
    "FundingSignal",
    "ExchangeFlowSignal",
    "ALL_SIGNALS",
]
