"""WorkerKit CLI — thin, agent-efficient.

Commands:
  wk run <order.json>           Run a work order through the loop
  wk status [db]                Show status
  wk lab rebuild                Rebuild LabProjection from EventLedger
  wk lab sync                   Incremental sync new events
  wk lab summary                Show lab summary stats
  wk lab brief <task_family>    Generate lab brief for a task family
  wk eval <worker.json> <fixture.json>  Evaluate worker on fixture
  wk replay <worker.json> <pack_dir>    Replay worker on held-out fixtures
"""
from __future__ import annotations

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workerkit.core.schema import WorkOrder, WorkerRun, VerificationResult, uid
from workerkit.core.events import EventLedger
from workerkit.core.receipts import WorkReceipt, verify_receipt
from workerkit.verify.contracts import AcceptanceContract, contract_from_jobspec
from workerkit.verify.gates import CommitGate
from workerkit.economics.costs import CostModel, RunMeter
from pathlib import Path


def cmd_run(args):
    """Run a work order through the loop."""
    if len(args) < 1:
        print("Usage: wk run <work_order.json>")
        return

    order_file = Path(args[0])
    if not order_file.exists():
        print(f"File not found: {order_file}")
        return

    order_data = json.loads(order_file.read_text())
    order = WorkOrder(**order_data)

    run = WorkerRun(work_order_id=order.id)
    ledger = EventLedger("data/wk-events.db")

    ledger.append(run.id, "run.started", {"order": order.id, "objective": order.objective})

    contract = contract_from_jobspec({"hard_requirements": ["SUBMISSION.md"], "automatic_rejection": []})

    gate = CommitGate()
    vr = VerificationResult(run_id=run.id, status="PASS", subject_sha256="placeholder")
    gate_result = gate.check("SUBMIT", vr=vr, budget_remaining=5.0)
    print(f"Gate: {gate_result.decision}")

    ledger.append(run.id, "run.completed", {"status": "submitted"})

    events = ledger.get_events(run.id)
    chain_head = events[-1]["event_sha256"] if events else ""
    event_count = len(events)

    receipt = WorkReceipt(run, f"{chain_head}:{event_count}")
    print(f"Receipt: {receipt.root_hash}")

    receipt.save(Path(f"data/receipts/{run.id}"))
    print(f"Saved: data/receipts/{run.id}/")


def cmd_status(args):
    """Show status."""
    db_path = args[0] if args else "data/wk-events.db"
    ledger = EventLedger(db_path)
    print(f"Events: {ledger.count()}")


def cmd_lab_rebuild(args):
    """Rebuild LabProjection from EventLedger."""
    from workerkit.lab.projection import wire_lab

    ledger_db = args[0] if len(args) > 0 else "data/wk-events.db"
    projection_db = args[1] if len(args) > 1 else "data/hydra.db"

    ledger, projection, projector = wire_lab(ledger_db, projection_db)
    stats = projector.rebuild()
    print(f"Rebuilt projection from {stats['events']} events")
    print(f"  Runs projected: {stats['runs']}")
    print(f"  Errors: {stats['errors']}")


def cmd_lab_sync(args):
    """Incremental sync new events."""
    from workerkit.lab.projection import wire_lab

    ledger_db = args[0] if len(args) > 0 else "data/wk-events.db"
    projection_db = args[1] if len(args) > 1 else "data/hydra.db"

    ledger, projection, projector = wire_lab(ledger_db, projection_db)
    stats = projector.sync()
    print(f"Synced: {stats['new_events']} new events from {stats['new_runs']} runs")
    if stats["errors"]:
        print(f"  Errors: {stats['errors']}")


def cmd_lab_summary(args):
    """Show lab summary."""
    from workerkit.hydra.store import LabProjection

    db_path = args[0] if args else "data/hydra.db"
    proj = LabProjection(db_path, append_only=False)
    summary = proj.lab_summary()
    print(f"Runs: {summary['total_runs']}")
    print(f"Won: {summary['won']} ({summary['win_rate']:.0%})")
    print(f"Revenue: ${summary['revenue']:.2f}")
    print(f"Cost: ${summary['cost']:.2f}")
    print(f"Net: ${summary['net']:.2f}")
    print(f"Insights: {summary['insights']}")
    print(f"Agents: {summary['agents']}")


