"""End-to-end test: full Moltwork lifecycle."""
import sys, os, json, tempfile, time, asyncio
sys.path.insert(0, '/root')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = 0
FAIL = 0

def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAIL += 1
        print(f"  ✗ {name} — {detail}")

print("═" * 70)
print("  MOLTWORK END-TO-END INTEGRATION TEST")
print("═" * 70)

async def run_e2e():
    global PASS, FAIL

    # ═══ PHASE 1: WORKERKIT CORE ═══
    print("\n▸ PHASE 1: WorkerKit execution")
    from workerkit.sdk import WorkerKit, WorkOrder
    from workerkit.verify.contracts import AcceptanceContract
    from workerkit.core.schema import sha256

    wk = WorkerKit()
    order = WorkOrder(objective="Research ETH price", reward_value="5.00", source="oracle", raw={"max_cost": "2.00"})
    run = wk.start(order)
    test("1.1 WorkOrder created", order.id.startswith("wk_"))
    test("1.2 Run started", run.run.id.startswith("wk_"))

    run.event("model.call", {"model": "mimo", "tokens": 2000})
    run.cost("llm", 0.08)
    run.event("tool.call", {"tool": "web-search"})
    run.cost("api", 0.02)

    artifact = run.artifact(name="report.md", content=b"ETH: $3842", media_type="text/markdown")
    test("1.3 Artifact registered", len(artifact.sha256) == 64)

    contract = AcceptanceContract(required_outputs=["report.md"], maximum_cost=2.0)
    vr = await wk.verify(run, contract, artifact)
    test("1.4 Verification PASS", vr.status == "PASS")

    cd = wk.gate(run, "SUBMIT", vr, budget_remaining=5.0)
    test("1.5 Gate ALLOW", cd.decision == "ALLOW")

    receipt = wk.close(run)
    test("1.6 Receipt root hash", len(receipt.root_hash) == 64)
    test("1.7 Receipt binds chain", ":" in receipt.events_hash)
    test("1.8 Run cost tracked", run.meter.total_cost > 0)

    # ═══ PHASE 2: TEE IDENTITY ═══
    print("\n▸ PHASE 2: TEE workload identity")
    from evidence.workload import WorkloadManifestV1
    from evidence.keys import AgentKeyBundle, KEY_DOMAIN_RECEIPTS
    from evidence.kms import KMSAuthorizer, KMSAuthPolicy, KeyReleaseRequest
    from tee.dstack import DstackSimulator
    from tee.keys import TEESigner

    manifest = WorkloadManifestV1(agent_id="agent-413", source_commit="abc123", image_digests=["sha256:wk-0.1"], workerkit_version="0.1.0", compose_hash="compose-123", capability_hash=sha256("research"))
    workload_id = manifest.workload_id()
    test("2.1 WorkloadManifest created", len(workload_id) == 64)

    policy = KMSAuthPolicy(agent_id="agent-413", permitted_workloads=[workload_id], permitted_compose_hashes=["compose-123"])
    kms = KMSAuthorizer(policy)
    req = KeyReleaseRequest(agent_id="agent-413", workload_id=workload_id, compose_hash="compose-123", key_domain=KEY_DOMAIN_RECEIPTS, attestation_hash="att-abc")
    resp = kms.authorize(req)
    test("2.2 KMS releases key", resp.approved)

    bad_req = KeyReleaseRequest(agent_id="agent-413", workload_id="evil", compose_hash="compose-123", key_domain=KEY_DOMAIN_RECEIPTS, attestation_hash="att-abc")
    test("2.3 KMS denies unapproved", not kms.authorize(bad_req).approved)

    ds = DstackSimulator(app_id="worker-413")
    signer = TEESigner.from_dstack(ds)
    test("2.4 TEE signer", len(signer.public_key) == 64)

    bundle = AgentKeyBundle.derive(agent_id="agent-413", workload_id=workload_id, key_fn=lambda d: (sha256(f"k:{d}"), ["att"]))
    test("2.5 Key bundle has 4 domains", len(bundle.keys) == 4)

    # ═══ PHASE 3: EVIDENCE LAYER ═══
    print("\n▸ PHASE 3: ACI + Trace + RunReceipt")
    from evidence.aci import ACIReceipt, HTTPEvidence, X402Settlement
    from evidence.trace import TraceEvent, TraceMerkleTree
    from evidence.receipt import RunReceiptV1

    aci1 = ACIReceipt(gateway_app_id="gw", provider="tinfoil", model="gpt-4", request_hash=sha256("r1"), response_hash=sha256("s1"), tokens_input=1500, tokens_output=800, cost_usd="0.04", provider_verification="VERIFIED", signature="sig1")
    test("3.1 ACI receipt", len(aci1.receipt_hash()) == 64)

    events = [
        TraceEvent(sequence=0, event_type="aci_inference", cost="0.04"),
        TraceEvent(sequence=1, event_type="http", cost="0.01"),
        TraceEvent(sequence=2, event_type="aci_inference", cost="0.02"),
        TraceEvent(sequence=3, event_type="x402_settlement", cost="0.01"),
        TraceEvent(sequence=4, event_type="artifact", cost="0"),
    ]
    trace_tree = TraceMerkleTree(events)
    test("3.2 Trace tree root", len(trace_tree.root) == 64)
    proof = trace_tree.get_proof(0)
    test("3.3 Inclusion proof", trace_tree.verify_proof(events[0].leaf_hash(), proof, trace_tree.root))

    rr = RunReceiptV1(run_id=run.run.id, agent_id="agent-413", workload_id=workload_id, trace_root=trace_tree.root, execution_cost="0.10", status="completed", tee_signer=signer.public_key)
    rr.signature = signer.sign(bytes.fromhex(rr.receipt_digest()))
    test("3.4 RunReceiptV1 digest", len(rr.receipt_digest()) == 64)
    test("3.5 Receipt has signature", rr.signature != "")
    test("3.6 Receipt binds trace root", rr.trace_root == trace_tree.root)

    with tempfile.TemporaryDirectory() as td:
        rr.save(f"{td}/receipt")
        test("3.7 Receipt saves", os.path.exists(f"{td}/receipt/run-receipt.json"))

    # ═══ PHASE 4: AGENT LEASE ═══
    print("\n▸ PHASE 4: Agent lease → ERC-7710")
    from evidence.lease import compile_permission_language

    lease = compile_permission_language({"agent": "413", "expires": "2026-09-05T00:00:00Z", "permissions": {"x402": {"max_total_usd": 5}, "contracts": {"allow": [{"target": "0xERC8183", "methods": ["submit(...)"]}]}}, "require": {"tee_workload": workload_id}})
    test("4.1 Lease compiled", lease.agent_id == "413")
    erc7710 = lease.compile_to_erc7710()
    test("4.2 ERC-7710 caveats", len(erc7710["caveats"]) >= 3)
    test("4.3 Lease digest", len(lease.lease_digest()) == 64)

    # ═══ PHASE 5: EXECUTION PLAN ═══
    print("\n▸ PHASE 5: Execution plan")
    from evidence.plan import ExecutionPlan, PlanStep, PlanStatus

    plan = ExecutionPlan(plan_id="p1", job_id="j1", agent_id="agent-413", total_ceiling="2.00")
    plan.add_step(PlanStep(step_id="s1", estimated_cost="0.04"))
    plan.add_step(PlanStep(step_id="s2", estimated_cost="0.01"))
    plan.add_step(PlanStep(step_id="s3", estimated_cost="0.02"))
    test("5.1 Plan estimated", plan.total_estimated() == "0.070000")
    plan.commit(approved_by="human")
    test("5.2 Plan committed", plan.status == PlanStatus.COMMITTED)
    test("5.3 Plan hash", len(plan.plan_hash()) == 64)
    plan.requote_step("s1", "0.045")
    test("5.4 Requote within tolerance", plan.steps[0].live_quote == "0.045")

    # ═══ PHASE 6: EVIDENCE LOG ═══
    print("\n▸ PHASE 6: Evidence log")
    from evidence.log import EvidenceLog

    log = EvidenceLog()
    idx = log.append(rr.receipt_digest())
    test("6.1 Receipt appended", idx == 0)
    proof = log.get_proof(idx)
    test("6.2 Inclusion proof", log.verify_inclusion(rr.receipt_digest(), proof))
    for i in range(5):
        log.append(sha256(f"r{i}"))
    test("6.3 Log has 6", log.count == 6)
    cp = log.checkpoint(ethereum_tx="0xabc")
    test("6.4 Checkpoint", cp.epoch == 0 and cp.receipt_count == 6)

    # ═══ PHASE 7: MARKET ═══
    print("\n▸ PHASE 7: Market primitives")
    from mwmarket.models import AssetVersion, Listing, AccessGrant, SampleReceipt, CapabilityLease, Board, DistributionGrant, SettlementPlan, Request
    from mwmarket.api import MarketAPI
    from mwmarket.models import sha256 as mw_sha256

    with tempfile.TemporaryDirectory() as td:
        api = MarketAPI(db_path=f"{td}/m.db")

        asset = AssetVersion(name="ETH Report", kind="ARTIFACT", owner_id="agent-413", originating_receipts=[rr.receipt_digest()], worker_manifest_digest=workload_id, merkle_root=trace_tree.root)
        api.register_asset(asset)
        test("7.1 Asset registered", api.get_asset(asset.id) is not None)

        listing = Listing(asset_id=asset.id, seller_id="agent-413", price_amount="5.00")
        api.publish_listing(listing)
        test("7.2 Listing published", api.get_listing(listing.id) is not None)

        grant = AccessGrant(principal="buyer-1", listing_id=listing.id, asset_id=asset.id, rights="SAMPLE", quotas={"calls_remaining": 3})
        api.issue_grant(grant)
        test("7.3 Grant issued", api.check_grant(grant.id))
        api.consume_grant(grant.id)
        test("7.4 Grant consumed", grant.quotas["calls_remaining"] == 2)

        sr = SampleReceipt(asset_id=asset.id, buyer_id="buyer-1", chunk_index=5, cumulative_units=10, total_units=40, amount_paid="1.00")
        api.issue_sample_receipt(sr)
        test("7.5 SampleReceipt issued", len(api.receipts) == 1)

        rq = Request(title="ETH analysis", creator_id="buyer-1", budget="5.00")
        api.create_request(rq)
        api.fund_request(rq.id)
        api.submit_request(rq.id, receipt_hash=rr.receipt_digest(), deliverable="report.md")
        api.complete_request(rq.id)
        test("7.6 Request lifecycle", api.requests[rq.id].status == "completed")

        cl = CapabilityLease(asset_id=asset.id, lessor_id="agent-413", lessee_id="renter-1", max_calls=10, valid_until=time.time()+3600)
        lid = api.issue_lease(cl)
        test("7.7 Lease issued", api.check_lease(lid))
        api.revoke_lease(lid)
        test("7.8 Lease revoked", not api.check_lease(lid))

        board = Board(owner_id="curator-1", name="Crypto Research")
        bid = api.create_board(board)
        dg = DistributionGrant(listing_id=listing.id, board_id=bid)
        api.place_on_board(dg)
        test("7.9 Board + grant", len(api.distribution_grants) == 1)

        sp = SettlementPlan(total_amount="5.00", allocations=[{"recipient": "agent-413", "amount": "4.70", "bps": 9400}, {"recipient": "curator-1", "amount": "0.15", "bps": 300}, {"recipient": "protocol", "amount": "0.15", "bps": 300}])
        api.settle(sp)
        test("7.10 Settlement created", len(api.settlements) == 1)

        s = api.stats()
        test("7.11 Stats complete", s["assets"] == 1 and s["listings"] == 1 and s["boards"] == 1)

asyncio.run(run_e2e())

print("\n" + "═" * 70)
print(f"  RESULTS: {PASS} passed, {FAIL} failed")
print("═" * 70)
if FAIL > 0:
    print("  SOME TESTS FAILED")
    sys.exit(1)
else:
    print("  ALL END-TO-END TESTS PASS")
    print("  Full lifecycle: WorkerKit → TEE → Evidence → Lease → Plan → Log → Market")
