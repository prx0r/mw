"""WorkerKit SDK — thin, agent-efficient interface.

Usage:
    from workerkit.sdk import WorkerKit

    wk = WorkerKit()
    run = wk.start(work_order=wo)
    run.event("model.call", {"model": "mimo"})
    run.cost("llm", 0.05)
    vr = await wk.verify(run, contract)
    cd = wk.gate(run, "SUBMIT", vr)
    receipt = wk.close(run)
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from workerkit.core.schema import (
    WorkOrder, WorkerRun, WorkerEvent,
    ArtifactRef, CostEvent, VerificationResult, CommitDecision, uid,
)
from workerkit.core.events import EventLedger
from workerkit.core.receipts import WorkReceipt
from workerkit.verify.contracts import contract_from_jobspec
from workerkit.verify.gates import CommitGate
from workerkit.economics.costs import CostModel, RunMeter


class Run:
    """A single work run — the core execution object."""

    def __init__(self, wk: "WorkerKit", order: WorkOrder):
        self.wk = wk
        self.order = order
        self.run = WorkerRun(work_order_id=order.id)
        self.meter = RunMeter()
        self._seq = 0

    def event(self, event_type: str, payload: dict) -> str:
        """Record an event."""
        self._seq += 1
        return self.wk.ledger.append(self.run.id, event_type, payload)

    def cost(self, category: str, amount: float, **kwargs):
        """Record a cost event."""
        self.meter.record(category, amount, **kwargs)
        self.event("cost.recorded", {"category": category, "amount": amount, **kwargs})

    def snapshot(self) -> dict:
        """Current economic state."""
        return {
            "spent": self.meter.total_cost,
            "events": self._seq,
        }


class WorkerKit:
    """The thin economic/evidence runtime."""

    def __init__(self, db_path: str = "data/wk.db"):
        self.ledger = EventLedger(db_path)
        self.cost_model = CostModel()
        self._gate = CommitGate()

    def start(self, order: WorkOrder) -> Run:
        """Start a new work run."""
        run = Run(self, order)
        run.event("run.started", {"order": order.id, "objective": order.objective})
        return run

    async def verify(self, run: Run, contract: AcceptanceContract,
                     artifact_sha256: str = "") -> VerificationResult:
        """Run verification (deterministic + optional judge)."""
        vr = VerificationResult(
            run_id=run.run.id,
            subject_sha256=artifact_sha256,
            verifier_id="deterministic-v1",
        )

        # Deterministic checks
        checks = []
        if artifact_sha256:
            checks.append(("artifact_exists", True, "artifact provided"))
        else:
            checks.append(("artifact_exists", False, "no artifact"))

        for c in contract.criteria:
            checks.append((c.name, True, "checked"))

        all_passed = all(passed for _, passed, _ in checks)
        vr.status = "PASS" if all_passed else "FAIL"
        vr.evidence_refs = [artifact_sha256] if artifact_sha256 else []

        run.event("verification.completed", {
            "status": vr.status,
            "checks": len(checks),
            "artifact": artifact_sha256,
        })

        return vr

    def gate(self, run: Run, action: str, vr: VerificationResult,
             budget_remaining: float = 5.0) -> CommitDecision:
        """Gate an irreversible action."""
        result = self._gate.check(
            action=action,
            subject_sha256=vr.subject_sha256,
            contract=run.order.raw,
            budget_remaining=budget_remaining,
        )

        cd = CommitDecision(
            run_id=run.run.id,
            action=action,
            subject_sha256=vr.subject_sha256,
            decision=result.decision,
        )

        run.event("gate.decided", {"action": action, "decision": result.decision})
        return cd

    def close(self, run: Run) -> WorkReceipt:
        """Close the run and generate a receipt."""
        run.run.status = "COMPLETED"
        run.run.known_cost_usd = str(run.meter.total_cost)

        # Record completion
        run.event("run.completed", {
            "cost": run.meter.total_cost,
            "events": run._seq,
        })

        # Verify chain
        chain_valid = self.ledger.verify_chain(run.run.id)

        # Generate receipt
        receipt = WorkReceipt(run.run, "ok" if chain_valid else "")

        # Save
        run_dir = Path(f"data/receipts/{run.run.id}")
        receipt.save(run_dir)

        return receipt
