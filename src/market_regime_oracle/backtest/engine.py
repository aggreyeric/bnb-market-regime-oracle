"""Vector backtester + performance metrics."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ..config import BacktestConfig


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def _max_drawdown(equity: pd.Series) -> float:
    hwm = equity.cummax()
    dd = equity / hwm - 1.0
    return float(dd.min())


def compute_metrics(equity: pd.Series, cfg: BacktestConfig, turnover: float = 0.0) -> dict:
    """Return a dict of standard performance metrics for an equity curve."""
    rets = equity.pct_change().dropna()
    n = len(rets)
    years = n / cfg.trading_days_per_year if n else 1.0

    total_return = float(equity.iloc[-1] / equity.iloc[0] - 1.0)
    cagr = float((equity.iloc[-1] / equity.iloc[0]) ** (1.0 / years) - 1.0) if years > 0 else 0.0
    ann_vol = float(rets.std() * np.sqrt(cfg.trading_days_per_year))
    sharpe = float((rets.mean() * cfg.trading_days_per_year - cfg.risk_free_rate_annual) / ann_vol) if ann_vol > 0 else 0.0
    downside = rets[rets < 0]
    downside_vol = float(downside.std() * np.sqrt(cfg.trading_days_per_year)) if len(downside) else 0.0
    sortino = float((rets.mean() * cfg.trading_days_per_year - cfg.risk_free_rate_annual) / downside_vol) if downside_vol > 0 else 0.0
    mdd = _max_drawdown(equity)
    win_rate = float((rets > 0).mean()) if n else 0.0

    return {
        "total_return": total_return,
        "cagr": cagr,
        "annualized_volatility": ann_vol,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_drawdown": mdd,
        "win_rate": win_rate,
        "turnover_per_day": turnover,
        "final_equity": float(equity.iloc[-1]),
    }


# ---------------------------------------------------------------------------
# Backtest
# ---------------------------------------------------------------------------

@dataclass
class BacktestResult:
    equity_strategy: pd.Series
    equity_buy_hold: pd.Series
    position: pd.Series
    regime: pd.Series
    trades: pd.DataFrame
    metrics_strategy: dict
    metrics_buy_hold: dict
    daily: pd.DataFrame

    def summary(self) -> pd.DataFrame:
        rows = []
        for k, v in self.metrics_strategy.items():
            rows.append({"metric": k, "strategy": v, "buy_hold": self.metrics_buy_hold.get(k)})
        return pd.DataFrame(rows)


class Backtester:
    """Run the regime-driven strategy against buy-and-hold."""

    def __init__(self, cfg: BacktestConfig | None = None):
        self.cfg = cfg or BacktestConfig()

    def run(self, regime_df: pd.DataFrame) -> BacktestResult:
        close = regime_df["close"]
        exposure = regime_df["target_exposure"].astype(float)

        # daily BTC return; realize it one day after the exposure decision
        ret = close.pct_change()
        position = exposure.shift(1).fillna(0.0)            # held over [t, t+1]
        gross = position * ret

        # transaction cost on exposure changes (rebalance at prior close)
        traded = position.diff().abs().fillna(position.abs())
        tc = self.cfg.transaction_cost_bps / 10_000.0
        cost = tc * traded
        net_ret = gross - cost

        # equity curves — seed day 0 with the initial capital (warm-up return = 0)
        net_ret = net_ret.fillna(0.0)
        eq_strat = (1.0 + net_ret).cumprod() * self.cfg.initial_capital
        eq_bh = (1.0 + ret.fillna(0.0)).cumprod() * self.cfg.initial_capital
        eq_strat.iloc[0] = self.cfg.initial_capital
        eq_bh.iloc[0] = self.cfg.initial_capital

        # trade log: rows where exposure changed
        change_mask = position.diff().abs().fillna(position.abs()) > 1e-9
        trades = pd.DataFrame({
            "date": regime_df.index,
            "regime": regime_df["regime"].astype(str).values,
            "prev_exposure": position.shift(1).fillna(0.0).values,
            "new_exposure": position.values,
            "turnover": traded.values,
        })
        trades = trades[change_mask.values].reset_index(drop=True)

        # equity series now starts cleanly at initial capital
        eq_s = eq_strat
        eq_b = eq_bh

        avg_turnover = float(traded.dropna().mean()) if len(traded) else 0.0

        daily = pd.DataFrame({
            "close": close,
            "btc_return": ret,
            "regime": regime_df["regime"].astype(str),
            "exposure": exposure,
            "position_held": position,
            "strategy_return": net_ret,
            "equity_strategy": eq_strat,
            "equity_buy_hold": eq_bh,
        })

        return BacktestResult(
            equity_strategy=eq_s,
            equity_buy_hold=eq_b,
            position=position,
            regime=regime_df["regime"].astype(str),
            trades=trades,
            metrics_strategy=compute_metrics(eq_s, self.cfg, avg_turnover),
            metrics_buy_hold=compute_metrics(eq_b, self.cfg, 1.0),
            daily=daily,
        )


def run_backtest(regime_df: pd.DataFrame, cfg: BacktestConfig | None = None) -> BacktestResult:
    return Backtester(cfg).run(regime_df)
