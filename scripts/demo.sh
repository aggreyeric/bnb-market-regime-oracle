#!/usr/bin/env bash
#
# scripts/demo.sh — live MCP demo for the Market Regime Oracle skill
# ---------------------------------------------------------------------------
# Spins up the MCP server (Model Context Protocol over stdio) and drives a real
# JSON-RPC round trip against it: initialize -> tools/list -> tools/call
# (list_regimes + get_market_regime), pretty-printing each response.
#
# This is exactly what Claude Desktop / Cursor / the CMC Agent Hub do when they
# call the `get_market_regime` tool.
#
# Usage:
#   ./scripts/demo.sh                  # uses .venv if present, else system python3
#   ./scripts/demo.sh --no-network     # same, but refuses to run if cache is missing
#
# Requirements:
#   - PYTHONPATH / data cache are handled automatically (MRO_HOME=.)
#   - `get_market_regime` uses the on-disk data_cache/ if present (offline);
#     otherwise the first run hits the free public CoinGecko + alternative.me
#     APIs (no key). `list_regimes` is always offline.
#
set -euo pipefail

# --- resolve repo root (parent of this script's dir) ----------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# --- pick an interpreter: project venv preferred, else system python3 -----
if [[ -x ".venv/bin/python" ]]; then
  PY=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
else
  PY="$(command -v python)"
fi

# --- environment for the skill --------------------------------------------
export PYTHONPATH="src"
export MRO_HOME="."        # data_cache/ and results/ live at repo root
export MPLBACKEND=Agg      # headless matplotlib (charts never block)

# Optional --no-network guard: bail out if the cache is missing, so a demo
# never silently stalls on a network call.
if [[ "${1:-}" == "--no-network" ]]; then
  if [[ ! -d data_cache || -z "$(ls -A data_cache 2>/dev/null)" ]]; then
    echo "❌ --no-network set but data_cache/ is empty — get_market_regime would need network." >&2
    exit 1
  fi
fi

# --- sanity checks ---------------------------------------------------------
if ! "$PY" -c "import mcp" >/dev/null 2>&1; then
  echo "❌ Python 'mcp' SDK not found." >&2
  echo "   Install deps:  pip install -r requirements.txt" >&2
  exit 1
fi
if [[ ! -f src/market_regime_oracle/mcp_server.py ]]; then
  echo "❌ Could not find src/market_regime_oracle/mcp_server.py from $REPO_ROOT" >&2
  exit 1
fi

# ===========================================================================
# Drive the MCP server over stdio with a tiny embedded JSON-RPC client.
# ===========================================================================
"$PY" - <<'PYEOF'
import json, subprocess, sys, threading, queue

PROC_VERSION = "2024-11-05"


def hr(title: str) -> None:
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72)


def banner() -> None:
    hr("Market Regime Oracle — live MCP skill demo")
    print(
        "  Starting the MCP server (stdio) and performing a real JSON-RPC\n"
        "  round trip — the same call Claude Desktop / Cursor / the CMC\n"
        "  Agent Hub make to invoke `get_market_regime`."
    )


def pretty(obj) -> str:
    """Pretty-print a JSON-RPC result payload, handling MCP content blocks."""
    if isinstance(obj, dict) and "result" in obj:
        res = obj["result"]
        # tools/call responses wrap content in a list of {type:text,text:...}
        if isinstance(res, dict) and "content" in res:
            parts = [blk["text"] for blk in res["content"]
                     if isinstance(blk, dict) and blk.get("type") == "text"]
            joined = "\n".join(parts)
            try:
                return json.dumps(json.loads(joined), indent=2, ensure_ascii=False)
            except (ValueError, TypeError):
                return joined
        return json.dumps(res, indent=2, ensure_ascii=False)
    return json.dumps(obj, indent=2, ensure_ascii=False)


