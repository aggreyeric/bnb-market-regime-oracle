"""Chart generation — equity curves, regime overlay, drawdown, regime summary.

All functions write a PNG and return its path. Use ``matplotlib.use('Agg')``
(headless) so charts render in a container without a display.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # non-interactive backend
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..backtest import BacktestResult

# consistent regime color map
REGIME_COLORS = {
    "RISK_ON": "#16a34a",       # green
    "RANGE_BOUND": "#ca8a04",   # amber
    "RISK_OFF": "#2563eb",      # blue
    "CAPITULATION": "#dc2626",  # red
    "EUPHORIA": "#db2777",      # magenta
}


def _style(ax, title):
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.grid(True, alpha=0.25)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))


def plot_equity_curve(bt: BacktestResult, out_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(bt.equity_buy_hold.index, bt.equity_buy_hold.values,
            label="Buy & Hold (100% BTC)", color="#6b7280", linewidth=1.8)
    ax.plot(bt.equity_strategy.index, bt.equity_strategy.values,
            label="Regime Strategy", color="#0ea5e9", linewidth=2.2)
    ax.axhline(bt.equity_strategy.iloc[0], color="#9ca3af", linestyle="--", linewidth=1, alpha=0.7)
    ms, mb = bt.metrics_strategy, bt.metrics_buy_hold
    txt = (f"Strategy: {ms['total_return']*100:+.1f}%  "
           f"(maxDD {ms['max_drawdown']*100:.1f}%, Sharpe {ms['sharpe']:.2f})\n"
           f"B&H:      {mb['total_return']*100:+.1f}%  "
           f"(maxDD {mb['max_drawdown']*100:.1f}%, Sharpe {mb['sharpe']:.2f})")
    ax.text(0.012, 0.97, txt, transform=ax.transAxes, va="top", fontsize=9,
            bbox=dict(boxstyle="round", fc="white", ec="#d1d5db", alpha=0.9))
    ax.set_ylabel("Equity ($)")
    ax.legend(loc="lower left")
    _style(ax, "Equity Curve: Regime Strategy vs Buy & Hold")
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    return out_path


def plot_regime_overlay(regime_df: pd.DataFrame, out_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(11, 5.5))
    close = regime_df["close"]
    ax.plot(regime_df.index, close.values, color="#111827", linewidth=1.4, zorder=3)
    regimes = regime_df["regime"].astype(str)
    ymin, ymax = close.min(), close.max()
    for reg, color in REGIME_COLORS.items():
        mask = (regimes == reg).values
        if not mask.any():
            continue
        # shade background where regime is active
        ax.fill_between(regime_df.index, ymin, ymax, where=mask,
                        color=color, alpha=0.16, step="mid", zorder=1, label=reg)
    ax.set_ylabel("BTC close (USD)")
    ax.set_yscale("log")
    ax.legend(loc="upper right", ncol=5, fontsize=8)
    _style(ax, "BTC Price with Regime Overlay")
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    return out_path


def plot_drawdown(bt: BacktestResult, out_path: Path) -> Path:
    def dd(equity):
        return equity / equity.cummax() - 1.0
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.fill_between(bt.equity_buy_hold.index, dd(bt.equity_buy_hold).values * 100, 0,
                    color="#dc2626", alpha=0.30, label="Buy & Hold")
    ax.fill_between(bt.equity_strategy.index, dd(bt.equity_strategy).values * 100, 0,
                    color="#0ea5e9", alpha=0.55, label="Strategy")
    ax.set_ylabel("Drawdown (%)")
    ax.legend(loc="lower left")
    _style(ax, "Drawdown: Strategy vs Buy & Hold")
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    return out_path


def plot_regime_summary(regime_df: pd.DataFrame, out_path: Path) -> Path:
    regimes = regime_df["regime"].astype(str)
    counts = regimes.value_counts()
    order = ["RISK_ON", "RANGE_BOUND", "RISK_OFF", "CAPITULATION", "EUPHORIA"]
    counts = counts.reindex([r for r in order if r in counts.index])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1, 1.4]})
    # left: regime share bar
    shares = counts / counts.sum() * 100
    ax1.barh(range(len(shares)), shares.values,
             color=[REGIME_COLORS[r] for r in shares.index])
    ax1.set_yticks(range(len(shares)))
    ax1.set_yticklabels(shares.index)
    ax1.invert_yaxis()
    ax1.set_xlabel("% of days")
    for i, v in enumerate(shares.values):
        ax1.text(v + 0.4, i, f"{v:.1f}%", va="center", fontsize=9)
    ax1.set_title("Regime distribution", fontweight="bold")
    ax1.grid(True, axis="x", alpha=0.25)

    # right: target exposure over time (the strategy's posture)
    ax2.fill_between(regime_df.index, 0, regime_df["target_exposure"].values * 100,
                     step="mid", color="#0ea5e9", alpha=0.5)
    ax2.set_ylabel("Target exposure (%)")
    ax2.set_ylim(0, 105)
    _style(ax2, "Target exposure over time (regime posture)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    return out_path


def plot_all(bt: BacktestResult, regime_df: pd.DataFrame, out_dir: Path) -> dict:
    """Generate the full demo chart set into ``out_dir``; return {name: path}."""
    out_dir.mkdir(parents=True, exist_ok=True)
    return {
        "equity_curve": plot_equity_curve(bt, out_dir / "equity_curve.png"),
        "regime_overlay": plot_regime_overlay(regime_df, out_dir / "regime_overlay.png"),
        "drawdown": plot_drawdown(bt, out_dir / "drawdown.png"),
        "regime_summary": plot_regime_summary(regime_df, out_dir / "regime_summary.png"),
    }
