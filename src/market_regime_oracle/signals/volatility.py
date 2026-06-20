"""Signal 5 — Volatility regime.  [REAL data]

Realized volatility from CoinGecko BTC daily log-returns.

* ``realized_vol``  — annualized rolling 21-day stdev of log-returns.
* ``vol_zscore``    — current vol vs its own ~6-month rolling mean (regime).
* ``return_skew``   — short-term skew of returns (crashes are negative-skew).

Bullishness score (``[-1, +1]``): low, calm vol is mildly risk-on; elevated,
spiking vol is risk-off. Score ≈ ``-tanh(vol_zscore)`` so a calm market scores
positive and a stress market scores negative.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .base import Signal


class VolatilitySignal(Signal):
    name = "volatility"
    is_proxy = False

    def __init__(self, vol_window: int = 21, z_window: int = 126, ann_days: int = 365):
        self.vol_window = vol_window
        self.z_window = z_window
        self.ann_days = ann_days

    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        log_ret = np.log(df["close"] / df["close"].shift(1))
        df["log_return"] = log_ret
        roll_std = log_ret.rolling(self.vol_window, min_periods=max(5, self.vol_window // 3)).std()
        df["realized_vol"] = roll_std * np.sqrt(self.ann_days)
        mean_vol = df["realized_vol"].rolling(self.z_window, min_periods=20).mean()
        std_vol = df["realized_vol"].rolling(self.z_window, min_periods=20).std()
        df["vol_zscore"] = (df["realized_vol"] - mean_vol) / std_vol.replace(0.0, np.nan)
        df["vol_zscore"] = df["vol_zscore"].fillna(0.0)
        return df

    def score(self, df: pd.DataFrame) -> pd.Series:
        # calm (z<0) -> risk-on; stressed (z>0) -> risk-off
        score = -np.tanh(df["vol_zscore"].fillna(0.0))
        return score.clip(-1.0, 1.0).rename(self.name)
