"""Regime definitions, posture mapping, and ordering."""

from .fusion import REGIME_PRIORITY, RegimeClassifier, classify_row, regime_to_posture

# Re-export the canonical posture table (single source of truth in config.py)
from ..config import POSTURES, REGIMES, Posture  # noqa: F401

__all__ = [
    "REGIME_PRIORITY",
    "RegimeClassifier",
    "classify_row",
    "regime_to_posture",
    "POSTURES",
    "REGIMES",
    "Posture",
]
