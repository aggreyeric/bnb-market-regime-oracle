"""Signal 4 — Momentum (RSI / MACD).  [REAL data]

Computed entirely from CoinGecko BTC daily closes:

* **RSI(14)** — Wilder's relative strength index.
* **MACD(12, 26, 9)** — EMA(12) − EMA(26), signal = EMA(9) of MACD, hist = diff.

Bullishness score (``[-1, +1]``): blends a centered RSI term with the MACD
histogram sign/strength so the signal responds both to overbought/oversold
levels and to trend acceleration.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .base import Signal


def _wilder_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    # Wilder smoothing == EMA with alpha = 1/period
    avg_gain = gain.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.fillna(50.0)


def _macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


class MomentumSignal(Signal):
    name = "momentum"
    is_proxy = False

    def __init__(self, rsi_period: int = 14, fast: int = 12, slow: int = 26, signal: int = 9):
        self.rsi_period = rsi_period
        self.fast, self.slow, self.signal = fast, slow, signal

    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["close"]
        df["rsi"] = _wilder_rsi(close, self.rsi_period)
        macd_line, signal_line, hist = _macd(close, self.fast, self.slow, self.signal)
        df["macd"] = macd_line
        df["macd_signal"] = signal_line
        df["macd_hist"] = hist
        return df

    def score(self, df: pd.DataFrame) -> pd.Series:
        rsi = df["rsi"]
        hist = df["macd_hist"]
        # RSI centered to [-1,1]: 50 -> 0, 70 -> +0.6, 30 -> -0.6, clipped
        rsi_term = ((rsi - 50.0) / 33.0).clip(-1.0, 1.0)
        # MACD histogram normalized by recent close magnitude -> dimensionless
        scale = (df["close"] * 0.01)  # ~1% of price as a soft scale
        hist_term = (hist / scale).clip(-1.0, 1.0)
        score = 0.6 * rsi_term + 0.4 * hist_term
        return score.clip(-1.0, 1.0).rename(self.name)
