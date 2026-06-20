"""Market Regime Oracle.

A CMC Strategy Skill that fuses 5 market signals into a regime classifier
(RISK_ON / RISK_OFF / RANGE_BOUND / CAPITULATION / EUPHORIA), maps each regime
to a trading posture, and backtests the result against buy-and-hold.

Track 2 ONLY: research / backtest artifact. No live trading, no wallet, no
external submission.
"""

__version__ = "1.0.0"
__all__ = ["__version__"]
