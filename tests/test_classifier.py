"""Classifier: regime validity, posture mapping, fusion determinism (offline)."""
import numpy as np
import pandas as pd
import pytest

from market_regime_oracle.classifier import (
    RegimeClassifier, classify_row, regime_to_posture,
)
from market_regime_oracle.config import REGIMES, ClassifierConfig
from conftest import synthetic_market


@pytest.fixture(scope="module")
def regime_df():
    return RegimeClassifier().predict(synthetic_market())


def test_only_valid_regimes(regime_df):
    assert set(regime_df["regime"].astype(str)).issubset(set(REGIMES))


def test_posture_mapping_complete(regime_df):
    for r in REGIMES:
        p = regime_to_posture(r)
        assert 0.0 <= p.target_exposure <= 1.0
        assert p.action
    # exposure assigned for every row
    assert regime_df["target_exposure"].between(0, 1).all()


def test_all_five_regimes_observed(regime_df):
    # synthetic data is designed to exercise all 5 regimes
    assert set(regime_df["regime"].astype(str)) == set(REGIMES)


def test_classify_row_scalar_contract():
    cfg = ClassifierConfig()
    # euphoria: high greed + overbought + strong composite
    assert classify_row(0.5, 80, 75, 0.01, 0.0, cfg) == "EUPHORIA"
    # capitulation: extreme fear + acute flush
    assert classify_row(-0.8, 8, 12, -0.15, 0.5, cfg) == "CAPITULATION"
    # risk on
    assert classify_row(0.4, 55, 60, 0.01, -0.5, cfg) == "RISK_ON"
    # risk off
    assert classify_row(-0.4, 40, 45, -0.01, 0.5, cfg) == "RISK_OFF"
    # range
    assert classify_row(0.0, 50, 50, 0.0, 0.0, cfg) == "RANGE_BOUND"


def test_classifier_deterministic(regime_df):
    out2 = RegimeClassifier().predict(synthetic_market())
    pd.testing.assert_series_equal(
        regime_df["regime"].astype(str).reset_index(drop=True),
        out2["regime"].astype(str).reset_index(drop=True),
        check_names=False,
    )


def test_weights_normalized():
    clf = RegimeClassifier()
    assert pytest.approx(sum(clf._weights), abs=1e-9) == 1.0
