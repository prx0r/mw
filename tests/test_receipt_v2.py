"""Receipt v2 tests — in-toto + DSSE + full lifecycle."""
import sys, os, tempfile, time, json, shutil
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = FAIL = 0
def test(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS+=1; print(f"  ✓ {name}")
    else: FAIL+=1; print(f"  ✗ {name} — {detail}")

print("=== RECEIPT V2 TESTS ===\n")

# 1. WorkReceipt v2 format
print("1. WorkReceipt v2 format")
from core.hashing import sha256
from core.receipts import WorkReceipt, verify_receipt

class MockRun:
    id = "wk_test_001"
    work_order_id = "wo_test_001"
    known_cost_usd = "0.15"
    status = "COMPLETED"
    outputs = ["report.md"]

receipt = WorkReceipt(MockRun(), "abc:3")
test("receipt is in-toto", receipt.to_attestation()["_type"] == "https://in-toto.io/Statement/v1")
test("receipt has subject", len(receipt.to_attestation()["subject"]) == 1)
test("receipt has predicateType", "worker-run" in receipt.to_attestation()["predicateType"])
test("receipt has root_hash", len(receipt.root_hash) == 64)

# 2. Receipt persistence
print("\n2. Receipt persistence")
with tempfile.TemporaryDirectory() as td:
    receipt.save(Path(f"{td}/receipt"))
    test("receipt saved", Path(f"{td}/receipt/receipt.json").exists())
    test("root_hash saved", Path(f"{td}/receipt/root_hash.txt").exists())

# 3. DSSE envelope
print("\n3. DSSE envelope")
from core.dsse import DSSEEnvelope

env = DSSEEnvelope(
    payload_type="application/vnd.in-toto+json",
    payload=json.dumps(receipt.to_attestation()).encode(),
)
env.sign("worker-key-1", b"mock-signature")
test("dsse has payload", len(env.payload) > 0)
test("dsse has signature", len(env.signatures) == 1)
test("dsse signable_hash is 64 hex", len(env.signable_hash()) == 64)
test("dsse round-trip", DSSEEnvelope.from_dict(env.to_dict()).payload == env.payload)

# 4. Merkle tree for selective disclosure
print("\n4. Merkle selective disclosure")
from core.merkle import MerkleTree

events = [
    {"type": "run.started", "data": "start"},
    {"type": "model.call", "data": "mimo"},
    {"type": "cost.recorded", "data": "0.15"},
    {"type": "verification.completed", "data": "PASS"},
    {"type": "run.completed", "data": "done"},
]
leaves = [sha256(json.dumps(e, sort_keys=True)) for e in events]
tree = MerkleTree(leaves)
test("merkle root", len(tree.root) == 64)
# Prove verification event belongs to receipt
proof = tree.proof(3)
test("verification proof valid", proof.verify())
test("verification in correct position", proof.leaf_index == 3)

# 5. AssetVersion
print("\n5. AssetVersion content addressing")
from assets.af import AssetVersion

av = AssetVersion(
    worker_id="researcher-03",
    model="opencode-go/mimo-v2.5",
    memory_digest=sha256("memory-v1"),
    skills_digest=sha256("skills-v1"),
)
digest1 = av.content_digest()
test("asset digest deterministic", av.content_digest() == digest1)
av2 = av.new_version(memory_digest=sha256("memory-v2"))
test("new version different", av2.content_digest() != digest1)
test("new version has parent", av2.parent_digest == digest1)

# 6. LettaSnapshot
print("\n6. LettaSnapshot")
from runtimes.letta.snapshot import LettaSnapshot, LettaSnapshotExporter

exporter = LettaSnapshotExporter()
snap = exporter.snapshot_from_agent(
    agent_id="agent-001",
    model="opencode-go/mimo-v2.5",
    blocks=[
        {"label": "persona", "content": "research worker"},
        {"label": "strategy", "content": "requirements matrix"},
    ],
    memfs_commit="abc123",
)
test("snapshot has 2 blocks", len(snap.blocks) == 2)
test("snapshot digest", len(snap.content_digest()) == 64)

# 7. Lineage
print("\n7. Lineage tracking")
from runtimes.letta.lineage import LineageTracker

shutil.rmtree('/tmp/test-receipt-lineage', ignore_errors=True)
tracker = LineageTracker(data_dir="/tmp/test-receipt-lineage")
tracker.record_version("researcher-03", "v1", memory_digest="m0")
tracker.record_version("researcher-03", "v2", memory_digest="m1")
tracker.record_version("researcher-03", "v3", memory_digest="m2")
summary = tracker.summary("researcher-03")
test("lineage has 3 versions", summary["total_versions"] == 3)
test("lineage head is v3", summary["head"] == "v3")

# 8. Lease
print("\n8. Lease lifecycle")
from leasing.lease import Lease

lease = Lease(
    lease_id="lease-test",
    asset_version_digest=av.content_digest(),
    lessor="alice",
    lessee="bob",
    valid_until=time.time() + 3600,
)
test("lease valid", lease.is_valid())
lease.record_invocation(0.15)
test("lease invocation 1", lease.invocations_used == 1)
lease.record_invocation(0.20)
test("lease invocation 2", lease.invocations_used == 2)
lease.limits.max_invocations = 2
test("lease exhausted", not lease.can_invoke())

# 9. QuoteCommitment
print("\n9. QuoteCommitment")
from attestation.dstack.quote import QuoteCommitment

qc = QuoteCommitment(
    run_id="wk_001",
    worker_id="researcher-03",
    worker_version_digest=av.content_digest(),
    event_chain_head="abc",
    artifact_root="def",
    memory_before_digest="m0",
    memory_after_digest="m1",
)
test("commitment digest", len(qc.compute_digest()) == 64)
test("report_data 64 bytes", len(qc.to_report_data()) == 64)
test("report_data varies with challenge", qc.to_report_data("aa" * 32) != qc.to_report_data("bb" * 32))

# 10. x402
print("\n11. x402 payment")
from protocols.x402.provider import X402Provider

x402 = X402Provider()
req = x402.quote("1.00", "USDC", "base", "0x1234")
test("quote created", req.amount == "1.00")
from protocols.x402.provider import PaymentPayload
payload = PaymentPayload(tx_hash="0xabc", from_address="0x5678", amount="1.00", currency="USDC", network="base")
receipt = x402.record_payment("inv-1", req, payload)
test("payment verified", receipt.verified)

# 12. ERC-8004
print("\n12. ERC-8004 identity")
from protocols.erc8004.identity import ERC8004Identity

erc = ERC8004Identity()
reg = erc.register("researcher-03", "Frontend Worker 17", "Moltwork worker")
test("registration created", reg.name == "Frontend Worker 17")
test("well-known", erc.to_well_known("researcher-03") is not None)

# 13. Full lifecycle
print("\n13. Full lifecycle")
# .af → snapshot → lineage → run → receipt → DSSE → outcome
from runtimes.letta.lineage import Lineage
lin = Lineage(worker_id="r3")
lin.add_version(av.content_digest(), memory_digest="m0")
# Run produces receipt
# Receipt gets DSSE-signed
# Lineage records new version
av3 = av2.new_version(memory_digest=sha256("memory-v3"))
lin.add_version(av3.content_digest(), memory_digest="m1")
test("full lifecycle", lin.head_digest == av3.content_digest())

print(f"\n=== {PASS} passed, {FAIL} failed ===")
if FAIL: sys.exit(1)
else: print("ALL RECEIPT V2 TESTS PASS")
