"""Full flow test — proves: run → EventLedger → Lab rebuild → profile.

No stubs. Real events. Real rebuild. Real profile.
"""
import sys, os, tempfile, asyncio
sys.path.insert(0, '/root')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = FAIL = 0
def test(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS+=1; print(f"  ✓ {name}")
    else: FAIL+=1; print(f"  ✗ {name} — {detail}")

print("=== FULL FLOW TEST: run → ledger → rebuild → profile ===\n")

async def run_test():
    from orchestrator import Orchestrator
    from opportunities.schema import Opportunity, OpportunityRoute
    from campaigns.schema import Campaign, WorkPlan, WorkUnit
    from lab.persistence import MoltworkLab
    from core.events import EventLedger

    with tempfile.TemporaryDirectory() as td:
        # ─── 1. Run 5 campaigns through the orchestrator ────────────────
        print("1. Run 5 campaigns")
        orch = Orchestrator(data_dir=f"{td}/orch", worker_id="support-17")
        opp = Opportunity(
            id="opp-flow", source="test", kind="BOUNTY", domain="CODE",
            title="Build features", reward_usd=50.0,
            routes=[OpportunityRoute(route_id="r1", name="Standard", reward_usd=50.0)],
        )
        caps_list = [["coding"], ["api-implementation"], ["coding", "debugging"],
                     ["technical-writing"], ["coding", "api-implementation"]]
        for i, caps in enumerate(caps_list):
            campaign = Campaign(
                campaign_id=f"camp-{i}", opportunity_id="opp-flow",
                work_plan=WorkPlan(work_units=[
                    WorkUnit(work_unit_id=f"wu-{i}", title=f"Task {i}",
                             required_capabilities=caps, estimated_cost_usd=1.0),
                ]),
            )
            await orch.run_campaign(opp, campaign)

        test("5 campaigns ran", orch.lab.evidence.total_runs == 5)

        # ─── 2. Verify events exist in ledger ───────────────────────────
        print("\n2. Check ledger")
        ledger = orch.ledger
        event_count = ledger.count()
        test("events in ledger", event_count > 0)
        print(f"    {event_count} events across {len(ledger._conn().execute('SELECT DISTINCT run_id FROM events').fetchall())} runs")

        # ─── 3. Verify chain integrity ──────────────────────────────────
        print("\n3. Verify event chains")
        conn = ledger._conn()
        run_ids = [r[0] for r in conn.execute("SELECT DISTINCT run_id FROM events").fetchall()]
        conn.close()
        chains_valid = all(ledger.verify_chain(rid) for rid in run_ids)
        test("all event chains valid", chains_valid)
        print(f"    {len(run_ids)} chains verified")

        # ─── 4. Create a fresh Lab and rebuild from ledger ──────────────
        print("\n4. Rebuild Lab from ledger (fresh, no prior state)")
        lab = MoltworkLab(data_dir=f"{td}/lab-fresh", worker_id="support-17")
        stats = lab.rebuild_from_ledger(ledger)
        test("rebuild reads events", stats["total_events"] > 0)
        test("rebuild processes runs", stats["runs_rebuilt"] > 0)
        test("evidence rebuilt", lab.evidence.total_runs == 5)
        test("economics rebuilt", lab.economics.total_spend_usd > 0)
        test("capabilities rebuilt", len(lab.capabilities) > 0)
        test("processes rebuilt", len(lab.version.process_versions) > 0)
        test("run_log rebuilt", len(lab._run_log) == 5)
        print(f"    runs: {stats['runs_rebuilt']}, events: {stats['total_events']}")
        print(f"    spend: ${lab.economics.total_spend_usd:.2f}")
        print(f"    capabilities: {len(lab.capabilities)}")
        print(f"    processes: {len(lab.version.process_versions)}")

        # ─── 5. Verify capabilities match what was used ─────────────────
        print("\n5. Check capabilities")
        cap_names = {c["name"] for c in lab.capabilities}
        test("coding in capabilities", "coding" in cap_names)
        test("api-implementation in capabilities", "api-implementation" in cap_names)
        test("technical-writing in capabilities", "technical-writing" in cap_names)
        for cap in sorted(lab.capabilities, key=lambda c: c.get("runs", 0), reverse=True):
            print(f"    {cap['name']}: runs={cap['runs']}, quality={cap['quality']:.2f}, confidence={cap['confidence']}")

        # ─── 6. Generate profile (the killer feature) ───────────────────
        print("\n6. Worker profile")
        profile = lab.profile()
        test("profile has worker_id", "support-17" in profile)
        test("profile has capabilities", "Capabilities:" in profile)
        test("profile has valuation", "Valuation:" in profile)
        test("profile has economics", "spend" in profile)
        test("profile has processes", "Processes:" in profile)
        print()
        for line in profile.split("\n"):
            print(f"    {line}")

        # ─── 7. Save and reload ─────────────────────────────────────────
        print("\n7. Save → reload → verify identical")
        lab.save()
        lab2 = MoltworkLab(data_dir=f"{td}/lab-fresh")
        lab2.load("support-17")
        test("reload preserves runs", lab2.evidence.total_runs == lab.evidence.total_runs)
        test("reload preserves capabilities", len(lab2.capabilities) == len(lab.capabilities))
        test("reload preserves spend", abs(lab2.economics.total_spend_usd - lab.economics.total_spend_usd) < 0.01)
        test("reload preserves run_log", len(lab2._run_log) == len(lab._run_log))

        # ─── 8. Compare: same ledger, same result ───────────────────────
        print("\n8. Rebuild idempotency")
        lab3 = MoltworkLab(data_dir=f"{td}/lab-fresh2", worker_id="support-17")
        lab3.rebuild_from_ledger(ledger)
        test("rebuild is idempotent (runs)", lab3.evidence.total_runs == lab.evidence.total_runs)
        test("rebuild is idempotent (spend)", abs(lab3.economics.total_spend_usd - lab.economics.total_spend_usd) < 0.01)
        test("rebuild is idempotent (capabilities)", len(lab3.capabilities) == len(lab.capabilities))

        print(f"\n{'='*60}")
        print("FULL FLOW SUMMARY")
        print(f"{'='*60}")
        print(f"Worker: support-17")
        print(f"Campaigns: 5")
        print(f"Events: {event_count}")
        print(f"Chains: {len(run_ids)} valid")
        print(f"Rebuilt: {stats['runs_rebuilt']} runs")
        print(f"Capabilities: {len(lab.capabilities)}")
        print(f"Processes: {len(lab.version.process_versions)}")
        print(f"Spend: ${lab.economics.total_spend_usd:.2f}")
        print(f"Revenue: ${lab.economics.total_revenue_usd:.2f}")
        print(f"{'='*60}")

asyncio.run(run_test())

print(f"\n=== {PASS} passed, {FAIL} failed ===")
if FAIL: sys.exit(1)
else: print("FULL FLOW PASS — run → ledger → rebuild → profile verified")
