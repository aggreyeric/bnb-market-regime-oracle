# Market Regime Oracle — CMC Agent Hub Skill Packaging

This directory packages the Market Regime Oracle as a **CoinMarketCap Agent Hub
Strategy Skill**, delivered as an MCP (Model Context Protocol) server that any
MCP-compatible client can call — the same model the CMC Agent Hub uses.

## Files

| file | purpose |
|---|---|
| `skill.md` | Human-readable skill manifest in the CMC marketplace format (what / use-when / inputs / outputs / limits). |
| `skill.json` | Machine-readable skill manifest. |
| `mcp_config.json` | MCP client config to connect to this skill (mirrors CMC's `mcp_config.json` shape). |

## What "a CMC Skill" is here

The CMC Agent Hub routes an agent's prompt to cloud **Skills** (structured compute
pipelines) over MCP. Each skill ships a manifest with: a name, a category, tags,
a *what / use-it-when / inputs / outputs / limits* description, and an MCP
connection. This packaging follows that exact shape.

The CMC MCP already exposes the raw primitives this skill fuses
(`get_crypto_technical_analysis`, `get_global_metrics_latest`,
`get_global_crypto_derivatives_metrics`, on-chain metrics). This skill is the
**fusion + posture** layer on top.

## Install & connect

```bash
# from the repo root
pip install -r requirements.txt
```

Add this block to your MCP client config (Claude Desktop, Cursor, OpenClaw,
VS Code, …) — it is the same structure as CMC's official config:

```json
{
  "mcpServers": {
    "market-regime-oracle": {
      "command": "python",
      "args": ["-m", "market_regime_oracle.mcp_server"],
      "env": { "PYTHONPATH": "./src", "MRO_HOME": "." }
    }
  }
}
```

Then ask your agent:

> *"What is the current BTC market regime and how much risk should I take?"*

The agent calls `get_market_regime` and returns the regime, posture, and a
backtest read.

## Verify the skill runs (stdio smoke test)

```bash
PYTHONPATH=src MRO_HOME=. python tests/_mcp_smoke.py
```

This performs a real `initialize` → `tools/list` → `tools/call` round-trip over
stdio and prints the responses.

## Hard rules (non-negotiable)

- **Track 2 only** — research/backtest. No live trading, no wallet, no token launch.
- **Not submitted to any portal** — only the admin approves submissions.
