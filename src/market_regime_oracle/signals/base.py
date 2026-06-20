"""Abstract base for all signal modules."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Signal(ABC):
    """A single market signal.

    Subclasses implement ``add_features`` (feature engineering on the shared
    DataFrame) and ``score`` (normalized bullishness ``[-1, +1]``).
    """

    #: short id; must match a key in ``ClassifierConfig.weights``
    name: str = "signal"

    #: ``True`` if this signal uses real authorized data, ``False`` if it is a
    #: documented proxy/synthetic placeholder for data with no free public feed.
    is_proxy: bool = False

    @abstractmethod
    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived feature columns to ``df`` and return it (idempotent)."""

    @abstractmethod
    def score(self, df: pd.DataFrame) -> pd.Series:
        """Return a normalized bullishness score in ``[-1, +1]``."""

    # convenience: run feature engineering + scoring in one call
    def compute(self, df: pd.DataFrame) -> pd.Series:
        enriched = self.add_features(df.copy())
        return self.score(enriched)
