"""Full test suite for Moltwork evidence primitives.

Tests: workload, ACI, trace merkle, RunReceiptV1, execution plan,
agent lease, KMS auth, evidence log, chain adapters, integration.
"""
import sys, os, json, tempfile, time
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

print("=== MOLTWORK EVIDENCE PRIMITIVES TESTS ===\n")

# ─── 1. WorkloadManifestV1 + capability fingerprint ───
print("1. WorkloadManifestV1")
from evidence.workload import WorkloadManifestV1, compute_capability_hash
wm = WorkloadManifestV1(
    agent_id="agent-1",
    source_repository="github.com/prx0r/mw",
    source_commit="abc123",
    image_digests=["sha256:aaa", "sha256:bbb"],
    workerkit_version="0.1.0",
    compose_hash="compose123",
)
wid = wm.workload_id()
test("workload_id is 64 chars", len(wid) == 64)
# Same manifest → same ID
wm2 = WorkloadManifestV1(
    agent_id="agent-1",
    source_repository="github.com/prx0r/mw",
    source_commit="abc123",
    image_digests=["sha256:aaa", "sha256:bbb"],
    workerkit_version="0.1.0",
    compose_hash="compose123",
)
test("same manifest → same workload_id", wid == wm2.workload_id())
# Different manifest → different ID
wm3 = WorkloadManifestV1(agent_id="agent-2", source_commit="def456")
test("different manifest → different workload_id", wid != wm3.workload_id())
# Capability fingerprint
tools = [{"name": "web_search", "endpoint": "/search"}, {"name": "code_exec", "endpoint": "/exec"}]
cap_hash = compute_capability_hash(tools)
test("capability hash is 64 chars", len(cap_hash) == 64)
tools2 = [{"name": "web_search", "endpoint": "/search"}, {"name": "wallet_sign", "endpoint": "/sign"}]
cap_hash2 = compute_capability_hash(tools2)
test("different tools → different capability hash", cap_hash != cap_hash2)

# ─── 2. ACI receipts ───
print("\n2. ACI receipts")
from evidence.aci import ACIReceipt, HTTPEvidence, ToolInvocation, X402Settlement
aci = ACIReceipt(
    gateway_app_id="gw-1",
    provider="tinfoil",
    model="gpt-4",
    request_hash="req123",
    response_hash="res456",
    tokens_input=1000,
    tokens_output=500,
    cost_usd="0.04",
    provider_verification="VERIFIED",
    signature="sig123",
)
rh = aci.receipt_hash()
test("ACI receipt hash is 64 chars", len(rh) == 64)
aci2 = ACIReceipt(
    gateway_app_id="gw-1",
    provider="tinfoil",
    model="gpt-4",
    request_hash="req123",
    response_hash="res456",
    tokens_input=1000,
    tokens_output=500,
    cost_usd="0.04",
    provider_verification="VERIFIED",
    signature="sig123",
    timestamp=aci.timestamp,
)
test("same ACI → same hash", rh == aci2.receipt_hash())
# HTTP evidence
http = HTTPEvidence(method="GET", url="https://api.example.com", status_code=200, cost_usd="0.01")
test("HTTP evidence serializes", "method" in http.to_dict())
# Tool invocation
tool = ToolInvocation(tool_id="erc8257-1", tool_name="web_search", cost_usd="0.005")
test("tool invocation serializes", "toolId" in tool.to_dict())
# x402 settlement
x402 = X402Settlement(amount="1.00", payer="0xaaa", payee="0xbbb", tx_hash="0xccc")
test("x402 settlement serializes", "txHash" in x402.to_dict())

