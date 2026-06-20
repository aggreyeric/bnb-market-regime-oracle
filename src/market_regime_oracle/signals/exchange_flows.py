"""Signal 3 — Exchange flow pressure.  [PROXY]

**Why a proxy?** True exchange inflow/outflow requires on-chain data
(Glassnode/CryptoQuant style) which is **not** free or authorized here. We
reconstruct a *clearly-labeled proxy* from CoinGecko **price + volume**, which
*is* authorized.

**Economic rationale.** Net exchange inflows (coins moving *to* exchanges) are
associated with selling pressure and often coincide with high-volume *down*
days; net outflows (coins leaving exchanges) coincide with accumulation and
high-volume *up* days. We therefore use **signed volume**: daily volume scaled
by the sign of the day's return, normalized against its rolling level. Positive
= accumulation/outflow-like (risk-on), negative = distribution/inflow-like
(risk-off).

**Columns (prefixed ``flow_proxy_``):**

* ``flow_proxy_signed``  — volume * sign(return), rolling-mean smoothed.
* ``flow_proxy_norm``    — signed volume / rolling mean(|volume|).

Score (``[-1, +1]``): ``tanh(flow_proxy_norm * scale)``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .base import Signal


class ExchangeFlowSignal(Signal):
    name = "exchange_flows"
    is_proxy = True

    def __init__(self, smooth: int = 7, vol_window: int = 30, scale: float = 2.5):
        self.smooth = smooth
        self.vol_window = vol_window
        self.scale = scale

    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        ret = df["close"].pct_change()
        signed = df["volume"] * np.sign(ret)
        signed = signed.rolling(self.smooth, min_periods=1).mean()
        base = df["volume"].rolling(self.vol_window, min_periods=5).mean().replace(0.0, np.nan)
        norm = (signed / base).replace([np.inf, -np.inf], np.nan).fillna(0.0)
        df["flow_proxy_signed"] = signed
        df["flow_proxy_norm"] = norm
        return df

    def score(self, df: pd.DataFrame) -> pd.Series:
        score = np.tanh(df["flow_proxy_norm"] * self.scale)
        return score.clip(-1.0, 1.0).rename(self.name)
