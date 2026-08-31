"""Lab wiring test — proves run → Lab → profile works end to end.

This is the single-player killer feature test.
"""
import sys, os, tempfile, asyncio
sys.path.insert(0, '/root')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = FAIL = 0
def test(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS+=1; print(f"  ✓ {name}")
    else: FAIL+=1; print(f"  ✗ {name} — {detail}")

print("=== LAB WIRING TEST: run → Lab → profile ===\n")

async def run_test():
    from orchestrator import Orchestrator
    from opportunities.schema import Opportunity, OpportunityRoute
    from campaigns.schema import Campaign, WorkPlan, WorkUnit
    from verify.contracts import AcceptanceContract
    from lab.persistence import MoltworkLab

    with tempfile.TemporaryDirectory() as td:
        # ─── 1. Create orchestrator with worker_id ──────────────────────
        print("1. Create orchestrator")
        orch = Orchestrator(data_dir=f"{td}/orch", worker_id="support-17")
        test("orchestrator created", orch.worker_id == "support-17")
        test("lab attached", orch.lab.worker_id == "support-17")

        # ─── 2. Run 5 campaigns with different capabilities ─────────────
        print("\n2. Run 5 work units")
        opp = Opportunity(
            id="opp-lab-1", source="test", kind="BOUNTY", domain="CODE",
            title="Build feature", reward_usd=50.0,
            routes=[OpportunityRoute(route_id="r1", name="Standard", reward_usd=50.0)],
        )
        caps_list = [["coding"], ["api-implementation"], ["coding", "debugging"],
                     ["technical-writing"], ["coding", "api-implementation"]]
        for i, caps in enumerate(caps_list):
            campaign = Campaign(
                campaign_id=f"camp-{i}", opportunity_id="opp-lab-1",
                work_plan=WorkPlan(work_units=[
                    WorkUnit(work_unit_id=f"wu-{i}", title=f"Task {i}",
                             required_capabilities=caps, estimated_cost_usd=1.0),
                ]),
            )
            await orch.run_campaign(opp, campaign)

        test("5 runs completed", orch.lab.evidence.total_runs == 5)
        test("lab has run log", len(orch.lab._run_log) == 5)

        # ─── 3. Check capabilities computed ─────────────────────────────
        print("\n3. Check capabilities")
        caps = orch.lab.capabilities
        test("capabilities computed", len(caps) > 0)
        coding = next((c for c in caps if c["name"] == "coding"), None)
        test("coding capability exists", coding is not None)
        if coding:
            test("coding has runs", coding["runs"] >= 2)
            test("coding has quality", coding["quality"] > 0)
            test("coding has confidence", coding["confidence"] in ("LOW", "MEDIUM", "HIGH", "INSUFFICIENT"))
            print(f"    coding: quality={coding['quality']}, runs={coding['runs']}, confidence={coding['confidence']}")

        # ─── 4. Check economics computed ────────────────────────────────
        print("\n4. Check economics")
        test("spend tracked", orch.lab.economics.total_spend_usd > 0)
        test("revenue tracked", orch.lab.economics.total_revenue_usd > 0)
        test("avg cost computed", orch.lab.economics.avg_cost_per_run > 0)
        print(f"    spend: ${orch.lab.economics.total_spend_usd:.2f}")
        print(f"    revenue: ${orch.lab.economics.total_revenue_usd:.2f}")
        print(f"    avg cost: ${orch.lab.economics.avg_cost_per_run:.2f}")

        # ─── 5. Check process versions tracked ──────────────────────────
        print("\n5. Check process versions")
        test("process versions tracked", len(orch.lab.version.process_versions) > 0)
        for p in orch.lab.version.process_versions:
            print(f"    {p['task_family']} v{p['version']} ({p['run_count']} runs)")

        # ─── 6. Check valuation computed ────────────────────────────────
        print("\n6. Check valuation")
        v = orch.lab.compute_valuation()
        test("valuation computed", v is not None)
        test("trailing revenue set", v.trailing_12m_revenue > 0)
        test("capability breadth set", v.capability_breadth > 0)
        test("process defensibility set", v.process_defensibility > 0)
        print(f"    revenue: ${v.trailing_12m_revenue:.2f}")
        print(f"    breadth: {v.capability_breadth:.2f}")
        print(f"    defensibility: {v.process_defensibility:.2f}")

        # ─── 7. Get profile (the killer feature) ────────────────────────
        print("\n7. Worker profile")
        profile = orch.get_lab_profile()
        test("profile generated", len(profile) > 0)
        test("profile has worker_id", "support-17" in profile)
        test("profile has capabilities", "Capabilities:" in profile)
        test("profile has valuation", "Valuation:" in profile)
        test("profile has economics", "spend" in profile)
        print()
        for line in profile.split("\n"):
            print(f"    {line}")

        # ─── 8. Save/load round-trip ────────────────────────────────────
        print("\n8. Save/load")
        orch.lab.save()
        lab2 = MoltworkLab(data_dir=f"{td}/orch/lab")
        lab2.load("support-17")
        test("load preserves runs", lab2.evidence.total_runs == 5)
        test("load preserves capabilities", len(lab2.capabilities) == len(caps))
        test("load preserves run_log", len(lab2._run_log) == 5)

        # ─── 9. Get machine-readable summary ────────────────────────────
        print("\n9. Summary")
        s = orch.get_lab_summary()
        test("summary has worker_id", s["worker_id"] == "support-17")
        test("summary has capabilities", len(s["capabilities"]) > 0)
        test("summary has valuation", "valuation" in s)
        test("summary has run_count", s["run_count"] == 5)

        print(f"\n{'='*60}")
        print("LAB WIRING SUMMARY")
        print(f"{'='*60}")
        print(f"Worker: support-17")
        print(f"Runs: {orch.lab.evidence.total_runs}")
        print(f"Spend: ${orch.lab.economics.total_spend_usd:.2f}")
        print(f"Revenue: ${orch.lab.economics.total_revenue_usd:.2f}")
        print(f"Capabilities: {len(orch.lab.capabilities)}")
        print(f"Processes: {len(orch.lab.version.process_versions)}")
        print(f"{'='*60}")

asyncio.run(run_test())

print(f"\n=== {PASS} passed, {FAIL} failed ===")
if FAIL: sys.exit(1)
else: print("LAB WIRING PASS — run → Lab → profile verified")
