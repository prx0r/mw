"""Protocol layer tests — receipt invariants, TEE invariants, delegation invariants."""
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

print("=== CRYPTOGRAPHIC PROTOCOL TESTS ===\n")

# ─── 1. Canonical hashing ───
print("1. Canonical hashing")
from protocol.canonical import sha256, keccak256, canonical_json, artifacts_root
h = sha256("test")
test("sha256 is 64 chars", len(h) == 64)
k = keccak256("test")
test("keccak256 is 64 chars", len(k) == 64)
test("sha256 != keccak256", h != k)
cj = canonical_json({"b": 2, "a": 1})
test("canonical json sorted", cj.index("a") < cj.index("b"))
ar = artifacts_root([{"sha256": "abc"}, {"sha256": "def"}])
test("artifacts_root is 64 chars", len(ar) == 64)

# ─── 2. Run commitment ───
print("\n2. Run commitment")
from protocol.commitments import RunCommitment
rc = RunCommitment(run_id="run-1", work_order_id="wo-1", event_chain_head="abc123", event_count=5)
d = rc.digest()
test("commitment digest is 64 chars", len(d) == 64)
rc2 = RunCommitment(run_id="run-1", work_order_id="wo-1", event_chain_head="abc123", event_count=5)
test("same inputs → same digest", rc.digest() == rc2.digest())
rc3 = RunCommitment(run_id="run-2", work_order_id="wo-1", event_chain_head="abc123", event_count=5)
test("different inputs → different digest", rc.digest() != rc3.digest())

# ─── 3. Receipt commitment report_data ───
print("\n3. Receipt commitment")
from protocol.commitments import ReceiptCommitment
rcc = ReceiptCommitment(receipt_digest="a" * 64, challenge_hash="b" * 64)
rd = rcc.report_data()
test("report_data is 64 bytes", len(rd) == 64)

# ─── 4. AttestedWorkReceiptV1 ───
print("\n4. AttestedWorkReceiptV1")
from protocol.attested_receipt import AttestedWorkReceiptV1, AgentIdentity, TEEInfo
att = AttestedWorkReceiptV1()
att.run_id = "run-1"
att.work_order_id = "wo-1"
att.event_chain_head = "abc123"
att.event_count = 5
att.agent = AgentIdentity(agent_id="agent-1")
att.tee = TEEInfo(app_id="moltwork-worker-001", signing_public_key="pub123")
att.artifacts = [{"sha256": "abc", "mediaType": "text/markdown"}]
d1 = att.compute_receipt_digest()
test("receipt digest is 64 chars", len(d1) == 64)
# Same inputs → same digest (set created_at to same value)
att2 = AttestedWorkReceiptV1()
att2.run_id = "run-1"
att2.work_order_id = "wo-1"
att2.event_chain_head = "abc123"
att2.event_count = 5
att2.agent = AgentIdentity(agent_id="agent-1")
att2.tee = TEEInfo(app_id="moltwork-worker-001", signing_public_key="pub123")
att2.artifacts = [{"sha256": "abc", "mediaType": "text/markdown"}]
att2.created_at = att.created_at
test("same inputs → same receipt digest", d1 == att2.compute_receipt_digest())
# Different artifact → different digest
att3 = AttestedWorkReceiptV1()
att3.run_id = "run-1"
att3.work_order_id = "wo-1"
att3.event_chain_head = "abc123"
att3.event_count = 5
att3.agent = AgentIdentity(agent_id="agent-1")
att3.tee = TEEInfo(app_id="moltwork-worker-001", signing_public_key="pub123")
att3.artifacts = [{"sha256": "DEF", "mediaType": "text/markdown"}]
att3.created_at = att.created_at
test("different artifact → different digest", d1 != att3.compute_receipt_digest())

