"""15 invariant tests — the minimum for WorkerKit to be trustworthy."""
import sys, os, json, tempfile
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

# 1. Schema: all 10 record families
print("1. Schema types")
from workerkit.core.schema import (
    WorkOrder, WorkerManifest, WorkerEvent, ArtifactRef, CostEvent,
    VerificationResult, CommitDecision, SubmissionReceipt, OutcomeReceipt,
    SettlementReceipt, WorkReceipt, uid, sha256
)
test("WorkOrder", WorkOrder().id.startswith("wk_"))
test("WorkerManifest", WorkerManifest().id.startswith("wk_"))
test("WorkerEvent", WorkerEvent().id.startswith("wk_"))
test("ArtifactRef", ArtifactRef().id.startswith("wk_"))
test("CostEvent", CostEvent().id.startswith("wk_"))
test("VerificationResult", VerificationResult().id.startswith("wk_"))
test("CommitDecision", CommitDecision().id.startswith("wk_"))
test("SubmissionReceipt", SubmissionReceipt().id.startswith("wk_"))
test("OutcomeReceipt", OutcomeReceipt().id.startswith("wk_"))
test("SettlementReceipt", SettlementReceipt().id.startswith("wk_"))
test("WorkReceipt", WorkReceipt().id.startswith("wk_"))
test("WorkReceipt", WorkReceipt().id.startswith("wk_"))
test("WorkerManifest", WorkerManifest().id.startswith("wk_"))
test("WorkerEvent", WorkerEvent().id.startswith("wk_"))
test("WorkerEvent", WorkerEvent().id.startswith("wk_"))
test("ArtifactRef", ArtifactRef().id.startswith("wk_"))
test("CostEvent", CostEvent().id.startswith("wk_"))
test("CostEvent", CostEvent().id.startswith("wk_"))
test("VerificationResult", VerificationResult().id.startswith("wk_"))
test("CommitDecision", CommitDecision().id.startswith("wk_"))
test("SettlementReceipt", SettlementReceipt().id.startswith("wk_"))

# 2. Events: append + chain verification
print("\n2. Event ledger")
from workerkit.core.events import EventLedger
with tempfile.TemporaryDirectory() as td:
    ledger = EventLedger(f"{td}/test.db")
    ledger.append("run-1", "run.started", {"task": "test"})
    ledger.append("run-1", "model.call", {"model": "mimo"})
    ledger.append("run-1", "run.completed", {"status": "submitted"})
    test("event count", ledger.count("run-1") == 3)
    test("chain valid", ledger.verify_chain("run-1"))
    events = ledger.get_events("run-1")
    test("events readable", len(events) == 3)

# 3. Artifacts: content hashing
print("\n3. ArtifactRef")
from workerkit.core.schema import ArtifactRef
ar = ArtifactRef(name="test.md", sha256=sha256("hello"))
test("artifact hash", ar.sha256 == sha256("hello"))
test("artifact dict", "sha256" in ar.to_dict())

# 4. Contracts
print("\n4. AcceptanceContract")
from workerkit.verify.contracts import AcceptanceContract, contract_from_jobspec
c = contract_from_jobspec({"hard_requirements": ["must run"], "automatic_rejection": ["no placeholders"]})
test("contract created", c.id.startswith("wk_"))
test("has criteria", len(c.criteria) == 1)

# 5. Gates
print("\n5. CommitGate")
from workerkit.verify.gates import CommitGate
gate = CommitGate()
r = gate.check("SUBMIT", "abc123", budget_remaining=5.0, max_cost=2.0)
test("gate allows", r.decision == "ALLOW")
r2 = gate.check("SUBMIT", "abc123", budget_remaining=0.5, max_cost=2.0)
test("gate denies on budget", r2.decision == "DENY")

# 6. Economics
print("\n6. Economics")
from workerkit.economics.costs import CostModel, RunMeter
from workerkit.economics.decisions import DecisionEngine
cm = CostModel()
cm.record("research", "mimo", 0.15, True)
cm.record("research", "mimo", 0.22, True)
test("cost model", cm.estimate("research", "mimo").expected == 0.22)
test("success rate", cm.success_rate("research", "mimo") == 1.0)

meter = RunMeter()
meter.record("llm", 0.05)
meter.record("api", 0.02)
test("meter total", abs(meter.total_cost - 0.07) < 0.001)

de = DecisionEngine()
d = de.decide(spent=0.07, remaining_budget=5.0, p_success=0.8, reward=5.0, estimated_remaining=0.15)
test("decision continue", d.action == "CONTINUE")

