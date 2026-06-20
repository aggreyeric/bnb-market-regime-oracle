"""CoinGecko v3 free-tier fetcher for BTC daily close + volume.

Source: https://api.coingecko.com/api/v3  (public, free, key-less for this endpoint)
Endpoint: ``/coins/{id}/market_chart``  ->  prices, market_caps, total_volumes
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ..config import DataConfig
from .http import cached_json_get


def fetch_btc_price(cfg: DataConfig, cache_dir: Path, force_refresh: bool = False) -> pd.DataFrame:
    """Return a daily DataFrame indexed by UTC date with columns ``close``, ``volume``.

    CoinGecko returns ``prices`` as ``[ms_epoch, price]`` and ``total_volumes``
    as ``[ms_epoch, volume]`` at daily granularity when ``interval=daily``.
    """
    url = f"{cfg.coingecko_base}/coins/{cfg.coin_id}/market_chart"
    params = {
        "vs_currency": cfg.vs_currency,
        "days": cfg.days,
        "interval": cfg.interval,
    }
    payload = cached_json_get(url, cfg, cache_dir, params=params, force_refresh=force_refresh)

    prices = payload.get("prices") or []
    volumes = payload.get("total_volumes") or []
    if not prices:
        raise RuntimeError("CoinGecko returned no price data")

    def _to_series(rows, name):
        idx = [datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).date() for ms, _ in rows]
        vals = [float(v) for _, v in rows]
        return pd.Series(vals, index=pd.to_datetime(idx), name=name)

    close = _to_series(prices, "close")
    volume = _to_series(volumes, "volume") if volumes else pd.Series(
        index=close.index, dtype=float, name="volume"
    )

    df = pd.concat([close, volume], axis=1)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    # CoinGecko's "today" candle is partial; drop the last (in-progress) row.
    df = df.iloc[:-1] if len(df) > 1 else df
    df.index.name = "date"
    return df
