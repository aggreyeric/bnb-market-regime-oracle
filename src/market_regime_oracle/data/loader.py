"""Build the aligned daily dataset used by all signal modules.

Joins BTC daily close/volume (CoinGecko) with the Fear & Greed Index
(alternative.me). Fear & Greed is forward-filled onto the price calendar so the
two series share one continuous daily timeline.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import DataConfig
from .alternative_me import fetch_fear_greed
from .coingecko import fetch_btc_price


def build_dataset(cfg: DataConfig, cache_dir: Path, force_refresh: bool = False) -> pd.DataFrame:
    """Fetch both sources and return an aligned daily DataFrame.

    Columns: ``close``, ``volume``, ``fear_greed``.
    """
    price = fetch_btc_price(cfg, cache_dir, force_refresh=force_refresh)
    fg = fetch_fear_greed(cfg, cache_dir, force_refresh=force_refresh)

    df = price.join(fg, how="left")
    # Fear & Greed is published daily but occasionally lags a day; ffill onto
    # the price calendar. Backward-fill the leading edge so early rows resolve.
    df["fear_greed"] = df["fear_greed"].ffill().bfill()
    df["volume"] = df["volume"].ffill().fillna(0.0)
    df["close"] = df["close"].ffill()

    df = df.dropna(subset=["close"]).sort_index()
    df.index.name = "date"
    return df


def load_dataset(path: Path) -> pd.DataFrame:
    """Reload a dataset previously persisted to CSV (no network)."""
    df = pd.read_csv(path, index_col="date", parse_dates=["date"])
    df.index.name = "date"
    return df