# --- launch the server -----------------------------------------------------
proc = subprocess.Popen(
    [sys.executable, "-u", "-m", "market_regime_oracle.mcp_server"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    text=True, bufsize=1,
)


def send(req: dict) -> None:
    proc.stdin.write(json.dumps(req) + "\n")
    proc.stdin.flush()


def recv(timeout: float = 25.0) -> dict | None:
    q: "queue.Queue[str | None]" = queue.Queue()

    def reader() -> None:
        line = proc.stdout.readline()
        q.put(line if line else None)

    t = threading.Thread(target=reader, daemon=True)
    t.start()
    try:
        line = q.get(timeout=timeout)
    except queue.Empty:
        return None
    if not line:
        return None
    try:
        return json.loads(line)
    except ValueError:
        err = proc.stderr.readline() if proc.stderr else ""
        print(f"  (non-JSON on stdout: {line.strip()!r}"
              f"{('  stderr: ' + err.strip()) if err else ''})")
        return None


_id = 0


def next_id() -> int:
    global _id
    _id += 1
    return _id


try:
    # 1) initialize ---------------------------------------------------------
    banner()
    hr("1) MCP handshake  →  initialize")
    send({
        "jsonrpc": "2.0", "id": next_id(), "method": "initialize",
        "params": {
            "protocolVersion": PROC_VERSION, "capabilities": {},
            "clientInfo": {"name": "demo.sh", "version": "1.0"},
        },
    })
    init = recv()
    if not init:
        raise SystemExit("❌ No response to initialize — server failed to start.")
    server_info = init.get("result", {}).get("serverInfo", {})
    print(f"  server name : {server_info.get('name', '?')}")
    print(f"  protocol    : {init.get('result', {}).get('protocolVersion', '?')}")
    print("  ✅ handshake OK")

    # required notification after initialize
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    # 2) tools/list ---------------------------------------------------------
    hr("2) Discover tools  →  tools/list")
    send({"jsonrpc": "2.0", "id": next_id(), "method": "tools/list", "params": {}})
    tl = recv()
    tools = tl.get("result", {}).get("tools", []) if tl else []
    for t in tools:
        print(f"  • {t['name']:22s} — {t.get('description', '').splitlines()[0]}")
    print(f"  ✅ {len(tools)} tool(s) advertised")

    # 3) tools/call list_regimes (offline, always works) --------------------
    hr("3) Ask the oracle  →  tools/call  list_regimes")
    send({"jsonrpc": "2.0", "id": next_id(), "method": "tools/call",
          "params": {"name": "list_regimes", "arguments": {}}})
    lr = recv()
    print(pretty(lr) if lr else "  (no response)")

    # 4) tools/call get_market_regime (uses cache or network) ---------------
    hr("4) Ask the oracle  →  tools/call  get_market_regime")
    send({"jsonrpc": "2.0", "id": next_id(), "method": "tools/call",
          "params": {"name": "get_market_regime",
                     "arguments": {"symbol": "bitcoin", "days": "365"}}})
    gr = recv(timeout=35.0)
    if gr:
        snap = json.loads(pretty(gr))
        print(f"  📅 as of            : {snap.get('as_of')}")
        print(f"  💰 BTC close        : ${snap.get('btc_close'):,.2f}")
        print(f"  🎯 current regime   : {snap.get('regime')}")
        print(f"     → {snap.get('regime_definition')}")
        post = snap.get("recommended_posture", {})
        print(f"  ⚖️  target exposure : {post.get('target_exposure')}  ({post.get('action')})")
        print(f"  🧮 composite score  : {snap.get('composite_score')}")
        scores = snap.get("signal_scores", {})
        print("  📊 signal scores    : "
              + ", ".join(f"{k}={v:+.2f}" for k, v in scores.items()))
        bt = snap.get("backtest_vs_buy_hold", {})
        strat, hold = bt.get("strategy", {}), bt.get("buy_hold", {})
        print("  📈 backtest vs B&H  : "
              f"strategy {strat.get('total_return', 0):+.1%} / "
              f"maxDD {strat.get('max_drawdown', 0):.1%}   |   "
              f"B&H {hold.get('total_return', 0):+.1%} / "
              f"maxDD {hold.get('max_drawdown', 0):.1%}")
        print("\n  --- full structured response ---")
        print(json.dumps(snap, indent=2, ensure_ascii=False))
    else:
        print("  (no response — if this hangs, the first run needs network to "
              "populate data_cache/; rerun once online, then it's offline forever)")

    hr("✅ Demo complete — the MCP skill answered every query over stdio")
finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
PYEOF
