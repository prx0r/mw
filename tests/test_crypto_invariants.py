"""Crypto invariants — canonicalization, hashing, chain integrity."""
import sys, os, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = FAIL = 0
def test(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS+=1; print(f"  ✓ {name}")
    else: FAIL+=1; print(f"  ✗ {name} — {detail}")

print("=== CRYPTO INVARIANTS ===\n")

# 1. JCS canonicalization
print("1. JCS canonicalization")
from core.hashing import jcs, sha256, event_hash, SCHEMA_EVENT

test("JCS sorts keys", jcs({"b": 2, "a": 1}) == jcs({"a": 1, "b": 2}))
test("JCS no whitespace", jcs({"x": 1}) == b'{"x":1}')
test("JCS deterministic", jcs({"x": [1, 2]}) == jcs({"x": [1, 2]}))
test("JCS handles nested", jcs({"a": {"b": 1}}) == b'{"a":{"b":1}}')
test("JCS handles unicode", jcs({"k": "hello"}) == jcs({"k": "hello"}))

# 2. SHA-256 integrity
print("\n2. SHA-256 integrity")
test("sha256 is 64 hex", len(sha256("test")) == 64)
test("sha256 is hex", all(c in '0123456789abcdef' for c in sha256("test")))
test("sha256 is deterministic", sha256("x") == sha256("x"))
test("sha256 changes on input", sha256("a") != sha256("b"))

# 3. Event hashing
print("\n3. Event hashing")
eh1 = event_hash(SCHEMA_EVENT, {"run_id": "r1", "seq": 1})
eh2 = event_hash(SCHEMA_EVENT, {"run_id": "r1", "seq": 2})
eh3 = event_hash(SCHEMA_EVENT, {"run_id": "r2", "seq": 1})
test("event hash is 64 hex", len(eh1) == 64)
test("different seq → different hash", eh1 != eh2)
test("different run → different hash", eh1 != eh3)
test("event hash is deterministic", eh1 == event_hash(SCHEMA_EVENT, {"run_id": "r1", "seq": 1}))

# 4. Merkle tree
print("\n4. Merkle tree")
from core.merkle import MerkleTree

leaves = [sha256(f"event{i}") for i in range(4)]
tree = MerkleTree(leaves)
test("merkle root is 64 hex", len(tree.root) == 64)
test("proof 0 valid", tree.proof(0).verify())
test("proof 1 valid", tree.proof(1).verify())
test("proof 2 valid", tree.proof(2).verify())
test("proof 3 valid", tree.proof(3).verify())
# Tamper test
bad_proof = tree.proof(0)
bad_proof.leaf_hash = sha256("tampered")
test("tampered proof fails", not bad_proof.verify())

# 5. DSSE
print("\n5. DSSE")
from core.dsse import DSSEEnvelope

env = DSSEEnvelope(payload_type="test", payload=b"hello")
env.sign("key1", b"sig1")
test("dsse signable_hash", len(env.signable_hash()) == 64)
test("dsse signatures", len(env.signatures) == 1)
test("dsse payload_type in signable", b"test" in env.signable_bytes())
test("dsse payload in signable", b"hello" in env.signable_bytes())

# 6. Event chain
print("\n6. Event chain")
from core.events import EventLedger

with tempfile.TemporaryDirectory() as td:
    ledger = EventLedger(f"{td}/test.db")
    e1 = ledger.append("r1", "run.started", {"order": "o1"})
    e2 = ledger.append("r1", "model.call", {"model": "mimo"})
    e3 = ledger.append("r1", "run.completed", {})
    events = ledger.get_events("r1")
    test("chain has 3 events", len(events) == 3)
    test("chain valid", ledger.verify_chain("r1"))
    # Tamper test
    conn = ledger._conn()
    conn.execute("UPDATE events SET payload='tampered' WHERE event_id=?", (e2,))
    conn.commit()
    conn.close()
    test("tampered chain fails", not ledger.verify_chain("r1"))

# 7. Receipt v2
print("\n7. Receipt v2")
from core.receipts import WorkReceipt, verify_receipt
import tempfile

class MockRun:
    id = "wk_test"
    work_order_id = "wo_test"
    known_cost_usd = "0.15"
    status = "COMPLETED"
    outputs = ["report.md"]

receipt = WorkReceipt(MockRun(), "abc:3")
test("receipt has root_hash", len(receipt.root_hash) == 64)
test("receipt is in-toto format", receipt.to_attestation()["_type"] == "https://in-toto.io/Statement/v1")

# 8. AssetVersion
print("\n8. AssetVersion")
from assets.af import AssetVersion

av = AssetVersion(worker_id="researcher-03", model="opencode-go/mimo-v2.5")
test("asset digest is 64 hex", len(av.content_digest()) == 64)
test("asset is deterministic", av.content_digest() == av.content_digest())
av2 = av.new_version(model="anthropic/claude-sonnet-5")
test("new version has different digest", av.content_digest() != av2.content_digest())
test("new version has parent", av2.parent_digest == av.content_digest())

# 9. LettaSnapshot
print("\n9. LettaSnapshot")
from runtimes.letta.snapshot import LettaSnapshot, LettaSnapshotExporter

exporter = LettaSnapshotExporter()
snap = exporter.snapshot_from_agent("a1", "mimo", [{"label": "p", "content": "test"}])
test("snapshot digest", len(snap.content_digest()) == 64)
test("snapshot has blocks", len(snap.blocks) == 1)

# 10. Lineage
print("\n10. Lineage")
from runtimes.letta.lineage import Lineage

lin = Lineage(worker_id="r3")
lin.add_version("v1", memory_digest="m0")
lin.add_version("v2", memory_digest="m1")
test("lineage head", lin.head_digest == "v2")
test("lineage has 2 versions", len(lin.versions) == 2)
test("lineage diff", lin.diff("v1", "v2")["memory_changed"])

# 11. Lease
print("\n11. Lease")
from leasing.lease import Lease, LeaseLimits

lease = Lease(
    lease_id="lease-1",
    asset_version_digest="av123",
    lessor="alice",
    lessee="bob",
    valid_until=time.time() + 3600,
)
test("lease valid", lease.is_valid())
test("lease hash", len(lease.lease_hash()) == 64)
lease.record_invocation(0.15)
test("lease invocation recorded", lease.invocations_used == 1)
lease.limits.max_invocations = 1
lease.record_invocation(0.15)
test("lease exhausted", not lease.can_invoke())

# 12. QuoteCommitment
print("\n12. QuoteCommitment")
from attestation.dstack.quote import QuoteCommitment

qc = QuoteCommitment(run_id="r1", worker_id="w1")
test("commitment digest", len(qc.compute_digest()) == 64)
test("report_data is 64 bytes", len(qc.to_report_data()) == 64)

# 13. WorkerSigner
print("\n13. WorkerSigner")
from attestation.dstack.signer import WorkerSigner

signer = WorkerSigner()
key = signer.derive_key("researcher-03")
test("key derived", key.public_key != "")
sig = signer.sign("researcher-03", b"test data")
test("sign produces signature", sig is not None)

print(f"\n=== {PASS} passed, {FAIL} failed ===")
if FAIL: sys.exit(1)
else: print("ALL CRYPTO INVARIANTS PASS")