# ─── 5. Execution policy ───
print("\n5. Execution policy")
from protocol.policy import ExecutionPolicy
p = ExecutionPolicy(
    allowed_tools=["web-search", "code-exec"],
    forbidden_tools=["file-delete"],
    allowed_targets=["0x1234"],
    allowed_methods=["submit(...)"],
    max_spend_usd="5.00",
    max_calls=100,
)
pd = p.digest()
test("policy digest is 64 chars", len(pd) == 64)
p2 = ExecutionPolicy(
    allowed_tools=["web-search", "code-exec"],
    forbidden_tools=["file-delete"],
    allowed_targets=["0x1234"],
    allowed_methods=["submit(...)"],
    max_spend_usd="5.00",
    max_calls=100,
)
test("same policy → same digest", pd == p2.digest())
p3 = ExecutionPolicy(allowed_tools=["different"], max_spend_usd="10.00")
test("different policy → different digest", pd != p3.digest())

# ─── 6. Evidence tiers ───
print("\n6. Evidence tiers")
from protocol.evidence import EvidenceTier
test("SELF_REPORTED < TEE_VERIFIED", EvidenceTier.SELF_REPORTED < EvidenceTier.TEE_VERIFIED)
test("OBSERVED < PAYMENT_VERIFIED", EvidenceTier.OBSERVED < EvidenceTier.PAYMENT_VERIFIED)
test("TEE_VERIFIED < REEXECUTED", EvidenceTier.TEE_VERIFIED < EvidenceTier.REEXECUTED)

# ─── 7. dstack simulator ───
print("\n7. dstack simulator")
from tee.dstack import DstackSimulator
ds = DstackSimulator(app_id="test-worker")
info = ds.info()
test("sim has app_id", info.app_id == "test-worker")
test("sim has compose_hash", len(info.compose_hash) == 64)
key = ds.get_key("/moltwork/agents/test/receipt-signing")
test("key has public_key", len(key.public_key) == 64)
test("key algorithm is secp256k1", key.algorithm == "secp256k1")
# Same path → same key (deterministic)
key2 = ds.get_key("/moltwork/agents/test/receipt-signing")
test("same path → same key", key.public_key == key2.public_key)
# Different path → different key
key3 = ds.get_key("/moltwork/agents/test/other")
test("different path → different key", key.public_key != key3.public_key)

# ─── 8. TEE attestation ───
print("\n8. TEE attestation")
from tee.dstack import DstackSimulator
ds = DstackSimulator(app_id="test-worker")
att = ds.attest(receipt_digest="a" * 64, challenge="b" * 64)
test("attestation has info", att.info.app_id == "test-worker")
test("attestation has signing key", len(att.signing_key.public_key) == 64)
test("attestation has receipt_digest", att.receipt_digest == "a" * 64)
# Fresh challenge → different attestation
att2 = ds.attest(receipt_digest="a" * 64, challenge="c" * 64)
test("different challenge → different quote", att.quote.quote != att2.quote.quote)

# ─── 9. TEE signer ───
print("\n9. TEE signer")
from tee.keys import TEESigner
from tee.dstack import DstackSimulator
ds = DstackSimulator(app_id="test-worker")
signer = TEESigner.from_dstack(ds)
test("signer has public_key", len(signer.public_key) == 64)
test("signer has address", signer.address.startswith("0x"))
sig = signer.sign(b"hello")
test("signature is 64 chars", len(sig) == 64)
# Same message → same signature
sig2 = signer.sign(b"hello")
test("deterministic signature", sig == sig2)
# Different message → different signature
sig3 = signer.sign(b"world")
test("different message → different sig", sig != sig3)

# ─── 10. TEE verifier ───
print("\n10. TEE verifier")
from tee.verifier import TEEVerifier
from protocol.attested_receipt import AttestedWorkReceiptV1, TEEInfo
v = TEEVerifier()
att = AttestedWorkReceiptV1()
att.run_id = "run-1"
att.work_order_id = "wo-1"
att.event_chain_head = "abc123"
att.event_count = 5
att.tee = TEEInfo(app_id="test-worker", signing_public_key="pub123")
att.artifacts = [{"sha256": "abc", "mediaType": "text/markdown"}]
att.signature = "sig123"
att.receipt_digest = att.compute_receipt_digest()
result = v.verify(att)
test("valid receipt → passes", result.valid)
test("tier is TEE_VERIFIED", result.tier == "E3_TEE_VERIFIED")
# Tamper with receipt
att.artifacts = [{"sha256": "TAMPERED", "mediaType": "text/markdown"}]
result2 = v.verify(att)
test("tampered receipt → fails", not result2.valid)
test("tampered tier is SELF_REPORTED", result2.tier == "E0_SELF_REPORTED")

