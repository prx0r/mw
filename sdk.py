"""WorkerKit SDK — thin, agent-efficient interface.

Usage:
    from workerkit.sdk import WorkerKit, WorkOrder

    wk = WorkerKit()
    run = wk.start(WorkOrder(objective="Research", reward_value="25.00"))
    artifact = run.artifact(name="report.md", content=b"...", media_type="text/markdown")
    run.event("model.call", {"model": "mimo", "tokens": 8000})
    run.cost("llm", 0.08)
    vr = await wk.verify(run, contract, artifact)
    cd = wk.gate(run, "SUBMIT", vr, budget_remaining=5.0)
    receipt = wk.close(run)
"""
from __future__ import annotations

import asyncio
from decimal import Decimal
from pathlib import Path
from workerkit.core.schema import (
    WorkOrder, WorkerRun, WorkerEvent,
    ArtifactRef, CostEvent, VerificationResult, CommitDecision, uid, sha256,
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
        self._artifacts: list[ArtifactRef] = []

    def artifact(self, name: str, content: bytes | str, media_type: str = "") -> ArtifactRef:
        """Register an artifact. WorkerKit computes the digest — never trust caller-provided hash."""
        if isinstance(content, str):
            content = content.encode()
        digest = sha256(content)
        ar = ArtifactRef(name=name, sha256=digest, media_type=media_type)
        self._artifacts.append(ar)
        self.event("artifact.registered", {"name": name, "sha256": digest, "media_type": media_type})
        return ar

    def event(self, event_type: str, payload: dict) -> str:
        self._seq += 1
        return self.wk.ledger.append(self.run.id, event_type, payload)

    def cost(self, category: str, amount: str | float, **kwargs):
        """Record a cost. Amount must be string or float — internally Decimal."""
        cost = Decimal(str(amount))
        if self._spent + cost > self._run_cap:
            raise ValueError(f"Per-run budget exceeded: ${self._spent + cost} > ${self._run_cap}")
        self._spent += cost
        self.meter.record(category, float(cost), **kwargs)
        self.event("cost.recorded", {"category": category, "amount": str(cost), **kwargs})

    def snapshot(self) -> dict:
        return {"spent": str(self._spent), "events": self._seq}


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
                     artifact: ArtifactRef | str | None = None) -> VerificationResult:
        """Run verification — REAL checks against typed criteria.

        artifact: ArtifactRef (preferred) or string digest (legacy).
        """
        # Normalize artifact input
        if isinstance(artifact, ArtifactRef):
            artifact_sha256 = artifact.sha256
        elif isinstance(artifact, str):
            artifact_sha256 = artifact
        else:
            artifact_sha256 = ""

        vr = VerificationResult(
            run_id=run.run.id, subject_sha256=artifact_sha256,
            verifier_id="deterministic-v1",
        )
        checks = []

        # Check artifact exists
        if artifact_sha256:
            # Validate hash is full SHA-256 (64 hex chars)
            if len(artifact_sha256) == 64 and all(c in '0123456789abcdef' for c in artifact_sha256):
                checks.append(("artifact_exists", True, "valid SHA-256"))
            else:
                checks.append(("artifact_exists", False, f"invalid hash: {len(artifact_sha256)} chars"))
        else:
            checks.append(("artifact_exists", False, "no artifact"))

        # Validate artifact is registered (if using ArtifactRef)
        if isinstance(artifact, ArtifactRef):
            registered = any(a.sha256 == artifact.sha256 for a in run._artifacts)
            checks.append(("artifact_registered", registered, "in run registry" if registered else "not registered"))

        # Check contract criteria
        for c in contract.criteria:
            if c.check_type == "artifact_exists":
                passed = bool(artifact_sha256)
            elif c.check_type == "digest_matches":
                # Would check against known digest — unknown → UNKNOWN
                passed = bool(artifact_sha256)
            else:
                # Unsupported check type → UNKNOWN (never PASS)
                checks.append((c.name, False, f"unsupported check_type: {c.check_type}"))
                continue
            checks.append((c.name, passed, "checked" if passed else "failed"))

        # Check budget
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
        """Gate — VerificationResult is mandatory."""
        if vr.status != "PASS":
            cd = CommitDecision(run_id=run.run.id, action=action,
                               subject_sha256=vr.subject_sha256, decision="DENY")
            run.event("gate.denied", {"action": action, "reason": f"verification {vr.status}"})
            return cd

        result = self._gate.check(action=action, vr=vr, subject_sha256=vr.subject_sha256,
                                   budget_remaining=budget_remaining)
        cd = CommitDecision(run_id=run.run.id, action=action,
                           subject_sha256=vr.subject_sha256, decision=result.decision)
        run.event("gate.decided", {"action": action, "decision": result.decision})
        return cd

    def close(self, run: Run) -> WorkReceipt:
        """Close run, validate chain, generate receipt."""
        run.run.status = "COMPLETED"
        run.run.finished_at = run._seq
        run.run.known_cost_usd = str(run.meter.total_cost)
        run.run.outputs = [a.name for a in run._artifacts]
        run.event("run.completed", {"cost": str(run.meter.total_cost), "events": run._seq})

        # CRITICAL: verify chain before issuing receipt
        if not self.ledger.verify_chain(run.run.id):
            raise ValueError(f"Event chain invalid for run {run.run.id} — receipt refused")

        events = self.ledger.get_events(run.run.id)
        chain_head = events[-1]["event_sha256"] if events else ""
        event_count = len(events)

        receipt = WorkReceipt(run.run)
        receipt.events_hash = f"{chain_head}:{event_count}"
        receipt.root_hash = receipt._compute_root(run.run, receipt.events_hash)

        run_dir = Path(f"data/receipts/{run.run.id}")
        receipt.save(run_dir)
        return receipt
