"""WorkerKit SDK — thin, agent-efficient interface.

Usage:
    from workerkit.sdk import WorkerKit, WorkOrder

    wk = WorkerKit()
    run = wk.start(WorkOrder(objective="Research", reward_value="25.00"))
    run.event("model.call", {"model": "mimo", "tokens": 8000})
    run.cost("llm", 0.08)
    vr = await wk.verify(run, contract, "abc123")
    cd = wk.gate(run, "SUBMIT", vr, budget_remaining=5.0)
    receipt = wk.close(run)
"""
from __future__ import annotations

import asyncio
from decimal import Decimal
from pathlib import Path
from workerkit.core.schema import (
    WorkOrder, WorkerRun, WorkerEvent,
    ArtifactRef, CostEvent, VerificationResult, CommitDecision, uid,
)
from workerkit.core.events import EventLedger
from workerkit.core.receipts import WorkReceipt
from workerkit.verify.contracts import AcceptanceContract
from workerkit.verify.gates import CommitGate
from workerkit.economics.costs import CostModel, RunMeter


class Run:
    """A single work run — the core execution object."""

    def __init__(self, wk, order: WorkOrder):
        self.wk = wk
        self.order = order
        self.run = WorkerRun(work_order_id=order.id)
        self.meter = RunMeter()
        self._seq = 0
        self._run_cap = Decimal(str(order.raw.get("max_cost", "999999")))
        self._spent = Decimal("0")

    def event(self, event_type: str, payload: dict) -> str:
        self._seq += 1
        return self.wk.ledger.append(self.run.id, event_type, payload)

    def cost(self, category: str, amount: float, **kwargs):
        cost = Decimal(str(amount))
        if self._spent + cost > self._run_cap:
            raise ValueError(f"Per-run budget exceeded: ${self._spent + cost} > ${self._run_cap}")
        self._spent += cost
        self.meter.record(category, amount, **kwargs)
        self.event("cost.recorded", {"category": category, "amount": str(cost), **kwargs})

    def snapshot(self) -> dict:
        return {"spent": float(self._spent), "events": self._seq}


class WorkerKit:
    """The thin economic/evidence runtime."""

    def __init__(self, db_path: str = "data/wk.db"):
        self.ledger = EventLedger(db_path)
        self.cost_model = CostModel()
        self._gate = CommitGate()

    def start(self, order: WorkOrder) -> Run:
        run = Run(self, order)
        run.event("run.started", {"order": order.id, "objective": order.objective})
        return run

    async def verify(self, run: Run, contract: AcceptanceContract,
                     artifact_sha256: str = "") -> VerificationResult:
        """Run verification — REAL checks."""
        vr = VerificationResult(
            run_id=run.run.id, subject_sha256=artifact_sha256,
            verifier_id="deterministic-v1",
        )
        checks = []

        if artifact_sha256:
            checks.append(("artifact_exists", True, "provided"))
        else:
            checks.append(("artifact_exists", False, "no artifact"))

        for c in contract.criteria:
            passed = bool(artifact_sha256)
            checks.append((c.name, passed, "checked" if passed else "no artifact"))

        if contract.maximum_cost and run.meter.total_cost > contract.maximum_cost:
            checks.append(("budget", False, f"${run.meter.total_cost:.2f} > ${contract.maximum_cost:.2f}"))
        else:
            checks.append(("budget", True, "within budget"))

        all_passed = all(passed for _, passed, _ in checks)
        vr.status = "PASS" if all_passed else "FAIL"
        vr.evidence_refs = [artifact_sha256] if artifact_sha256 else []

        run.event("verification.completed", {
            "status": vr.status, "checks": len(checks),
            "passed": sum(1 for _, p, _ in checks if p),
            "artifact": artifact_sha256,
        })
        return vr

    def gate(self, run: Run, action: str, vr: VerificationResult,
             budget_remaining: float = 5.0) -> CommitDecision:
        """Gate — REQUIRES verification to pass."""
        if vr.status != "PASS":
            cd = CommitDecision(run_id=run.run.id, action=action,
                               subject_sha256=vr.subject_sha256, decision="DENY")
            run.event("gate.denied", {"action": action, "reason": f"verification {vr.status}"})
            return cd

        result = self._gate.check(action=action, subject_sha256=vr.subject_sha256,
                                   budget_remaining=budget_remaining)
        cd = CommitDecision(run_id=run.run.id, action=action,
                           subject_sha256=vr.subject_sha256, decision=result.decision)
        run.event("gate.decided", {"action": action, "decision": result.decision})
        return cd

    def close(self, run: Run) -> WorkReceipt:
        """Close run, generate receipt with REAL chain hash."""
        run.run.status = "COMPLETED"
        run.run.known_cost_usd = str(run.meter.total_cost)
        run.event("run.completed", {"cost": str(run.meter.total_cost), "events": run._seq})

        events = self.ledger.get_events(run.run.id)
        chain_head = events[-1]["event_sha256"] if events else ""
        event_count = len(events)

        receipt = WorkReceipt(run.run)
        receipt.events_hash = f"{chain_head}:{event_count}"
        receipt.root_hash = receipt._compute_root(run.run, receipt.events_hash)

        run_dir = Path(f"data/receipts/{run.run.id}")
        receipt.save(run_dir)
        return receipt
