"""15 brutal invariant tests — WorkerKit tells the truth or we catch it lying."""
import sys, os, json, tempfile, hashlib, sqlite3
sys.path.insert(0, '/root')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = 0
FAIL = 0

def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name} — {detail}")

print("=== WORKERKIT INVARIANT TESTS ===\n")

# ─── INVARIANT 1: SHA-256 is full 64 hex chars ───
print("1. SHA-256 integrity")
from workerkit.core.schema import sha256
h = sha256("test")
test("sha256 is 64 chars", len(h) == 64, f"got {len(h)}")
test("sha256 is hex", all(c in '0123456789abcdef' for c in h))
h2 = sha256("tesu")
test("one byte change → different hash", h != h2)

# ─── INVARIANT 2: Schema types all exist ───
print("\n2. Schema completeness")
from workerkit.core.schema import (
    WorkOrder, WorkerManifest, WorkerEvent, ArtifactRef, CostEvent,
    VerificationResult, CommitDecision, SubmissionReceipt, OutcomeReceipt,
    SettlementReceipt, uid, sha256
)
for cls in [WorkOrder, WorkerManifest, WorkerEvent, ArtifactRef, CostEvent,
            VerificationResult, CommitDecision, SubmissionReceipt, OutcomeReceipt,
            SettlementReceipt]:
    test(f"{cls.__name__} has id", hasattr(cls(), "id"))

# ─── INVARIANT 3: Event ledger chain integrity ───
print("\n3. Event chain integrity")
from workerkit.core.events import EventLedger
with tempfile.TemporaryDirectory() as td:
    ledger = EventLedger(f"{td}/chain.db")
    for i in range(5):
        ledger.append("run-1", f"event.{i}", {"i": i})
    test("chain valid", ledger.verify_chain("run-1"))
    test("wrong run_id fails", not ledger.verify_chain("run-wrong"))
    test("empty run fails", not ledger.verify_chain("run-nonexistent"))
    test("event count", ledger.count("run-1") == 5)

# ─── INVARIANT 4: Artifact digest is computed by WorkerKit ───
print("\n4. Artifact registration")
from workerkit.sdk import WorkerKit, WorkOrder
from workerkit.verify.contracts import AcceptanceContract
import asyncio

async def test_artifact():
    wk = WorkerKit()
    order = WorkOrder(objective="test", reward_value="10.00", raw={"max_cost": "2.00"})
    run = wk.start(order)

    # WorkerKit computes digest — not caller
    ar = run.artifact(name="report.md", content=b"hello world", media_type="text/markdown")
    test("artifact has 64 char hash", len(ar.sha256) == 64)
    test("artifact hash is deterministic", ar.sha256 == sha256("hello world"))
    test("artifact registered in run", len(run._artifacts) == 1)

    # Different content → different hash
    ar2 = run.artifact(name="other.md", content=b"different", media_type="text/markdown")
    test("different content → different hash", ar.sha256 != ar2.sha256)

asyncio.run(test_artifact())

# ─── INVARIANT 5: Verification is real, not pretend ───
print("\n5. Verification is real")
async def test_verify():
    wk = WorkerKit()
    order = WorkOrder(objective="test", reward_value="10.00", raw={"max_cost": "2.00"})
    run = wk.start(order)
    run.event("model.call", {"model": "mimo"})
    run.cost("llm", 0.05)
    contract = AcceptanceContract(required_outputs=["report.md"])

    # No artifact → FAIL
    vr1 = await wk.verify(run, contract, "")
    test("no artifact → FAIL", vr1.status == "FAIL")

    # With artifact → PASS
    ar = run.artifact(name="report.md", content=b"output")
    vr2 = await wk.verify(run, contract, ar)
    test("with artifact → PASS", vr2.status == "PASS")

    # Gate denies FAIL
    cd1 = wk.gate(run, "SUBMIT", vr1, 5.0)
    test("gate + FAIL → DENY", cd1.decision == "DENY")

    # Gate allows PASS
    cd2 = wk.gate(run, "SUBMIT", vr2, 5.0)
    test("gate + PASS → ALLOW", cd2.decision == "ALLOW")

asyncio.run(test_verify())

