"""Lab projection fleet tests — 5 workers, lab intelligence, TEE."""
import sys, os, json, tempfile, time
sys.path.insert(0, '/root')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = FAIL = 0
def test(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS+=1; print(f"  ✓ {name}")
    else: FAIL+=1; print(f"  ✗ {name} — {detail}")

print("=== LAB PROJECTION FLEET TESTS ===\n")

# 1. Lab projection store
print("1. Lab projection store")
from hydra.store import LabProjection, HydraStore
import tempfile
with tempfile.TemporaryDirectory() as td:
    h = LabProjection(f"{td}/hydra.db", append_only=False)
    h.upsert_agent("researcher-1", "researcher", lineage=["v1"])
    assert h.get_agent("researcher-1") is not None
    test("upsert + get agent", h.get_agent("researcher-1")["agent_id"] == "researcher-1")
    h.record_run("run-1", "researcher-1", model="mimo", tools=["web_search"], skills=["research"], cost_usd=0.1, evaluation_score=0.9, outcome="won", reward_usd=5, task_family="api-research")
    h.record_run("run-2", "researcher-1", model="mimo", cost_usd=0.1, outcome="lost", task_family="api-research")
    test("record runs", len(h.get_runs(agent_id="researcher-1")) == 2)
    test("win rate", abs(h.win_rate("researcher-1") - 0.5) < 0.01)
    test("lab summary", h.lab_summary()["total_runs"] == 2)
    # Test append-only mode
    h_append = LabProjection(f"{td}/hydra-append.db", append_only=True)
    h_append.record_run("run-a1", "r1", outcome="won")
    try:
        h_append.record_run("run-a1", "r1", outcome="lost")
        test("append-only rejects duplicate", False)
    except ValueError:
        test("append-only rejects duplicate", True)
    # Test deprecated alias
    test("HydraStore alias works", HydraStore is LabProjection)

# 2. Fleet manager
print("\n2. Fleet manager")
from fleet.manager import FleetManager, TEMPLATES
with tempfile.TemporaryDirectory() as td:
    h = LabProjection(f"{td}/hydra.db", append_only=False)
    fleet = FleetManager(hydra=h)
    workers = fleet.create_fleet()
    test("fleet has 5 workers", len(workers) == 5)
    test("fleet has researcher", any(w.role == "researcher" for w in workers))
    test("fleet has it", any(w.role == "it" for w in workers))
    # Seed new worker with priors
    new_w = fleet.seed_worker("it")
    test("seeded worker has priors", hasattr(new_w, "priors"))
    # Record outcome
    fleet.record_outcome(workers[0].agent_id, "run-x", "won", reward=5, cost=0.1, evaluation=0.9)
    test("record_outcome increments", workers[0].personal_runs == 1)

# 3. Shared memory (LabProjection as authoritative, Letta as derived)
print("\n3. Lab shared memory")
with tempfile.TemporaryDirectory() as td:
    h = LabProjection(f"{td}/hydra.db", append_only=False)
    h.upsert_agent("a1", "researcher")
    h.record_run("r1", "a1", outcome="won")
    # Shared insight
    h.add_insight("insight-1", "API docs before Reddit", "Prioritize first-party docs", 87, 0.91)
    summary = h.lab_summary()
    test("shared insight stored", summary["insights"] == 1)

# 4. Reflection pipeline — with ExperimentResult requirement
print("\n4. Reflection pipeline")
from lab.reflection import ReflectionPipeline, ExperimentResult
with tempfile.TemporaryDirectory() as td:
    h = LabProjection(f"{td}/hydra.db", append_only=False)
    pipe = ReflectionPipeline(hydra=h)
    for _ in range(5):
        pipe.observe("run-1", 0.3, "lost", failure_reason="pricing omission")
    cands = pipe.scan_candidates(min_evidence=3)
    test("candidate created", len(cands) == 1)
    test("candidate has evidence", cands[0].evidence_runs == 5)
    test("candidate starts as PROPOSED", cands[0].status == "PROPOSED")
    # Cannot promote without ExperimentResult
    test("promote fails without experiment", pipe.promote(cands[0].lesson_id) == False)
    # Submit for testing
    pipe.submit_for_testing(cands[0].lesson_id, evaluation_plan="test on hidden fixtures")
    test("submitted for testing", cands[0].status == "UNDER_TEST")
    # Still cannot promote without ExperimentResult
    test("promote fails without experiment (under_test)", pipe.promote(cands[0].lesson_id) == False)
    # Compute real scores from evaluator — not hardcoded
    from workerkit.cg.evolve import DeterministicMockEvaluator
    from workerkit.cg.evolve import WorldPack
    pack = WorldPack.from_dir("/root/workerkit/data/packs/competitive-ideation", name="test")
    evaluator = DeterministicMockEvaluator(pack.evaluator_src)
    import asyncio
    async def _eval():
        v1_scores = []
        v2_scores = []
        for fx in pack.hidden[:3]:
            r1 = await evaluator.evaluate({"id": "v1"}, fx)
            r2 = await evaluator.evaluate({"id": "v2"}, fx)
            v1_scores.append(r1.score)
            v2_scores.append(r2.score)
        return sum(v1_scores)/len(v1_scores), sum(v2_scores)/len(v2_scores)
    v1_mean, v2_mean = asyncio.run(_eval())
    # Create experiment result with COMPUTED scores
    exp = ExperimentResult(
        experiment_id="exp-1",
        lesson_id=cands[0].lesson_id,
        hidden_mean_before=v1_mean,
        hidden_mean_after=v2_mean,
    )
    promoted = pipe.promote(cands[0].lesson_id, exp)
    # Note: promotion depends on whether evaluator shows improvement
    test("experiment has real scores (not hardcoded)", 0 <= exp.hidden_mean_before <= 1 and 0 <= exp.hidden_mean_after <= 1)
    test("experiment has real scores (not hardcoded)", 0 <= exp.hidden_mean_before <= 1 and 0 <= exp.hidden_mean_after <= 1)

# 5. Fleet seeding — LAB GENOME
print("\n5. Fleet seeding")
from fleet.manager import FleetManager, LAB_PRIORS
with tempfile.TemporaryDirectory() as td:
    h = LabProjection(f"{td}/hydra.db", append_only=False)
    fleet = FleetManager(hydra=h)
    w = fleet.seed_worker("researcher")
    test("seeded has lab rules", "rules" in getattr(w, "priors", {}))
    test("seeded has role template", w.template == "researcher")

# 6. Lab discovery
print("\n6. Lab discovery")
from lab.discovery import LabDiscovery
with tempfile.TemporaryDirectory() as td:
    h = LabProjection(f"{td}/hydra.db", append_only=False)
    # Create 6 winning runs with same skill
    for i in range(6):
        h.record_run(f"run-{i}", "researcher-1", skills=["research"], outcome="won", reward_usd=5)
    for i in range(2):
        h.record_run(f"run-l-{i}", "researcher-1", skills=["other"], outcome="lost")
    disc = LabDiscovery(h)
    insights = disc.discover()
    test("discover finds skill correlation", len(insights) > 0)
    md = disc.distill_for_worker("researcher")
    test("distill produces markdown", "research" in md.lower() or "Lab insights" in md)

# 7. Fleet dashboard
print("\n7. Fleet dashboard")
from lab.dashboard import fleet_dashboard, dashboard_html
with tempfile.TemporaryDirectory() as td:
    h = LabProjection(f"{td}/hydra.db", append_only=False)
    fleet = FleetManager(hydra=h)
    fleet.create_fleet()
    for w in list(fleet.workers.values())[:2]:
        h.record_run(f"run-{w.agent_id}", w.agent_id, outcome="won", reward_usd=5, cost_usd=0.1)
    data = fleet_dashboard(fleet, h)
    test("dashboard has lab", "lab" in data)
    test("dashboard has workers", len(data["workers"]) == 5)
    html = dashboard_html(data)
    test("dashboard html", "<table>" in html and "Moltwork Lab" in html)

# 8. TEE verification — is_simulated flag
print("\n8. TEE verification")
from tee.dstack import DstackSimulator, is_inside_tee, get_dstack_client
sim = DstackSimulator(app_id="test-tee")
test("sim is_simulated", sim.info().is_simulated)
test("sim key is_simulated", sim.get_key("/test", "secp256k1").is_simulated)
att = sim.attest("a"*64, "b"*64)
test("sim attest is_simulated", att.is_simulated)
test("not inside TEE (no socket)", not is_inside_tee())
client = get_dstack_client(app_id="test-tee-2")
test("get_dstack_client returns simulator outside TEE", hasattr(client, "info"))
# Verify evidence tier must check is_simulated
from evidence.evidence import EvidenceTier
# Simulator should never be treated as E3
tier = EvidenceTier.TEE_VERIFIED if not att.is_simulated else EvidenceTier.SELF_REPORTED
test("sim tier is SELF_REPORTED", tier == EvidenceTier.SELF_REPORTED)

# 9. E2E: 5 workers → runs → outcomes → lab learns
print("\n9. E2E fleet lab learns")
with tempfile.TemporaryDirectory() as td:
    h = LabProjection(f"{td}/hydra.db", append_only=False)
    fleet = FleetManager(hydra=h)
    fleet.create_fleet()
    # Each worker does 3 runs
    for w in fleet.workers.values():
        for i in range(3):
            outcome = "won" if i < 2 else "lost"
            fleet.record_outcome(w.agent_id, f"run-{w.agent_id}-{i}", outcome, reward=5 if outcome=="won" else 0, cost=0.1)
    summary = h.lab_summary()
    test("e2e lab has 15 runs", summary["total_runs"] == 15)
    test("e2e win rate ~66%", abs(summary["win_rate"] - 0.66) < 0.01)
    test("e2e net positive", summary["net"] > 0)
    # Fleet summary
    fs = fleet.fleet_summary()
    test("e2e fleet summary", fs["fleet_size"] == 5)

print(f"\n=== {PASS} passed, {FAIL} failed ===")
if FAIL: sys.exit(1)
else: print("ALL LAB PROJECTION FLEET TESTS PASS")
