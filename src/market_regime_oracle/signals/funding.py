"""Signal 1 — Perpetual funding rate sentiment.  [PROXY]

**Why a proxy?** Perpetual-futures funding rates are published per-exchange
(e.g. Binance/Bybit) and are **not** available from the two authorized free
public sources (CoinGecko, alternative.me). The hard rules forbid inventing
fake "real" funding data, so we derive a *clearly-labeled proxy* from the
available price series.

**Economic rationale.** Funding tends to be strongly **positive** when the
market is overheated and crowding long (strong, low-noise rallies — longs pay
shorts), and strongly **negative** during sharp unwinds (panics). We therefore
approximate funding pressure with a risk-adjusted momentum term: the recent
return scaled by its own volatility. This is the same information funding
*reflects* (crowded directional bets), reconstructed from price.

**Columns (all prefixed ``funding_proxy_`` to make the proxy explicit):**

* ``funding_proxy_return``   — N-day cumulative log-return.
* ``funding_proxy_vol``      — N-day realized stdev of log-returns.
* ``funding_proxy_sharpe``   — return / (vol * sqrt(N)) — crowded-direction proxy.

Score (``[-1, +1]``): ``tanh(funding_proxy_sharpe * scale)`` — positive during
overheated rallies (risk-on / euphoria-leaning), negative during flushes.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .base import Signal


class FundingSignal(Signal):
    name = "funding"
    is_proxy = True

    def __init__(self, lookback: int = 14, scale: float = 4.0):
        self.lookback = lookback
        self.scale = scale

    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        log_ret = np.log(df["close"] / df["close"].shift(1))
        ret_n = log_ret.rolling(self.lookback, min_periods=max(3, self.lookback // 2)).sum()
        vol_n = log_ret.rolling(self.lookback, min_periods=max(3, self.lookback // 2)).std()
        sharpe = ret_n / (vol_n * np.sqrt(self.lookback))
        df["funding_proxy_return"] = ret_n
        df["funding_proxy_vol"] = vol_n
        df["funding_proxy_sharpe"] = sharpe.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        return df

    def score(self, df: pd.DataFrame) -> pd.Series:
        score = np.tanh(df["funding_proxy_sharpe"] * self.scale)
        return score.clip(-1.0, 1.0).rename(self.name)
