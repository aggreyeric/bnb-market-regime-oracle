#!/usr/bin/env python3
"""Generate demo output for BNB Market Regime Oracle video."""
import sys, json
sys.path.insert(0, "src")

print("═══════════════════════════════════════════════════════════════════")
print("  Market Regime Oracle — BNB AI Trading Hackathon Demo")
print("═══════════════════════════════════════════════════════════════════")
print()

print("Step 1: Running test suite (24 tests)...")
print("─" * 60)
import subprocess
r = subprocess.run([".venv/bin/python", "-m", "pytest", "tests/", "-v", "--tb=short"],
                    capture_output=True, text=True)
for line in r.stdout.strip().split("\n"):
    if line.strip():
        print(line)
if r.returncode != 0 and r.stderr:
    print(r.stderr[-500:])
print()

print("Step 2: Running full pipeline (signals → classifier → backtest → charts)...")
print("─" * 60)
from market_regime_oracle.run import run_pipeline
from pathlib import Path
out = run_pipeline(results_dir="results", cache_dir="data_cache")
for k, v in out.items():
    if isinstance(v, Path):
        print(f"  {k}: {v}")
    else:
        print(f"  {k}: {v}")
print()

print("Step 3: Backtest Results vs Buy-and-Hold...")
print("─" * 60)
metrics = json.loads(open("results/metrics.json").read())
for k, v in metrics.items():
    print(f"  {k}: {v}")
print()

# Regime distribution
import pandas as pd
regimes = pd.read_csv("results/regime_timeseries.csv")
regime_counts = regimes["regime"].value_counts()
print("Regime distribution:")
for regime, count in regime_counts.items():
    pct = count / len(regimes) * 100
    bar = "█" * int(pct / 2)
    print(f"  {regime:20s} {bar} {pct:.1f}%")
print()

print("Step 4: MCP Server — tool the CMC Agent Hub would call...")
print("─" * 60)
print("  Endpoint: get_market_regime")
latest = regimes.iloc[-1]
print(f"  Latest regime: {latest['regime']}")
print(f"  Target exposure: {latest['target_exposure']*100:.0f}%")
print("  (This is the signal an AI trading agent would consume)")
print()

print("═══════════════════════════════════════════════════════════════════")
print("  ✅ Demo complete — Market Regime Oracle is submission-ready")
print("  Repo: https://github.com/aggreyeric/bnb-market-regime-oracle")
print("  Docker: docker compose up --build")
print("═══════════════════════════════════════════════════════════════════")
