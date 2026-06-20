"""End-to-end pipeline: fetch -> classify -> backtest -> charts -> save results.

Run as a module (``python -m market_regime_oracle.run``) or via ``main.py`` at the
repo root.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from .backtest import run_backtest
from .classifier import RegimeClassifier, regime_to_posture
from .config import POSTURES, REGIMES, BacktestConfig, ClassifierConfig, DataConfig
from .data.loader import build_dataset
from .viz import plot_all


def _posture_table_df() -> pd.DataFrame:
    rows = []
    for r in REGIMES:
        p = POSTURES[r]
        rows.append({"regime": p.regime, "target_exposure": p.target_exposure, "action": p.action})
    return pd.DataFrame(rows)


def run_pipeline(
    results_dir: Path | str = "results",
    cache_dir: Path | str = "data_cache",
    force_refresh: bool = False,
) -> dict:
    """Execute the full pipeline and persist all artifacts under ``results_dir``.

    Returns a dict with key metrics + paths.
    """
    results_dir = Path(results_dir)
    cache_dir = Path(cache_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # 1) data
    data_cfg = DataConfig()
    df = build_dataset(data_cfg, cache_dir, force_refresh=force_refresh)
    df.to_csv(results_dir / "dataset.csv")

    # 2) classify
    clf = RegimeClassifier(cfg=ClassifierConfig())
    regime_df = clf.predict(df)
    regime_df.to_csv(results_dir / "regime_timeseries.csv")

    posture_tbl = _posture_table_df()
    posture_tbl.to_csv(results_dir / "posture_mapping.csv", index=False)
    clf.weight_table().to_csv(results_dir / "signal_weights.csv", index=False)

    # 3) backtest
    bt = run_backtest(regime_df, BacktestConfig())
    bt.daily.to_csv(results_dir / "equity_curve.csv")
    bt.trades.to_csv(results_dir / "trades.csv", index=False)

    metrics = {"strategy": bt.metrics_strategy, "buy_hold": bt.metrics_buy_hold}
    (results_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))

    regime_dist = regime_df["regime"].astype(str).value_counts().rename("days")
    regime_dist.to_csv(results_dir / "regime_distribution.csv")

    # 4) charts
    chart_paths = plot_all(bt, regime_df, results_dir)

    return {
        "rows": int(len(df)),
        "date_range": [str(df.index.min().date()), str(df.index.max().date())],
        "metrics": metrics,
        "regime_distribution": regime_dist.to_dict(),
        "charts": {k: str(v) for k, v in chart_paths.items()},
        "results_dir": str(results_dir),
    }


def regime_snapshot(regime_df: pd.DataFrame, latest_n: int = 5) -> dict:
    """Return a compact, CMC-facing snapshot of the latest regimes + postures."""
    recent = regime_df.tail(latest_n)
    out = []
    for ts, row in recent.iterrows():
        regime = str(row["regime"])
        out.append({
            "date": str(ts.date()),
            "btc_close": round(float(row["close"]), 2),
            "regime": regime,
            "target_exposure": float(regime_to_posture(regime).target_exposure),
            "action": regime_to_posture(regime).action,
            "composite_score": round(float(row["composite"]), 3),
        })
    return {"latest": out[-1], "history": out}


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Market Regime Oracle pipeline")
    ap.add_argument("--results", default="results")
    ap.add_argument("--cache", default="data_cache")
    ap.add_argument("--refresh", action="store_true", help="force re-fetch data")
    args = ap.parse_args()
    summary = run_pipeline(args.results, args.cache, force_refresh=args.refresh)
    m = summary["metrics"]
    print("\n=== Market Regime Oracle — pipeline complete ===")
    print(f"Data: {summary['rows']} daily rows, {summary['date_range'][0]} -> {summary['date_range'][1]}")
    print(f"Regimes: {summary['regime_distribution']}")
    s, b = m["strategy"], m["buy_hold"]
    print(f"Strategy : return {s['total_return']*100:+.1f}% | maxDD {s['max_drawdown']*100:.1f}% | "
          f"Sharpe {s['sharpe']:.2f} | vol {s['annualized_volatility']*100:.1f}%")
    print(f"Buy&Hold : return {b['total_return']*100:+.1f}% | maxDD {b['max_drawdown']*100:.1f}% | "
          f"Sharpe {b['sharpe']:.2f} | vol {b['annualized_volatility']*100:.1f}%")
    print(f"Artifacts: {summary['results_dir']}")


if __name__ == "__main__":
    main()
