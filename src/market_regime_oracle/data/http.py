"""Resilient HTTP GET with exponential-backoff retries and on-disk JSON cache.

Keeps reruns free of redundant API calls (and gentle on the free rate limits of
CoinGecko / alternative.me). Cache files are keyed by a stable URL hash.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional

import requests

from ..config import DataConfig


def _cache_path(cache_dir: Path, url: str) -> Path:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    return cache_dir / f"{digest}.json"


def _get_with_retry(url: str, cfg: DataConfig, params: Optional[dict] = None,
                    headers: Optional[dict] = None) -> dict:
    """GET JSON with retries; raises RuntimeError after all retries fail."""
    hdrs = {"User-Agent": cfg.user_agent, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)

    last_err: Optional[Exception] = None
    for attempt in range(1, cfg.request_retries + 1):
        try:
            resp = requests.get(url, params=params, headers=hdrs, timeout=cfg.request_timeout)
            if resp.status_code == 429:
                # rate limited — back off harder
                wait = min(2 ** attempt, 30)
                time.sleep(wait)
                last_err = RuntimeError(f"429 rate limited (attempt {attempt})")
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:  # noqa: BLE001 — retry any transient error
            last_err = exc
            wait = min(2 ** attempt, 20)
            time.sleep(wait)

    raise RuntimeError(f"GET failed after {cfg.request_retries} retries: {url} :: {last_err}")


def cached_json_get(url: str, cfg: DataConfig, cache_dir: Path,
                    params: Optional[dict] = None, force_refresh: bool = False) -> Any:
    """GET ``url`` and cache the parsed JSON under ``cache_dir``.

    If a cached file exists and ``force_refresh`` is False, it is returned
    directly. Set ``force_refresh=True`` (or delete the cache file) to refetch.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    cpath = _cache_path(cache_dir, url)

    if cpath.exists() and not force_refresh:
        try:
            return json.loads(cpath.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            # corrupted cache — refetch
            cpath.unlink(missing_ok=True)

    data = _get_with_retry(url, cfg, params=params)
    cpath.write_text(json.dumps(data), encoding="utf-8")
    return data
