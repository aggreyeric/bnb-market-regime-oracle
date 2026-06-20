"""Shared synthetic fixtures for offline tests (no network)."""
import numpy as np
import pandas as pd


def synthetic_market(n: int = 400, seed: int = 7) -> pd.DataFrame:
    """Build a deterministic BTC-like daily series with regimes embedded.

    Segments: uptrend -> blow-off -> chop -> crash -> panic -> recovery, so the
    classifier can observe every regime. Includes a Fear & Greed proxy and
    volume that co-move with returns.
    """
    rng = np.random.default_rng(seed)
    segs = [
        ("up", 90, 0.004, 0.012),     # steady uptrend
        ("blow", 30, 0.012, 0.025),   # euphoric blow-off
        ("chop", 70, 0.000, 0.010),   # sideways
        ("down", 70, -0.005, 0.014),  # downtrend
        ("panic", 40, -0.015, 0.040), # capitulation
        ("rec", 100, 0.003, 0.011),   # recovery
    ]
    rets, vol = [], []
    for _, m, mu, sd in segs:
        rets.append(rng.normal(mu, sd, m))
        vol.append(rng.normal(1.5e10, 3e9, m).clip(1e9))
    r = np.concatenate(rets)
    v = np.concatenate(vol)
    close = 100.0 * np.exp(np.cumsum(r))
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    # sentiment proxy: greed in uptrends, fear in panics
    fg = 50 + 2500 * pd.Series(r).rolling(10, min_periods=1).mean().clip(-0.04, 0.04)
    fg = fg.clip(2, 95).round(0)
    df = pd.DataFrame({"close": close, "volume": v, "fear_greed": fg.values}, index=dates)
    df.index.name = "date"
    return df
