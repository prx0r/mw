"""Letta adapter tests — reference stateful runtime for Moltwork."""
import sys, os, json, tempfile, asyncio, hashlib
sys.path.insert(0, '/root')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS+=1; print(f"  ✓ {name}")
    else: FAIL+=1; print(f"  ✗ {name} — {detail}")

print("=== LETTA ADAPTER TESTS ===\n")

from workerkit.adapters.letta import LettaAdapter
from workerkit.adapters.base import RunContext
from workerkit.worker_manifest import WorkerManifest, build_manifest
from pathlib import Path

print("1. LettaAdapter with .af")
af = {"agents": [{"name": "researcher-v12", "id": "a1"}], "blocks": [{"label": "persona"}, {"label": "skills"}], "tools": [{"name": "web_search"}], "mcp_servers": ["moltwork"]}
with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False) as f:
    json.dump(af, f); af_path = f.name

async def run():
    global PASS, FAIL
    a = LettaAdapter(af_path=af_path)
    assert a.has_af and not a.has_server

    insp = await a.inspect()
    check("inspect worker_id", insp.worker_id == "researcher-v12")
    check("inspect tools", "web_search" in insp.tools)
    check("inspect blocks", "persona" in insp.memory_blocks)
    check("inspect hash", len(insp.state_hash) == 64)

    h = await a.health()
    check("health ok with af", h.ok and h.runtime == "letta")

    ctx = RunContext(budget_remaining=2.0)
    r = await a.execute({"title": "research", "description": "find data"}, ctx)
    check("execute returns NOT_EXECUTED (no server)", not r.ok and r.error_code == "NOT_EXECUTED")
    check("execute has error detail", "no Letta server" in r.error)

    # force_stub=True for testing only
    r_stub = await a.execute({"title": "research", "description": "find data"}, ctx, force_stub=True)
    check("force_stub returns ok", r_stub.ok)
    check("force_stub has trace", len(r_stub.trace_events) > 0)

    # No af, no server → NO_RUNTIME
    b = LettaAdapter()
    r_no = await b.execute({"title": "test"}, ctx)
    check("no runtime returns NO_RUNTIME", not r_no.ok and r_no.error_code == "NO_RUNTIME")
    h2 = await b.health()
    check("health fails without af/server", not h2.ok)

    # WorkerManifest
    m = build_manifest("researcher-v12", af_path=af_path, runtime_adapter="letta")
    check("manifest worker", m.worker_id == "researcher-v12")
    check("manifest agent hash", len(m.agent.sha256) == 64)
    check("manifest hash", len(m.manifest_hash()) == 64)
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as mf:
        m.save(mf.name)
        m2 = WorkerManifest.load(mf.name)
        check("manifest round-trip", m2.worker_id == "researcher-v12" and m2.agent.sha256 == m.agent.sha256)

    # Sanitize
    af_secret = {"agents": [{"name": "x", "api_key": "sk-123", "secret_token": "s"}], "blocks": []}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False) as f:
        json.dump(af_secret, f); sec_path = f.name
    with tempfile.NamedTemporaryFile(suffix='.af', delete=False) as out:
        LettaAdapter.sanitize_af(sec_path, out.name)
        sanitized = json.loads(Path(out.name).read_bytes())
        check("sanitize nulls secrets", sanitized["agents"][0]["api_key"] is None)

    # Runtime registry
    from workerkit.adapters import get_adapter
    inst = get_adapter("letta", af_path=af_path)
    check("registry returns LettaAdapter", inst.runtime == "letta")

asyncio.run(run())
print(f"\n=== {PASS} passed, {FAIL} failed ===")
if FAIL: sys.exit(1)
else: print("ALL LETTA TESTS PASS")
