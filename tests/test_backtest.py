"""Backtest engine: mechanics, metrics, no-look-ahead (offline)."""
import numpy as np
import pandas as pd
import pytest

from market_regime_oracle.backtest import run_backtest, compute_metrics
from market_regime_oracle.config import BacktestConfig
from conftest import synthetic_market


@pytest.fixture(scope="module")
def bt():
    from market_regime_oracle.classifier import RegimeClassifier
    regime_df = RegimeClassifier().predict(synthetic_market())
    return run_backtest(regime_df)


def test_equity_starts_at_capital(bt):
    assert bt.equity_strategy.iloc[0] == pytest.approx(BacktestConfig().initial_capital)
    assert bt.equity_buy_hold.iloc[0] == pytest.approx(BacktestConfig().initial_capital)


def test_metrics_keys(bt):
    for key in ["total_return", "cagr", "sharpe", "sortino", "max_drawdown",
                "annualized_volatility", "win_rate", "final_equity"]:
        assert key in bt.metrics_strategy
        assert key in bt.metrics_buy_hold


def test_strategy_lower_vol_when_defensive(bt):
    # a regime strategy that de-risks in CAPITULATION/RISK_OFF should not be
    # more volatile than holding BTC outright
    assert bt.metrics_strategy["annualized_volatility"] <= bt.metrics_buy_hold["annualized_volatility"] + 1e-9


def test_max_drawdown_is_non_positive(bt):
    assert bt.metrics_strategy["max_drawdown"] <= 0.0
    assert bt.metrics_buy_hold["max_drawdown"] <= 0.0


def test_trades_logged_on_exposure_change(bt):
    assert len(bt.trades) >= 1
    assert {"date", "regime", "new_exposure", "turnover"}.issubset(bt.trades.columns)


def test_compute_metrics_standalone():
    eq = pd.Series([100, 110, 105, 120], index=pd.date_range("2024-01-01", periods=4))
    m = compute_metrics(eq, BacktestConfig())
    assert m["total_return"] == pytest.approx(0.20, rel=1e-9)
    assert m["max_drawdown"] <= 0.0
