"""Convenience entry point: `python main.py` runs the full pipeline.

For the installable console script use `market-regime-oracle` (see pyproject.toml).
"""
import sys
from pathlib import Path

# Bootstrap the src/ layout onto sys.path BEFORE importing the package, so that
# `python main.py` works from a fresh checkout without installing or setting
# PYTHONPATH. (Docker sets PYTHONPATH=/app/src already; this is a no-op there.)
_src = Path(__file__).resolve().parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from market_regime_oracle.run import main  # noqa: E402

if __name__ == "__main__":
    main()