# ─── 3. Trace Merkle tree ───
print("\n3. Trace Merkle tree")
from evidence.trace import TraceEvent, TraceMerkleTree
events = [
    TraceEvent(sequence=0, event_type="aci_inference", request_hash="r1", response_hash="s1", provider="tinfoil", cost="0.04"),
    TraceEvent(sequence=1, event_type="http", request_hash="r2", response_hash="s2", provider="api.example", cost="0.01"),
    TraceEvent(sequence=2, event_type="tool", request_hash="r3", response_hash="s3", provider="web_search", cost="0.005"),
    TraceEvent(sequence=3, event_type="artifact", request_hash="r4", response_hash="s4", provider="local", cost="0"),
]
tree = TraceMerkleTree(events)
test("tree root is 64 chars", len(tree.root) == 64)
test("leaf count matches", tree.leaf_count == 4)
# Inclusion proof
proof = tree.get_proof(0)
test("proof is list", isinstance(proof, list))
test("proof has entries", len(proof) > 0)
leaf_hash = events[0].leaf_hash()
test("verify proof for leaf 0", tree.verify_proof(leaf_hash, proof, tree.root))
# Tamper: wrong leaf fails
test("verify wrong leaf fails", not tree.verify_proof("wrong", proof, tree.root))
# Empty tree
empty = TraceMerkleTree([])
test("empty tree has root", len(empty.root) == 64)
# Single event
single = TraceMerkleTree([events[0]])
test("single event tree", single.leaf_count == 1)

# ─── 4. RunReceiptV1 ───
print("\n4. RunReceiptV1")
from evidence.receipt import RunReceiptV1
rr = RunReceiptV1(
    run_id="run-001",
    agent_id="agent-001",
    workload_id="wl-001",
    work_order_hash="wo123",
    lease_hash="lease456",
    attestation_hash="att789",
    compose_hash="comp012",
    input_commitment="in345",
    output_commitment="out678",
    trace_root=tree.root,
    artifact_root="art901",
    tokens_used=5000,
    execution_cost="0.42",
    payment_reference="pay123",
    status="completed",
    tee_signer="pub123",
)
digest = rr.receipt_digest()
test("receipt digest is 64 chars", len(digest) == 64)
# Same data → same digest (set timestamps equal)
rr2 = RunReceiptV1(
    run_id="run-001", agent_id="agent-001", workload_id="wl-001",
    work_order_hash="wo123", lease_hash="lease456", attestation_hash="att789",
    compose_hash="comp012", input_commitment="in345", output_commitment="out678",
    trace_root=tree.root, artifact_root="art901", tokens_used=5000,
    execution_cost="0.42", payment_reference="pay123", status="completed",
    tee_signer="pub123",
)
rr2.started_at = rr.started_at
rr2.completed_at = rr.completed_at
test("same data → same digest", digest == rr2.receipt_digest())
# Different cost → different digest
rr3 = RunReceiptV1(run_id="run-001", execution_cost="0.99", tee_signer="pub123")
test("different cost → different digest", digest != rr3.receipt_digest())
# Save/load
with tempfile.TemporaryDirectory() as td:
    rr.save(td)
    with open(f"{td}/run-receipt.json") as f:
        loaded = json.load(f)
    test("receipt round-trips", loaded["run"]["runId"] == "run-001")
    test("receipt has traceRoot", loaded["commitments"]["traceRoot"] == tree.root)

# ─── 5. ExecutionPlan (PlanBound) ───
print("\n5. ExecutionPlan")
from evidence.plan import ExecutionPlan, PlanStep, PlanStatus
plan = ExecutionPlan(plan_id="plan-1", job_id="job-1", agent_id="agent-1", total_ceiling="1.00")
plan.add_step(PlanStep(step_id="s1", description="LLM call", provider="openai", method="model.call", estimated_cost="0.05"))
plan.add_step(PlanStep(step_id="s2", description="API call", provider="api.example", method="http.get", estimated_cost="0.01"))
test("total estimated is sum", plan.total_estimated() == "0.060000")
test("plan starts as draft", plan.status == PlanStatus.DRAFT)
# Commit
plan.commit(approved_by="human-1")
test("plan committed", plan.status == PlanStatus.COMMITTED)
test("plan has hash", len(plan.plan_hash()) == 64)
# Re-quote: within tolerance
ok = plan.requote_step("s1", "0.055")
test("re-quote within tolerance", ok)
# Re-quote: drift too large
plan2 = ExecutionPlan(plan_id="plan-2", total_ceiling="1.00", drift_tolerance_pct=0.10)
plan2.add_step(PlanStep(step_id="s1", estimated_cost="0.05"))
plan2.requote_step("s1", "0.20")  # 300% drift
s1 = [s for s in plan2.steps if s.step_id == "s1"][0]
test("re-quote outside tolerance fails step", s1.status == "failed")

