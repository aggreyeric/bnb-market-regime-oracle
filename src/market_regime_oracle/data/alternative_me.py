"""Fear & Greed Index fetcher (alternative.me, public + free).

Source: https://api.alternative.me/fng/  ->  value in [0,100], classification,
timestamp (unix seconds, UTC midnight).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ..config import DataConfig
from .http import cached_json_get


def fetch_fear_greed(cfg: DataConfig, cache_dir: Path, force_refresh: bool = False) -> pd.DataFrame:
    """Return a daily DataFrame indexed by UTC date with ``fear_greed`` (0..100)."""
    params = {"limit": cfg.fng_limit, "format": "json"}
    payload = cached_json_get(cfg.fng_base, cfg, cache_dir, params=params, force_refresh=force_refresh)

    rows = payload.get("data") or []
    if not rows:
        raise RuntimeError("alternative.me returned no Fear & Greed data")

    dates, values = [], []
    for r in rows:
        ts = int(r["timestamp"])
        dates.append(datetime.fromtimestamp(ts, tz=timezone.utc).date())
        values.append(float(r["value"]))

    df = pd.DataFrame(
        {"fear_greed": values},
        index=pd.to_datetime(dates),
    )
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df.index.name = "date"
    return df
