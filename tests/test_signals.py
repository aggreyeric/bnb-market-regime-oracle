"""Each of the 5 signals is independently runnable and well-formed (offline)."""
import numpy as np
import pandas as pd
import pytest

from market_regime_oracle.signals import ALL_SIGNALS
from conftest import synthetic_market


@pytest.fixture(scope="module")
def df():
    return synthetic_market()


@pytest.mark.parametrize("cls", ALL_SIGNALS, ids=[c.name for c in ALL_SIGNALS])
def test_signal_score_range_and_no_nan(cls, df):
    sig = cls()
    enriched = sig.add_features(df.copy())
    sc = sig.score(enriched)
    assert isinstance(sc, pd.Series)
    assert sc.between(-1.0, 1.0).all(), f"{sig.name} score out of [-1,1]"
    assert int(sc.isna().sum()) == 0, f"{sig.name} has NaNs"


@pytest.mark.parametrize("cls", ALL_SIGNALS, ids=[c.name for c in ALL_SIGNALS])
def test_signal_idempotent_and_independent(cls, df):
    sig = cls()
    # runs on close+volume+fear_greed alone, no other signal required
    base = df[["close", "volume", "fear_greed"]].copy()
    a = sig.add_features(base.copy())
    b = sig.add_features(base.copy())
    col = [c for c in a.columns if c not in base.columns][0]
    pd.testing.assert_series_equal(a[col], b[col], check_names=False)


def test_signal_names_unique():
    names = [cls().name for cls in ALL_SIGNALS]
    assert len(names) == len(set(names)) == 5


def test_proxy_flags_documented():
    # funding + exchange_flows are the two documented proxies
    flags = {cls().name: cls().is_proxy for cls in ALL_SIGNALS}
    assert flags["funding"] is True
    assert flags["exchange_flows"] is True
    assert flags["momentum"] is False
    assert flags["fear_greed"] is False
    assert flags["volatility"] is False