# ─── 6. AgentLease ───
print("\n6. AgentLease")
from evidence.lease import AgentLeaseV1, LeasePermissions, compile_permission_language
lease = AgentLeaseV1(
    lease_id="lease-1",
    agent_id="agent-1",
    owner="0xowner",
    delegate="0xtee_signer",
    permissions=LeasePermissions(
        x402_max_total_usd="5.00",
        allowed_targets=["0x1234"],
        allowed_methods=["submit(...)"],
        valid_until=time.time() + 3600,
    ),
)
ld = lease.lease_digest()
test("lease digest is 64 chars", len(ld) == 64)
test("lease not expired", not lease.is_expired())
# Compile to ERC-7710
erc7710 = lease.compile_to_erc7710()
test("erc7710 has caveats", len(erc7710["caveats"]) >= 3)
test("erc7710 has delegate", erc7710["delegate"] == "0xtee_signer")
# Compile from permission language
perm = compile_permission_language({
    "agent": "842",
    "expires": "2026-09-05T00:00:00Z",
    "permissions": {
        "x402": {"max_total_usd": 5, "max_request_usd": 0.20},
        "contracts": {"allow": [{"target": "0xabc", "methods": ["submit(...)"]}]},
        "jobs": {"categories": ["research"]},
    },
    "require": {"tee_workload": "0xdef"},
})
test("permission language compiles", perm.agent_id == "842")
test("compiled has targets", "0xabc" in perm.permissions.allowed_targets)
test("compiled has categories", "research" in perm.permissions.allowed_job_categories)
test("compiled has TEE requirement", perm.permissions.required_tee_workload == "0xdef")

# ─── 7. KMS auth ───
print("\n7. KMS auth")
from evidence.kms import KMSAuthorizer, KMSAuthPolicy, KeyReleaseRequest
policy = KMSAuthPolicy(
    agent_id="agent-1",
    permitted_workloads=["wl-approved-1", "wl-approved-2"],
    permitted_compose_hashes=["compose-ok"],
)
kms = KMSAuthorizer(policy)
# Approved workload
req = KeyReleaseRequest(agent_id="agent-1", workload_id="wl-approved-1", compose_hash="compose-ok", key_domain="/moltwork/v1/agent/evm", attestation_hash="att123")
resp = kms.authorize(req)
test("approved workload → key released", resp.approved)
test("key has public key", len(resp.public_key) == 64)
test("key has signature chain", len(resp.signature_chain) == 2)
# Unapproved workload
req2 = KeyReleaseRequest(agent_id="agent-1", workload_id="wl-evil", compose_hash="compose-ok", key_domain="/moltwork/v1/agent/evm", attestation_hash="att123")
resp2 = kms.authorize(req2)
test("unapproved workload → denied", not resp2.approved)
test("denial has reason", "not in permitted list" in resp2.rejection_reason)
# Missing attestation
req3 = KeyReleaseRequest(agent_id="agent-1", workload_id="wl-approved-1", compose_hash="compose-ok", key_domain="/moltwork/v1/agent/evm", attestation_hash="")
resp3 = kms.authorize(req3)
test("missing attestation → denied", not resp3.approved)

# ─── 8. Evidence log + checkpoint ───
print("\n8. Evidence log")
from evidence.log import EvidenceLog
log = EvidenceLog()
idx0 = log.append("receipt-1-hash")
idx1 = log.append("receipt-2-hash")
idx2 = log.append("receipt-3-hash")
test("log root is 64 chars", len(log.root) == 64)
test("log count", log.count == 3)
# Inclusion proof
proof = log.get_proof(0)
test("inclusion proof for receipt 1", log.verify_inclusion("receipt-1-hash", proof, ) if False else log.verify_inclusion("receipt-1-hash", proof))
test("inclusion proof for receipt 2", log.verify_inclusion("receipt-2-hash", log.get_proof(1)))
test("inclusion proof for receipt 3", log.verify_inclusion("receipt-3-hash", log.get_proof(2)))
# Wrong hash fails
test("wrong hash fails proof", not log.verify_inclusion("wrong-hash", proof))
# Checkpoint
cp = log.checkpoint(ethereum_tx="0xtx123")
test("checkpoint has epoch", cp.epoch == 0)
test("checkpoint has root", cp.root == log.root)
test("checkpoint has receipt count", cp.receipt_count == 3)
# Second checkpoint
cp2 = log.checkpoint(ethereum_tx="0xtx456")
test("second checkpoint epoch", cp2.epoch == 1)
test("checkpoint has previous root", cp2.previous_root == cp.root)

