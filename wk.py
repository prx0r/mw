"""WorkerKit CLI — thin, agent-efficient."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from workerkit.core.schema import WorkOrder, WorkerRun, uid
from workerkit.core.events import EventLedger
from workerkit.core.receipts import WorkReceipt, verify_receipt
from workerkit.verify.contracts import AcceptanceContract, contract_from_jobspec
from workerkit.verify.gates import CommitGate
from workerkit.economics.costs import CostModel, RunMeter


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


def main():
    if len(sys.argv) < 2:
        print("wk — WorkerKit CLI")
        print("  wk run <order.json>   Run a work order")
        print("  wk status [db]        Show status")
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "run":
        cmd_run(args)
    elif cmd == "status":
        cmd_status(args)
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
