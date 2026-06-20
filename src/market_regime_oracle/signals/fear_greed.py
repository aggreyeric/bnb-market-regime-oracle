"""Signal 2 — Fear & Greed Index.  [REAL data]

Source: alternative.me Fear & Greed Index in ``[0, 100]``.

We interpret sentiment **directionally** for regime fusion: high greed is a
risk-on contribution, deep fear a risk-off contribution. (The classifier's
extreme-regime logic separately uses raw F&G thresholds for EUPHORIA vs
CAPITULATION, so contrarian behavior at the tails is handled there, not here.)
"""

from __future__ import annotations

import pandas as pd

from .base import Signal


class FearGreedSignal(Signal):
    name = "fear_greed"
    is_proxy = False

    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        fg = df["fear_greed"]
        # rolling mean smooths day-to-day noise in the sentiment print
        df["fear_greed_smooth"] = fg.rolling(5, min_periods=1).mean()
        return df

    def score(self, df: pd.DataFrame) -> pd.Series:
        fg = df["fear_greed_smooth"]
        # 50 -> 0 (neutral), 100 -> +1 (greed), 0 -> -1 (fear)
        score = ((fg - 50.0) / 50.0).clip(-1.0, 1.0)
        return score.rename(self.name)
