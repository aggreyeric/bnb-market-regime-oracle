"""Signal-fusion regime classifier.

Combines the 5 signal scores into a single composite, then maps each day to
exactly one regime via a documented, priority-ordered rule hierarchy:

    1. CAPITULATION   (highest priority — extreme fear + crash)
    2. EUPHORIA       (extreme greed + blow-off)
    3. RISK_OFF       (composite strongly negative)
    4. RISK_ON        (composite strongly positive)
    5. RANGE_BOUND    (default — neutral / sideways)

The classifier is fully deterministic and parameterized by ``ClassifierConfig``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import ClassifierConfig, POSTURES, REGIMES
from ..signals import ALL_SIGNALS, Signal

# priority high -> low (later entries are defaults, earlier ones override)
REGIME_PRIORITY = ["CAPITULATION", "EUPHORIA", "RISK_OFF", "RISK_ON", "RANGE_BOUND"]


def regime_to_posture(regime: str):
    """Return the documented :class:`Posture` for ``regime``."""
    if regime not in POSTURES:
        raise KeyError(f"unknown regime {regime!r}; expected one of {REGIMES}")
    return POSTURES[regime]


def classify_row(composite, fear_greed, rsi, recent_ret, vol_z, cfg: ClassifierConfig) -> str:
    """Classify a single time step (scalar inputs). Exposed for testing.

    ``recent_ret`` is the short-term (7-day) BTC return used to detect acute
    capitulation flushes.
    """
    # 1. CAPITULATION — extreme fear + acute flush (sharp drop) or vol spike
    capit = fear_greed <= cfg.capitulation_fg and (
        recent_ret <= cfg.capitulation_recent or vol_z >= cfg.capitulation_vol_z
    )
    if capit:
        return "CAPITULATION"

    # 2. EUPHORIA — extreme greed + overbought + strong uptrend (blow-off)
    if fear_greed >= cfg.euphoria_fg and rsi >= cfg.euphoria_rsi and composite > 0.2:
        return "EUPHORIA"

    # 3/4. trending regimes by composite score
    if composite <= -cfg.range_abs_score:
        return "RISK_OFF"
    if composite >= cfg.range_abs_score:
        return "RISK_ON"

    # 5. default
    return "RANGE_BOUND"


class RegimeClassifier:
    """Run all signals, fuse, and assign a regime + posture per day."""

    def __init__(self, signals=None, cfg: ClassifierConfig | None = None,
                 high_water_window: int = 90):
        self.signals: list[Signal] = list(signals) if signals else [cls() for cls in ALL_SIGNALS]
        self.cfg = cfg or ClassifierConfig()
        self.high_water_window = high_water_window
        # weight vector aligned to the signal order
        self._weights = np.array([self._w(s.name) for s in self.signals], dtype=float)
        self._weights = self._weights / self._weights.sum()

    def _w(self, name: str) -> float:
        return float(self.cfg.weights.get(name, 0.0))

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a frame indexed like ``df`` with scores, composite, regime, exposure."""
        enriched = df.copy()
        score_cols = {}
        for sig in self.signals:
            enriched = sig.add_features(enriched)
            sc = sig.score(enriched)
            score_cols[sig.name] = sc.reindex(enriched.index).fillna(0.0)
        scores = pd.DataFrame(score_cols, index=enriched.index)

        # composite fusion (weighted sum of normalized scores)
        composite = scores.fillna(0.0).values @ self._weights
        enriched["composite"] = composite

        # drawdown vs rolling high-water mark (feature + used for analysis)
        hwm = enriched["close"].rolling(self.high_water_window, min_periods=10).max()
        enriched["drawdown"] = enriched["close"] / hwm - 1.0

        # short-term return — acute flush detector for CAPITULATION
        enriched["recent_return"] = enriched["close"].pct_change(7)

        # expose individual scores for transparency
        for col in scores.columns:
            enriched[f"score_{col}"] = scores[col]

        # vectorized regime assignment following the priority hierarchy
        fg = enriched["fear_greed"].values
        rsi = enriched["rsi"].values
        rret = enriched["recent_return"].fillna(0.0).values
        vz = enriched["vol_zscore"].values
        comp = composite

        regimes = np.array(["RANGE_BOUND"] * len(enriched), dtype=object)
        # base trending split
        regimes[comp >= self.cfg.range_abs_score] = "RISK_ON"
        regimes[comp <= -self.cfg.range_abs_score] = "RISK_OFF"
        # EUPHORIA override
        euphoria = (fg >= self.cfg.euphoria_fg) & (rsi >= self.cfg.euphoria_rsi) & (comp > 0.2)
        regimes[euphoria] = "EUPHORIA"
        # CAPITULATION override (highest priority): acute panic
        capit = (fg <= self.cfg.capitulation_fg) & (
            (rret <= self.cfg.capitulation_recent) | (vz >= self.cfg.capitulation_vol_z)
        )
        regimes[capit] = "CAPITULATION"

        enriched["regime"] = regimes
        enriched["target_exposure"] = np.array(
            [POSTURES[r].target_exposure for r in regimes], dtype=float
        )
        # categorical, ordered by priority
        enriched["regime"] = pd.Categorical(
            enriched["regime"], categories=REGIMES, ordered=False
        )
        return enriched

    def weight_table(self) -> pd.DataFrame:
        return pd.DataFrame(
            {"signal": [s.name for s in self.signals],
             "weight": self._weights,
             "is_proxy": [s.is_proxy for s in self.signals]},
        )