# ─── 11. Chain adapters ───
print("\n11. Chain adapters")
from chain.erc8004 import IdentityAdapter, ValidationAdapter
from chain.erc8183 import JobAdapter, JobState
from chain.delegation import DelegationAdapter
from protocol.policy import ExecutionPolicy

ia = IdentityAdapter()
meta = ia.registration_metadata("agent-1", "Moltwork Worker 001", "abc123")
test("identity has name", meta["name"] == "Moltwork Worker 001")
test("identity has TEE trust", "tee-attestation" in meta["supportedTrust"])

va = ValidationAdapter()
vr = va.validation_request("agent-1", "receipt123")
test("validation has receipt hash", vr["requestHash"] == "receipt123")

ja = JobAdapter()
job = ja.create_job(client="0xaaa", provider="0xbbb", amount="5.00")
test("job starts Open", job.state == JobState.OPEN)
job = ja.fund_job(job)
test("job funded", job.state == JobState.FUNDED)
job = ja.submit_job(job, receipt_hash="abc", deliverable="output.md")
test("job submitted", job.state == JobState.SUBMITTED)
job = ja.complete_job(job)
test("job completed", job.state == JobState.COMPLETED)

da = DelegationAdapter()
policy = ExecutionPolicy(allowed_targets=["0x1234"], allowed_methods=["submit(...)"], max_spend_usd="5.00")
delegation = da.build_delegation(policy, delegate="0xtee_signer")
test("delegation has caveats", len(delegation["caveats"]) >= 2)
test("delegation has policy digest", len(delegation["policyDigest"]) == 64)

# ─── 12. Full chain: WorkerKit → AttestedReceipt → Verify ───
print("\n12. Full chain integration")
from protocol.attested_receipt import AttestedWorkReceiptV1, AgentIdentity, TEEInfo, JobRef
from tee.dstack import DstackSimulator
from tee.keys import TEESigner
from tee.verifier import TEEVerifier

# Simulate a full run
ds = DstackSimulator(app_id="moltwork-worker-001")
signer = TEESigner.from_dstack(ds)
policy = ExecutionPolicy(allowed_tools=["web-search"], max_spend_usd="2.00")

# Build receipt
att = AttestedWorkReceiptV1()
att.run_id = "run-001"
att.work_order_id = "wo-001"
att.event_chain_head = "abc123def456"
att.event_count = 10
att.known_cost = "0.83"
att.agent = AgentIdentity(agent_id="agent-001")
att.tee = TEEInfo(
    app_id=ds.app_id,
    compose_hash=ds.compose_hash,
    instance_id=ds.instance_id,
    signing_public_key=signer.public_key,
)
att.artifacts = [{"sha256": "artifact123", "mediaType": "text/markdown"}]
att.policy_digest = policy.digest()
att.receipt_digest = att.compute_receipt_digest()
att.signature = signer.sign(bytes.fromhex(att.receipt_digest))

# Verify
v = TEEVerifier()
result = v.verify(att, expected_compose_hash=ds.compose_hash, expected_policy_digest=policy.digest())
test("full chain → TEE_VERIFIED", result.valid)
test("all checks passed", all(c.passed for c in result.checks))

# Save receipt
with tempfile.TemporaryDirectory() as td:
    att.save(td)
    test("receipt saved", os.path.exists(f"{td}/attested-receipt.json"))
    with open(f"{td}/attested-receipt.json") as f:
        loaded = json.load(f)
    test("receipt round-trips", loaded["run"]["runId"] == "run-001")
    test("receipt has signature", loaded["signature"] != "")

print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
if FAIL > 0:
    print("SOME TESTS FAILED")
    sys.exit(1)
else:
    print("ALL CRYPTOGRAPHIC PROTOCOL TESTS PASS")