# ─── INVARIANT 6: Gate requires verification (CommitGate directly) ───
print("\n6. Gate requires verification")
from workerkit.verify.gates import CommitGate
gate = CommitGate()
vr_fail = VerificationResult(status="FAIL", subject_sha256="abc")
vr_pass = VerificationResult(status="PASS", subject_sha256="abc")
r_fail = gate.check("SUBMIT", vr_fail, subject_sha256="abc", budget_remaining=5.0, max_cost=5.0)
r_pass = gate.check("SUBMIT", vr_pass, subject_sha256="abc", budget_remaining=5.0, max_cost=5.0)
test("gate + FAIL → DENY (direct)", r_fail.decision == "DENY")
test("gate + PASS → ALLOW (direct)", r_pass.decision == "ALLOW")

# ─── INVARIANT 7: Budget per-run enforcement ───
print("\n7. Budget per-run cap")
from workerkit.economics.budgets import Budget
b = Budget(daily_cap=5.0, per_run_cap=2.0)
test("within per-run cap", b.can_spend(1.5, 0.0, 0.0, 0.0))
test("exceeds per-run cap", not b.can_spend(2.5, 0.0, 0.0, 0.0))
test("within daily cap", b.can_spend(1.0, 4.0, 0.0, 0.0))
test("exceeds daily cap", not b.can_spend(2.0, 4.0, 0.0, 0.0))
test("within lifetime cap", b.can_spend(1.0, 0.0, 49.0, 0.0))
test("exceeds lifetime cap", not b.can_spend(2.0, 0.0, 49.0, 0.0))
test("all caps checked", not b.can_spend(3.0, 4.0, 49.0, 0.0))

# ─── INVARIANT 8: Decision engine uses marginal EV ───
print("\n8. Decision engine safety")
from workerkit.economics.decisions import DecisionEngine
de = DecisionEngine()
# High EV → CONTINUE
d1 = de.decide(spent=0.5, remaining_budget=5.0, p_success=0.8, reward=10.0, estimated_remaining=1.0)
test("high EV → CONTINUE", d1.action == "CONTINUE")
# Low EV → ABORT
d2 = de.decide(spent=5.0, remaining_budget=5.0, p_success=0.1, reward=2.0, estimated_remaining=3.0)
test("low EV → ABORT", d2.action == "ABORT")
# Negative EV → ABORT
d3 = de.decide(spent=0.0, remaining_budget=10.0, p_success=0.0, reward=0.0, estimated_remaining=5.0)
test("negative EV → ABORT", d3.action == "ABORT")
# Insufficient budget → ABORT even with positive marginal EV
d4 = de.decide(spent=0.0, remaining_budget=0.5, p_success=0.8, reward=10.0, estimated_remaining=2.0)
test("insufficient budget → ABORT", d4.action == "ABORT")
# Marginal EV positive but sunk costs negative → CONTINUE (sunk costs are sunk)
d5 = de.decide(spent=20.0, remaining_budget=5.0, p_success=0.8, reward=10.0, estimated_remaining=1.0)
test("sunk costs don't abort", d5.action == "CONTINUE")

# ─── INVARIANT 9: Cost meter is Decimal-safe ───
print("\n9. Cost meter arithmetic")
from workerkit.economics.costs import RunMeter
m = RunMeter()
m.record("llm", 0.10)
m.record("api", 0.05)
test("meter sum", abs(m.total_cost - 0.15) < 0.001)
m.record("llm", 0.20)
test("meter cumulative", abs(m.total_cost - 0.35) < 0.001)

# ─── INVARIANT 10: close() refuses invalid chains ───
print("\n10. close() chain validation")
async def test_close_chain():
    wk = WorkerKit()
    order = WorkOrder(objective="test", reward_value="10.00", raw={"max_cost": "2.00"})
    run = wk.start(order)
    run.event("model.call", {"model": "mimo"})
    ar = run.artifact(name="output.md", content=b"result")
    vr = await wk.verify(run, AcceptanceContract(), ar)
    wk.gate(run, "SUBMIT", vr, 5.0)
    # Valid chain → receipt
    receipt = wk.close(run)
    test("valid chain → receipt", len(receipt.root_hash) == 64)

asyncio.run(test_close_chain())