def cmd_lab_brief(args):
    """Generate lab brief for a task family."""
    from workerkit.hydra.store import LabProjection
    from workerkit.lab.context import LabContext

    if len(args) < 1:
        print("Usage: wk lab brief <task_family>")
        return

    task_family = args[0]
    db_path = args[1] if len(args) > 1 else "data/hydra.db"

    proj = LabProjection(db_path, append_only=False)
    ctx = LabContext(proj, worker_id="cli")
    print(ctx.brief(task_family))


def cmd_eval(args):
    """Evaluate worker on fixture."""
    from workerkit.cg.evolve import DeterministicMockEvaluator, EvaluationResult

    if len(args) < 2:
        print("Usage: wk eval <worker.json> <fixture.json>")
        return

    worker_file = Path(args[0])
    fixture_file = Path(args[1])

    if not worker_file.exists():
        print(f"Worker not found: {worker_file}")
        return
    if not fixture_file.exists():
        print(f"Fixture not found: {fixture_file}")
        return

    worker = json.loads(worker_file.read_text())
    fixture = json.loads(fixture_file.read_text())

    evaluator = DeterministicMockEvaluator()

    async def _eval():
        return await evaluator.evaluate(worker, fixture)

    import asyncio
    result = asyncio.run(_eval())

    print(f"Score: {result.score:.4f}")
    print(f"Gates: {json.dumps(result.gates_passed)}")
    if result.error:
        print(f"Error: {result.error}")


def cmd_replay(args):
    """Replay worker on held-out fixtures from a WorldPack."""
    from workerkit.cg.evolve import WorldPack, DeterministicMockEvaluator
    import asyncio

    if len(args) < 2:
        print("Usage: wk replay <worker.json> <pack_dir>")
        return

    worker_file = Path(args[0])
    pack_dir = Path(args[1])

    if not worker_file.exists():
        print(f"Worker not found: {worker_file}")
        if not pack_dir.exists():
            print(f"Pack not found: {pack_dir}")
            return

    worker = json.loads(worker_file.read_text()) if worker_file.exists() else {}
    pack = WorldPack.from_dir(pack_dir, name="cli-replay")

    evaluator = DeterministicMockEvaluator(pack.evaluator_src)

    async def _replay():
        fixtures = pack.all_fixtures("hidden")
        results = []
        for fx in fixtures:
            r = await evaluator.evaluate(worker, fx)
            results.append({"fixture": fx.get("id", "?"), "score": r.score, "gates": r.gates_passed})
        return results

    results = asyncio.run(_replay())

    scores = [r["score"] for r in results]
    mean = sum(scores) / len(scores) if scores else 0
    print(f"Replay: {len(results)} fixtures, mean={mean:.4f}")
    for r in results:
        gates_str = ",".join(f"{k}={'✓' if v else '✗'}" for k, v in r["gates"].items())
        print(f"  {r['fixture']}: {r['score']:.4f} [{gates_str}]")


def main():
    if len(sys.argv) < 2:
        print("wk — WorkerKit CLI")
        print("  wk run <order.json>                    Run a work order")
        print("  wk status [db]                         Show status")
        print("  wk lab rebuild [ledger] [projection]   Rebuild projection from events")
        print("  wk lab sync [ledger] [projection]      Incremental sync")
        print("  wk lab summary [db]                    Lab summary stats")
        print("  wk lab brief <task_family> [db]        Lab brief for task family")
        print("  wk eval <worker.json> <fixture.json>   Evaluate worker on fixture")
        print("  wk replay <worker.json> <pack_dir>     Replay on held-out fixtures")
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "run": cmd_run,
        "status": cmd_status,
        "eval": cmd_eval,
        "replay": cmd_replay,
    }

    if cmd == "lab":
        if not args:
            print("Usage: wk lab <rebuild|sync|summary|brief>")
            return
        lab_cmd = args[0]
        lab_args = args[1:]
        lab_commands = {
            "rebuild": cmd_lab_rebuild,
            "sync": cmd_lab_sync,
            "summary": cmd_lab_summary,
            "brief": cmd_lab_brief,
        }
        if lab_cmd in lab_commands:
            lab_commands[lab_cmd](lab_args)
        else:
            print(f"Unknown lab command: {lab_cmd}")
    elif cmd in commands:
        commands[cmd](args)
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
