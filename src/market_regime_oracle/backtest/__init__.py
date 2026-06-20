"""Backtest engine: regime-driven strategy vs buy-and-hold.

Decision model (no look-ahead): the regime and target exposure are decided at
day *t*'s close using only information up to and including day *t*; the resulting
position earns day *t → t+1*'s BTC return. Rebalancing from the prior exposure
to the new exposure incurs a linear transaction cost.
"""

from .engine import BacktestResult, Backtester, run_backtest, compute_metrics

__all__ = ["BacktestResult", "Backtester", "run_backtest", "compute_metrics"]