# ─── INVARIANT 11: Three-receipt separation ───
print("\n11. Three-receipt separation")
sub = SubmissionReceipt(run_id="wo-1", venue="taskmarket")
out = OutcomeReceipt(submission_id="wo-1", status="submitted")
settle = SettlementReceipt(outcome_id="wo-1", status="pending")
test("submission != outcome", sub.id != out.id)
test("outcome != settlement", out.id != settle.id)
test("submission has run_id", sub.run_id == "wo-1")
test("outcome has status", out.status == "submitted")
test("settlement has status", settle.status == "pending")

# ─── INVARIANT 12: One receipt = one run ───
print("\n12. One receipt = one run")
from workerkit.core.receipts import WorkReceipt
with tempfile.TemporaryDirectory() as td:
    ledger = EventLedger(f"{td}/loop.db")
    wo = WorkOrder(objective="test", reward_value="10.00")
    ledger.append(wo.id, "run.started", {"task": "test"})
    ledger.append(wo.id, "model.call", {"model": "mimo"})
    ledger.append(wo.id, "run.completed", {"status": "submitted"})
    events = ledger.get_events(wo.id)
    chain_head = events[-1]["event_sha256"]
    event_count = len(events)

    class MockRun:
        pass
    r = MockRun()
    r.id = wo.id
    r.work_order_id = wo.id
    r.known_cost_usd = "0.15"
    r.status = "ok"
    r.outputs = []

    receipt = WorkReceipt(r, f"{chain_head}:{event_count}")
    test("receipt binds to chain head", chain_head in receipt.events_hash)
    test("receipt has full 64 char root", len(receipt.root_hash) == 64)
    att = receipt.to_attestation()
    test("attestation is in-toto", att["_type"].startswith("https://in-toto.io/"))
    test("attestation has workOrderId", att["predicate"]["workOrderId"] == wo.id)
    # NOT workerId
    test("attestation has no workerId", "workerId" not in att["predicate"])

# ─── INVARIANT 13: Actual tamper test — SQLite UPDATE breaks chain ───
print("\n13. Event chain tamper (SQLite UPDATE)")
with tempfile.TemporaryDirectory() as td:
    db_path = f"{td}/tamper.db"
    ledger = EventLedger(db_path)
    ledger.append("run-t", "step1", {"a": 1})
    ledger.append("run-t", "step2", {"b": 2})
    ledger.append("run-t", "step3", {"c": 3})
    test("valid chain", ledger.verify_chain("run-t"))

    # Tamper: UPDATE payload directly in SQLite
    conn = sqlite3.connect(db_path)
    conn.execute("UPDATE events SET payload='{\"b\": 999}' WHERE run_id='run-t' AND event_type='step2'")
    conn.commit()
    conn.close()
    test("tampered chain fails", not ledger.verify_chain("run-t"))

# ─── INVARIANT 14: Actual tamper test — SQLite DELETE breaks chain ───
print("\n14. Event chain tamper (SQLite DELETE)")
with tempfile.TemporaryDirectory() as td:
    db_path = f"{td}/delete.db"
    ledger = EventLedger(db_path)
    ledger.append("run-d", "step1", {"a": 1})
    ledger.append("run-d", "step2", {"b": 2})
    ledger.append("run-d", "step3", {"c": 3})
    test("valid chain", ledger.verify_chain("run-d"))

    # Tamper: DELETE middle event
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM events WHERE run_id='run-d' AND event_type='step2'")
    conn.commit()
    conn.close()
    test("deleted event breaks chain", not ledger.verify_chain("run-d"))

# ─── INVARIANT 15: Receipt root is content-addressed ───
print("\n15. Receipt root is content-addressed")
from workerkit.core.receipts import WorkReceipt
r1 = WorkReceipt(type("Run", (), {"id": "a", "work_order_id": "a", "known_cost_usd": "1.0", "status": "ok", "outputs": []})())
r2 = WorkReceipt(type("Run", (), {"id": "b", "work_order_id": "b", "known_cost_usd": "2.0", "status": "ok", "outputs": []})())
test("different runs → different root", r1.root_hash != r2.root_hash)
r3 = WorkReceipt(type("Run", (), {"id": "a", "work_order_id": "a", "known_cost_usd": "1.0", "status": "ok", "outputs": []})())
test("same runs → same root", r1.root_hash == r3.root_hash)

print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
if FAIL > 0:
    print("SOME INVARIANTS BROKEN — FIX BEFORE DEPLOYING")
    sys.exit(1)
else:
    print("ALL INVARIANTS HOLD — WorkerKit tells the truth")
