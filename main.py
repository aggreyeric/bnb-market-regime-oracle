"""Convenience entry point: `python main.py` runs the full pipeline.

For the installable console script use `market-regime-oracle` (see pyproject.toml).
"""
from market_regime_oracle.run import main

if __name__ == "__main__":
    import sys
    from pathlib import Path
    # allow running directly from the repo root without installing
    src = Path(__file__).parent / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    main()
