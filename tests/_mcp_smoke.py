"""Ad-hoc MCP stdio smoke test for the Market Regime Oracle skill."""
import json, subprocess, sys, threading, queue, time

p = subprocess.Popen([sys.executable, "-u", "-m", "market_regime_oracle.mcp_server"],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                     text=True, bufsize=1)

def send(obj):
    p.stdin.write(json.dumps(obj) + "\n"); p.stdin.flush()

def recv(timeout=20):
    q = queue.Queue()
    def t():
        q.put(p.stdout.readline())
    th = threading.Thread(target=t); th.daemon = True; th.start()
    try:
        return q.get(timeout=timeout)
    except queue.Empty:
        return None

send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
      "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                 "clientInfo": {"name": "smoke", "version": "0.0"}}})
print("INIT:", (recv() or "").strip()[:260])
send({"jsonrpc": "2.0", "method": "notifications/initialized"})

send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
tl = recv()
print("TOOLS/LIST:", (tl or "").strip()[:360])

send({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
      "params": {"name": "list_regimes", "arguments": {}}})
tr = recv()
print("TOOLS/CALL list_regimes:", (tr or "").strip()[:300])

p.terminate()
try:
    p.wait(timeout=5)
except subprocess.TimeoutExpired:
    p.kill()
print("SMOKE TEST OK")