# ─── 9. Chain adapters still work ───
print("\n9. Chain adapters")
from chain.erc8183 import JobAdapter, JobState
ja = JobAdapter()
job = ja.create_job(client="0xaaa", provider="0xbbb", amount="5.00")
ja.fund_job(job)
ja.submit_job(job, receipt_hash="abc", deliverable="output.md")
ja.complete_job(job)
test("ERC-8183 lifecycle", job.state == JobState.COMPLETED)

# ─── 10. Full integration: manifest → receipt → evidence log ───
print("\n10. Full integration")
from evidence.workload import WorkloadManifestV1
from evidence.receipt import RunReceiptV1
from evidence.trace import TraceEvent, TraceMerkleTree
from evidence.log import EvidenceLog
from evidence.lease import AgentLeaseV1, LeasePermissions
from evidence.kms import KMSAuthorizer, KMSAuthPolicy, KeyReleaseRequest
from tee.dstack import DstackSimulator
from tee.keys import TEESigner

# 1. Workload manifest
wm = WorkloadManifestV1(agent_id="agent-1", source_commit="abc123", workerkit_version="0.1.0", compose_hash="compose123")
wid = wm.workload_id()

# 2. KMS authorization
policy = KMSAuthPolicy(agent_id="agent-1", permitted_workloads=[wid])
kms = KMSAuthorizer(policy)
req = KeyReleaseRequest(agent_id="agent-1", workload_id=wid, compose_hash="compose123", key_domain="/moltwork/v1/receipts", attestation_hash="att123")
resp = kms.authorize(req)
test("KMS releases key for approved workload", resp.approved)

# 3. TEE signer
ds = DstackSimulator(app_id="moltwork-worker-001")
signer = TEESigner.from_dstack(ds)

# 4. Trace events
events = [
    TraceEvent(sequence=0, event_type="aci_inference", provider="tinfoil", cost="0.04"),
    TraceEvent(sequence=1, event_type="http", provider="api.example", cost="0.01"),
    TraceEvent(sequence=2, event_type="artifact", provider="local", cost="0"),
]
tree = TraceMerkleTree(events)

# 5. Run receipt
rr = RunReceiptV1(
    run_id="run-001",
    agent_id="agent-1",
    workload_id=wid,
    trace_root=tree.root,
    execution_cost="0.05",
    status="completed",
    tee_signer=signer.public_key,
)
rr.signature = signer.sign(bytes.fromhex(rr.receipt_digest()))

# 6. Evidence log
log = EvidenceLog()
idx = log.append(rr.receipt_digest())
proof = log.get_proof(idx)
test("receipt included in evidence log", log.verify_inclusion(rr.receipt_digest(), proof))
cp = log.checkpoint(ethereum_tx="0xanchored")

# 7. Save everything
with tempfile.TemporaryDirectory() as td:
    wm_path = f"{td}/workload.json"
    with open(wm_path, "w") as f:
        json.dump(wm.to_dict(), f, indent=2)
    rr.save(f"{td}/receipt")
    with open(f"{td}/evidence-log.json", "w") as f:
        json.dump({"root": log.root, "count": log.count, "checkpoint": cp.to_dict()}, f, indent=2)
    test("all artifacts saved", os.path.exists(wm_path) and os.path.exists(f"{td}/receipt/run-receipt.json"))

print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
if FAIL > 0:
    print("SOME TESTS FAILED")
    sys.exit(1)
else:
    print("ALL EVIDENCE PRIMITIVES TESTS PASS")
