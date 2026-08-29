"""WorkerKit CLI — thin, agent-efficient."""
from __future__ import annotations

import asyncio
import json
import sys
from workerkit.core.schema import WorkOrder, WorkRun, uid
from workerkit.core.events import EventLedger
from workerkit.core.receipts import WorkReceipt
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

    # Create run
    run = WorkRun(id=uid(), work_order_id=order.id)
    ledger = EventLedger("data/wk-events.db")

    # Record start
    ledger.append(run.id, "run.started", {"order": order.id, "objective": order.objective})

    # Contract
    contract = contract_from_jobspec({"hard_requirements": ["SUBMISSION.md"], "automatic_rejection": []})

    # Gate
    gate = CommitGate()
    gate_result = gate.check("SUBMIT", budget_remaining=5.0)
    print(f"Gate: {gate_result.decision}")

    # Record completion
    ledger.append(run.id, "run.completed", {"status": "submitted"})

    # Generate receipt
    receipt = WorkReceipt(run, ledger.verify_chain(run.id) and ledger.count(run.id) or "")
    print(f"Receipt: {receipt.root_hash}")

    # Save
    receipt.save(Path(f"data/receipts/{run.id}"))
    print(f"Saved: data/receipts/{run.id}/")


def cmd_status(args):
    """Show status."""
    ledger = EventLedger("data/wk-events.db")
    print(f"Events: {ledger.count()}")
    print(f"Chain valid: {ledger.verify_chain()}")


def main():
    if len(sys.argv) < 2:
        print("wk — WorkerKit CLI")
        print("  wk run <order.json>   Run a work order")
        print("  wk status             Show status")
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