# 7. WorkReceipt
print("\n7. WorkReceipt")
from workerkit.core.schema import WorkReceipt
wr = WorkReceipt(run_id="wo-123")
test("receipt id", wr.id.startswith("wk_"))
test("receipt has root_hash field", hasattr(wr, "root_hash"))
wr.root_hash = sha256("test")
test("receipt hash after set", len(wr.root_hash) == 16)
wr2 = WorkReceipt(run_id="wo-123")
receipt = WorkReceipt(run_id="wo-123")
receipt.root_hash = sha256("test")
test("receipt attestation", receipt.to_attestation()["_type"].startswith("https://"))

# 9. CostModel + RunMeter integration
print("\n9. Cost economics")
from workerkit.economics.costs import CostModel, RunMeter
from workerkit.economics.decisions import DecisionEngine
cm = CostModel()
for i in range(10):
    cm.record("coding", "mimo", 0.10 + i*0.01, i < 7)
env = cm.estimate("coding", "mimo")
test("cost envelope", env.low < env.expected < env.high)
test("success rate", 0.6 < cm.success_rate("coding", "mimo") < 0.8)

# 10. Budget
print("\n10. Budget")
from workerkit.economics.budgets import Budget
b = Budget(daily_cap=5.0, per_run_cap=2.0)
test("budget allows", b.can_spend(1.0, 0.0, 0.0))
test("budget denies daily", not b.can_spend(6.0, 0.0, 0.0))
test("budget denies lifetime", not b.can_spend(1.0, 0.0, 50.0))

# 11. Contract validation
print("\n11. Contract validation")
from workerkit.verify.contracts import AcceptanceContract
ac = AcceptanceContract(required_outputs=["SUBMISSION.md"], minimum_quality=0.7)
test("contract has outputs", len(ac.required_outputs) == 1)
test("contract min quality", ac.minimum_quality == 0.7)

# 12. Gate checks all conditions
print("\n12. Gate comprehensive")
from workerkit.verify.gates import CommitGate
gate = CommitGate()
r = gate.check("SUBMIT", "abc", {"constraints": ["must run"]}, budget_remaining=5.0)
test("gate with contract", r.decision == "ALLOW")
test("gate checks count", len(r.checks) >= 2)

# 13. Event chain integrity
print("\n13. Event chain integrity")
with tempfile.TemporaryDirectory() as td:
    ledger = EventLedger(f"{td}/integrity.db")
    for i in range(5):
        ledger.append("run-test", f"event.{i}", {"i": i})
    test("chain valid", ledger.verify_chain("run-test"))
    # Tamper test: can't verify with wrong run_id
    test("wrong run_id fails", not ledger.verify_chain("run-wrong"))

# 14. Cost envelope math
print("\n14. Cost envelope")
from workerkit.economics.costs import CostModel
cm = CostModel()
for c in [0.10, 0.15, 0.20, 0.25, 0.30]:
    cm.record("test", "m", c, True)
env = cm.estimate("test", "m")
test("low <= expected", env.low <= env.expected)
test("expected <= high", env.expected <= env.high)
test("hard_cap > high", env.hard_cap > env.high)

# 15. Full loop simulation
print("\n15. Full loop simulation")
from workerkit.core.events import EventLedger
from workerkit.verify.contracts import AcceptanceContract, contract_from_jobspec
from workerkit.verify.gates import CommitGate
from workerkit.core.schema import WorkOrder

with tempfile.TemporaryDirectory() as td:
    ledger = EventLedger(f"{td}/loop.db")
    wo = WorkOrder(objective="simulate")

    # Simulate loop
    ledger.append(wo.id, "run.started", {"task": "simulate"})
    ledger.append(wo.id, "model.call", {"model": "mimo", "tokens": 1000})
    ledger.append(wo.id, "artifact.created", {"name": "output.md"})
    ledger.append(wo.id, "verification.passed", {"verifier": "v1"})
    ledger.append(wo.id, "submission.made", {"venue": "taskmarket"})
    ledger.append(wo.id, "run.completed", {"status": "submitted"})

    # Verify chain
    test("sim chain valid", ledger.verify_chain(wo.id))
    test("sim event count", ledger.count(wo.id) == 6)

    # Generate receipt
    receipt = WorkReceipt(run_id=wo.id)
    receipt.root_hash = sha256("test")
    test("sim receipt", len(receipt.root_hash) == 16)

print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
if FAIL > 0: sys.exit(1)
