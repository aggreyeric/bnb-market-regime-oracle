"""Data layer: public, free, authorized sources only (CoinGecko, alternative.me).

Modules
-------
http           : resilient GET with retries + on-disk JSON caching.
coingecko      : BTC daily close + volume from CoinGecko v3 (free).
alternative_me : Fear & Greed Index history from alternative.me (free).
loader         : builds the aligned daily feature DataFrame used by signals.
"""

from .loader import build_dataset, load_dataset

__all__ = ["build_dataset", "load_dataset"]
