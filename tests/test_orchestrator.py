"""Orchestrator integration test — proves the full pipeline works.

Flow: Opportunity → Campaign → WorkOrder → Run → Receipt → Lab → Harvest → Capabilities → Learning

Reports actual numbers, not boolean claims.
"""
import sys, os, tempfile, time, asyncio
sys.path.insert(0, '/root')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = FAIL = 0
def test(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS+=1; print(f"  ✓ {name}")
    else: FAIL+=1; print(f"  ✗ {name} — {detail}")

print("=== ORCHESTRATOR INTEGRATION TEST ===\n")

async def run_test():
    from orchestrator import Orchestrator, CampaignResult
    from opportunities.schema import Opportunity, OpportunityRoute
    from campaigns.schema import Campaign, WorkPlan, WorkUnit
    from verify.contracts import AcceptanceContract, Criterion

    with tempfile.TemporaryDirectory() as td:
        # ─── 1. Create Opportunity ──────────────────────────────────────
        print("1. Create Opportunity")
        opp = Opportunity(
            id="opp-test-001",
            source="test",
            kind="BOUNTY",
            domain="CODE",
            title="Build an API rate limiter",
            description="Implement a token bucket rate limiter in Python",
            reward_model="FIXED",
            reward_usd=50.0,
            routes=[
                OpportunityRoute(
                    route_id="route-1",
                    name="Standard",
                    reward_usd=50.0,
                    required_capabilities=["python", "api-design"],
                ),
            ],
            required_capabilities=["python", "api-design"],
        )
        test("opportunity created", opp.id == "opp-test-001")
        test("best_route has reward", opp.best_route().reward_usd == 50.0)
        test("estimated_ev computed", opp.estimated_ev(win_probability=0.5) == 25.0)

        # ─── 2. Create Campaign with WorkPlan ───────────────────────────
        print("\n2. Create Campaign")
        campaign = Campaign(
            campaign_id="camp-001",
            opportunity_id="opp-test-001",
            route_id="route-1",
            budget_usd=10.0,
            cost_cap_usd=5.0,
            work_plan=WorkPlan(
                plan_id="plan-001",
                strategy="implement-and-test",
                work_units=[
                    WorkUnit(
                        work_unit_id="wu-1",
                        title="Design API surface",
                        description="Design the rate limiter API: classes, methods, config",
                        required_capabilities=["python", "api-design"],
                        estimated_cost_usd=1.0,
                    ),
                    WorkUnit(
                        work_unit_id="wu-2",
                        title="Implement rate limiter",
                        description="Implement token bucket algorithm with threading",
                        required_capabilities=["python"],
                        estimated_cost_usd=2.0,
                    ),
                    WorkUnit(
                        work_unit_id="wu-3",
                        title="Write tests",
                        description="Unit tests + integration tests for rate limiter",
                        required_capabilities=["python", "testing"],
                        estimated_cost_usd=1.5,
                    ),
                ],
            ),
        )
        test("campaign created", campaign.campaign_id == "camp-001")
        test("3 work units", len(campaign.work_plan.work_units) == 3)
        test("can_continue", campaign.can_continue())

        # ─── 3. Run orchestrator ────────────────────────────────────────
        print("\n3. Run orchestrator (full pipeline)")
        orch = Orchestrator(data_dir=f"{td}/orch")

        result = await orch.run_campaign(opp, campaign)

        test("campaign completed", result.status == "COMPLETED")
        test("3 units executed", result.total_units == 3 or len(result.unit_results) == 3)
        test("all units succeeded", result.failed_units == 0)
        test("total cost tracked", result.total_cost > 0)
        test("duration recorded", result.duration_s > 0)
        print(f"    Status: {result.status}")
        print(f"    Units: {len(result.unit_results)}")
        print(f"    Cost: ${result.total_cost:.4f}")
        print(f"    Duration: {result.duration_s:.2f}s")

        # ─── 4. Verify receipts generated ───────────────────────────────
        print("\n4. Verify receipts")
        receipts = [u for u in result.unit_results if u.receipt_hash]
        test("receipts generated", len(receipts) == 3)
        for u in receipts:
            test(f"  receipt {u.work_unit_id} has hash", len(u.receipt_hash) == 64)
            test(f"  receipt {u.work_unit_id} gate passed", u.gate_decision == "ALLOW")

        # ─── 5. Verify lab projection synced ────────────────────────────
        print("\n5. Verify lab projection")
        projected = [u for u in result.unit_results if u.lab_projected]
        test("all runs projected to lab", len(projected) == 3)
        lab_runs = orch.projection.get_runs()
        test("lab has runs", len(lab_runs) >= 3)
        print(f"    Lab runs: {len(lab_runs)}")

        # ─── 6. Verify harvest candidates extracted ─────────────────────
        print("\n6. Verify harvest")
        candidates = orch.harvester.list_candidates()
        test("harvest candidates extracted", len(candidates) > 0)
        test("candidates have run_id", all(len(c.derived_from_runs) > 0 for c in candidates))
        print(f"    Candidates: {len(candidates)}")

        # ─── 7. Verify capabilities recorded ────────────────────────────
        print("\n7. Verify capabilities")
        caps = orch.capabilities.list_capabilities()
        test("capabilities recorded", len(caps) > 0)
        for cap in caps:
            test(f"  capability '{cap.name}' has evidence", cap.evidence_count > 0)
            test(f"  capability '{cap.name}' has quality", cap.quality_estimate > 0)
        print(f"    Capabilities: {len(caps)}")

        # ─── 8. Verify learning observations ────────────────────────────
        print("\n8. Verify learning")
        test("reflection has observations", orch.reflection._total_runs > 0)
        print(f"    Observations: {orch.reflection._total_runs}")

        # ─── 9. Verify event chain integrity ────────────────────────────
        print("\n9. Verify event chain integrity")
        for u in receipts:
            valid = orch.ledger.verify_chain(u.run_id)
            test(f"  chain valid for {u.work_unit_id}", valid)

        # ─── 10. Verify campaign state ──────────────────────────────────
        print("\n10. Verify campaign state")
        test("campaign status COMPLETED", campaign.status == "COMPLETED")
        test("campaign spent > 0", campaign.spent_usd > 0)
        test("campaign can_continue = False", not campaign.can_continue())
        print(f"    Spent: ${campaign.spent_usd:.4f}")

        # ─── Summary ────────────────────────────────────────────────────
        print(f"\n{'='*60}")
        print("ORCHESTRATOR INTEGRATION SUMMARY")
        print(f"{'='*60}")
        print(f"Opportunity:   {opp.title}")
        print(f"Route:         {opp.best_route().name} (${opp.best_route().reward_usd})")
        print(f"Campaign:      {campaign.campaign_id}")
        print(f"Status:        {result.status}")
        print(f"Units:         {result.completed_units} completed, {result.failed_units} failed")
        print(f"Cost:          ${result.total_cost:.4f}")
        print(f"Receipts:      {len(receipts)}")
        print(f"Lab runs:      {len(lab_runs)}")
        print(f"Candidates:    {len(candidates)}")
        print(f"Capabilities:  {len(caps)}")
        print(f"Learning:      {orch.reflection._total_runs} observations")
        print(f"Duration:      {result.duration_s:.2f}s")
        print(f"{'='*60}")

asyncio.run(run_test())

print(f"\n=== {PASS} passed, {FAIL} failed ===")
if FAIL: sys.exit(1)
else: print("ORCHESTRATOR INTEGRATION PASS — full pipeline verified")
