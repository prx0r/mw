"""MoltworkLab — the personal Lab. Single-player killer feature.

Wires together:
  - WorkerKit run history → EvidenceState
  - CapabilityTracker → capabilities
  - ValuationEngine → economics + valuation
  - WorkerAsset → worker profile

After every run, call lab.record_run() and the Lab recomputes everything.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.worker_asset import (
    WorkerAsset, CapabilityScore, RuntimeDescriptor,
    ProductionSummary, ValuationSignals,
)
from economics.valuation import compute_valuation, estimate_worker_price


@dataclass
class MemoryState:
    provider: str = "letta"
    agent_id: str = ""
    memfs_commit: str = ""
    memory_tree_digest: str = ""
    blocks: list[dict] = field(default_factory=list)
    last_updated: float = 0.0

    def to_dict(self) -> dict:
        return {"provider": self.provider, "agent_id": self.agent_id,
                "memfs_commit": self.memfs_commit,
                "memory_tree_digest": self.memory_tree_digest,
                "blocks": self.blocks, "last_updated": self.last_updated}


@dataclass
class VersionState:
    repo_path: str = ""
    current_branch: str = "main"
    total_commits: int = 0
    process_versions: list[dict] = field(default_factory=list)
    skill_versions: list[dict] = field(default_factory=list)
    latest_commit: str = ""
    branches: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"repo_path": self.repo_path, "current_branch": self.current_branch,
                "total_commits": self.total_commits,
                "process_versions": self.process_versions,
                "skill_versions": self.skill_versions,
                "latest_commit": self.latest_commit, "branches": self.branches}


@dataclass
class EvidenceState:
    total_runs: int = 0
    verified_runs: int = 0
    total_receipts: int = 0
    acceptance_rate: float = 0.0
    escalation_rate: float = 0.0
    latest_receipt_hash: str = ""
    event_chain_head: str = ""
    last_run_at: float = 0.0

    def to_dict(self) -> dict:
        return {"total_runs": self.total_runs, "verified_runs": self.verified_runs,
                "total_receipts": self.total_receipts,
                "acceptance_rate": round(self.acceptance_rate, 4),
                "escalation_rate": round(self.escalation_rate, 4),
                "latest_receipt_hash": self.latest_receipt_hash,
                "last_run_at": self.last_run_at}


@dataclass
class EconomicsState:
    total_spend_usd: float = 0.0
    total_revenue_usd: float = 0.0
    total_inference_usd: float = 0.0
    total_api_usd: float = 0.0
    avg_cost_per_run: float = 0.0
    cost_trend: str = "STABLE"
    model_usage: dict[str, float] = field(default_factory=dict)
    last_calculated: float = 0.0

    @property
    def gross_contribution(self) -> float:
        return self.total_revenue_usd - self.total_spend_usd

    def to_dict(self) -> dict:
        return {"total_spend_usd": round(self.total_spend_usd, 2),
                "total_revenue_usd": round(self.total_revenue_usd, 2),
                "total_inference_usd": round(self.total_inference_usd, 2),
                "total_api_usd": round(self.total_api_usd, 2),
                "avg_cost_per_run": round(self.avg_cost_per_run, 4),
                "cost_trend": self.cost_trend,
                "model_usage": self.model_usage,
                "last_calculated": self.last_calculated}


class MoltworkLab:
    """Personal Lab — wires WorkerKit + CapabilityTracker + Valuation.

    Usage:
        lab = MoltworkLab(data_dir="data/lab", worker_id="support-17")
        lab.record_run(run, receipt, gate_decision="ALLOW", reward=5.0)
        print(lab.profile())
    """

    def __init__(self, data_dir: str = "data/lab", worker_id: str = ""):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.worker_id = worker_id
        self.memory = MemoryState()
        self.version = VersionState()
        self.evidence = EvidenceState()
        self.economics = EconomicsState()
        self.capabilities: list[dict] = []
        self.education: list[dict] = []
        self._run_log: list[dict] = []  # full run history for recomputation

    def record_run(self, run, receipt, gate_decision: str = "",
                   reward: float = 0.0, task_family: str = "",
                   capabilities_used: list[str] | None = None):
        """Record a completed WorkerKit run. Recomputes everything.

        Args:
            run: WorkerKit Run object (has run.id, run.meter, run._artifacts)
            receipt: WorkReceipt (has root_hash, events_hash)
            gate_decision: "ALLOW" or "DENY"
            reward: payout for this run
            task_family: canonical task family
            capabilities_used: list of capability names used
        """
        cost = float(run.meter.total_cost) if hasattr(run, 'meter') else 0.0
        accepted = gate_decision == "ALLOW"
        run_id = run.run.id if hasattr(run, 'run') else str(run)

        # Record in run log
        self._run_log.append({
            "run_id": run_id,
            "cost": cost,
            "reward": reward,
            "accepted": accepted,
            "task_family": task_family,
            "capabilities": capabilities_used or [],
            "receipt_hash": receipt.root_hash if receipt else "",
            "timestamp": time.time(),
        })

        # Update evidence
        self.evidence.total_runs += 1
        if accepted:
            self.evidence.verified_runs += 1
        self.evidence.total_receipts += 1
        self.evidence.acceptance_rate = self.evidence.verified_runs / max(1, self.evidence.total_runs)
        self.evidence.latest_receipt_hash = receipt.root_hash if receipt else ""
        self.evidence.last_run_at = time.time()

        # Update economics
        self.economics.total_spend_usd += cost
        self.economics.total_revenue_usd += reward if accepted else 0
        self.economics.avg_cost_per_run = self.economics.total_spend_usd / max(1, self.evidence.total_runs)
        self.economics.last_calculated = time.time()

        # Track model usage from events
        if hasattr(run, '_seq'):
            # Try to extract model info from the run's events
            pass  # Model tracking happens at orchestrator level

        # Update capabilities
        for cap_name in (capabilities_used or []):
            self._update_capability(cap_name, accepted, cost, reward)

        # Update version (track process iteration)
        if task_family:
            self._update_process_version(task_family)

    def _update_capability(self, name: str, accepted: bool, cost: float, reward: float):
        """Update or create a capability record."""
        existing = next((c for c in self.capabilities if c.get("name") == name), None)
        if existing:
            existing["runs"] = existing.get("runs", 0) + 1
            existing["accepted"] = existing.get("accepted", 0) + (1 if accepted else 0)
            existing["total_cost"] = existing.get("total_cost", 0) + cost
            existing["total_reward"] = existing.get("total_reward", 0) + (reward if accepted else 0)
            # Recompute quality
            runs = existing["runs"]
            acc = existing["accepted"] / max(1, runs)
            roi = existing["total_reward"] / max(0.01, existing["total_cost"])
            existing["quality"] = round((acc * 0.6 + min(1.0, roi) * 0.4), 4)
            existing["confidence"] = (
                "HIGH" if runs >= 10 else
                "MEDIUM" if runs >= 5 else
                "LOW" if runs >= 2 else
                "INSUFFICIENT"
            )
        else:
            self.capabilities.append({
                "name": name,
                "runs": 1,
                "accepted": 1 if accepted else 0,
                "total_cost": cost,
                "total_reward": reward if accepted else 0,
                "quality": 0.8 if accepted else 0.2,
                "confidence": "INSUFFICIENT",
            })

    def _update_process_version(self, task_family: str):
        """Track process versions (iterative improvement)."""
        existing = next((p for p in self.version.process_versions
                        if p.get("task_family") == task_family), None)
        if existing:
            existing["run_count"] = existing.get("run_count", 0) + 1
            existing["last_used"] = time.time()
        else:
            self.version.process_versions.append({
                "task_family": task_family,
                "version": 1,
                "run_count": 1,
                "created_at": time.time(),
                "last_used": time.time(),
            })

    def compute_valuation(self):
        """Recompute valuation from accumulated economics."""
        w = WorkerAsset(
            worker_id=self.worker_id,
            runtime=RuntimeDescriptor(),
            lineage=[p.get("commit", "") for p in self.version.process_versions],
            education=[{"school_name": e.get("school_name", "")} for e in self.education],
            capabilities=[
                CapabilityScore(name=c["name"], quality=c.get("quality", 0),
                               confidence=c.get("confidence", "INSUFFICIENT"),
                               evidence_count=c.get("runs", 0))
                for c in self.capabilities
            ],
            production=ProductionSummary(
                total_runs=self.evidence.total_runs,
                total_revenue_usd=self.economics.total_revenue_usd,
                total_cost_usd=self.economics.total_spend_usd,
                acceptance_rate=self.evidence.acceptance_rate,
            ),
        )
        return compute_valuation(w)

    def profile(self) -> str:
        """Human-readable worker profile — the single-player killer feature."""
        valuation = self.compute_valuation()
        price = estimate_worker_price(
            WorkerAsset(
                worker_id=self.worker_id,
                capabilities=[CapabilityScore(name=c["name"], quality=c.get("quality", 0))
                             for c in self.capabilities],
                production=ProductionSummary(
                    total_runs=self.evidence.total_runs,
                    total_revenue_usd=self.economics.total_revenue_usd,
                    total_cost_usd=self.economics.total_spend_usd),
            ),
            valuation,
        )

        lines = [
            f"Worker: {self.worker_id}",
            f"Age: {len(self._run_log)} runs recorded",
            "",
            "Lifetime:",
            f"  runs              {self.evidence.total_runs}",
            f"  spend             ${self.economics.total_spend_usd:.2f}",
            f"  verified outcomes {self.evidence.verified_runs}",
            f"  revenue           ${self.economics.total_revenue_usd:.2f}",
            f"  contribution      ${self.economics.gross_contribution:.2f}",
            f"  acceptance rate   {self.evidence.acceptance_rate:.1%}",
            "",
        ]

        if self.capabilities:
            lines.append("Capabilities:")
            for cap in sorted(self.capabilities, key=lambda c: c.get("quality", 0), reverse=True):
                q = cap.get("quality", 0)
                stars = "★" * int(q * 5) + "☆" * (5 - int(q * 5))
                runs = cap.get("runs", 0)
                lines.append(f"  {cap['name']}: {stars} ({cap.get('confidence','?')}, {runs} runs)")
            lines.append("")

        if self.version.process_versions:
            lines.append("Processes:")
            for p in sorted(self.version.process_versions, key=lambda x: x.get("run_count", 0), reverse=True)[:5]:
                lines.append(f"  {p.get('task_family', '?')} v{p.get('version', 1)} ({p.get('run_count', 0)} runs)")
            lines.append("")

        if self.economics.model_usage:
            lines.append("Model spend:")
            for model, spend in sorted(self.economics.model_usage.items(), key=lambda x: x[1], reverse=True)[:3]:
                lines.append(f"  {model}: ${spend:.2f}")
            lines.append("")

        lines.extend([
            "Valuation:",
            f"  12m revenue: ${valuation.trailing_12m_revenue:,.2f}",
            f"  12m contribution: ${valuation.trailing_12m_contribution:,.2f}",
            f"  Utilization: {valuation.utilization_rate:.1%}",
            f"  Trend: {valuation.performance_trend}",
            f"  Capability breadth: {valuation.capability_breadth:.2f}",
            f"  Process defensibility: {valuation.process_defensibility:.2f}",
        ])

        if price > 0:
            lines.append(f"  Estimated monthly: ${price:,.2f}")

        return "\n".join(lines)

    def summary(self) -> dict:
        """Machine-readable worker profile."""
        valuation = self.compute_valuation()
        return {
            "worker_id": self.worker_id,
            "memory": self.memory.to_dict(),
            "version": self.version.to_dict(),
            "evidence": self.evidence.to_dict(),
            "economics": self.economics.to_dict(),
            "capabilities": self.capabilities,
            "education": self.education,
            "valuation": valuation.to_dict(),
            "run_count": len(self._run_log),
        }

    def save(self):
        data = self.summary()
        data["run_log"] = self._run_log  # preserve full history
        path = self.data_dir / f"{self.worker_id}.json"
        path.write_text(json.dumps(data, indent=2))

    def load(self, worker_id: str):
        path = self.data_dir / f"{worker_id}.json"
        if not path.exists():
            self.worker_id = worker_id
            return
        data = json.loads(path.read_text())
        self.worker_id = data.get("worker_id", worker_id)
        self.memory = MemoryState(**data.get("memory", {}))
        self.version = VersionState(**data.get("version", {}))
        self.evidence = EvidenceState(**data.get("evidence", {}))
        self.economics = EconomicsState(**data.get("economics", {}))
        self.capabilities = data.get("capabilities", [])
        self.education = data.get("education", [])
        self._run_log = data.get("run_log", [])

    def rebuild_from_ledger(self, ledger) -> dict:
        """Rebuild Lab state from EventLedger. Real, not simulated.

        Reads every event from the ledger, reconstructs runs,
        recomputes capabilities, economics, and processes.

        Args:
            ledger: core.events.EventLedger instance

        Returns:
            Stats dict with rebuild counts
        """
        # Reset state
        self.evidence = EvidenceState()
        self.economics = EconomicsState()
        self.capabilities = []
        self.version = VersionState()
        self._run_log = []

        # Get all unique run IDs
        conn = ledger._conn()
        run_rows = conn.execute("SELECT DISTINCT run_id FROM events").fetchall()
        run_ids = [r[0] for r in run_rows]
        conn.close()

        runs_rebuilt = 0
        for run_id in run_ids:
            events = ledger.get_events(run_id)
            if not events:
                continue
            self._rebuild_run_from_events(events)
            runs_rebuilt += 1

        # Recompute derived state
        self._recompute_economics()
        self._recompute_processes()

        return {"runs_rebuilt": runs_rebuilt, "total_events": ledger.count()}

    def _rebuild_run_from_events(self, events: list[dict]):
        """Reconstruct a single run from its event chain."""
        import json as _json

        run_id = events[0]["run_id"] if events else ""
        cost = 0.0
        reward = 0.0
        accepted = False
        task_family = ""
        capabilities_used = []
        model = ""
        receipt_hash = ""

        for e in events:
            etype = e["event_type"]
            try:
                payload = _json.loads(e["payload"]) if isinstance(e["payload"], str) else e["payload"]
            except:
                payload = {}

            if etype == "run.started":
                model = payload.get("model", "")

            elif etype == "task.assigned":
                task_family = payload.get("task_family", task_family)
                if not capabilities_used:
                    capabilities_used = payload.get("capabilities", [])

            elif etype == "cost.recorded":
                try:
                    cost += float(payload.get("amount", 0))
                except (ValueError, TypeError):
                    pass

            elif etype == "artifact.registered":
                pass  # artifact tracked elsewhere

            elif etype == "verification.completed":
                if payload.get("status") == "FAIL":
                    accepted = False

            elif etype == "gate.decided":
                if payload.get("decision") == "ALLOW":
                    accepted = True
                elif payload.get("decision") == "DENY":
                    accepted = False

            elif etype == "run.completed":
                try:
                    cost = float(payload.get("cost", cost))
                except (ValueError, TypeError):
                    pass

            elif etype == "dependencies.set":
                capabilities_used = payload.get("skill_version_ids", [])

        # Extract capabilities from task_family if not set from deps
        if not capabilities_used and task_family:
            capabilities_used = [task_family]

        # Record in run log
        self._run_log.append({
            "run_id": run_id,
            "cost": cost,
            "reward": 0,  # reward comes from WorkOrder, not events
            "accepted": accepted,
            "task_family": task_family,
            "capabilities": capabilities_used,
            "model": model,
            "receipt_hash": receipt_hash,
            "timestamp": 0,
        })

        # Update evidence
        self.evidence.total_runs += 1
        if accepted:
            self.evidence.verified_runs += 1
        self.evidence.total_receipts += 1
        self.evidence.acceptance_rate = (
            self.evidence.verified_runs / max(1, self.evidence.total_runs)
        )

        # Update economics
        self.economics.total_spend_usd += cost
        self.economics.avg_cost_per_run = (
            self.economics.total_spend_usd / max(1, self.evidence.total_runs)
        )

        # Track model usage
        if model:
            self.economics.model_usage[model] = (
                self.economics.model_usage.get(model, 0) + cost
            )

        # Update capabilities
        for cap_name in capabilities_used:
            self._update_capability(cap_name, accepted, cost, 0)

        # Update process versions
        if task_family:
            self._update_process_version(task_family)

    def _recompute_economics(self):
        """Recompute economics from accumulated run log."""
        total_cost = sum(r.get("cost", 0) for r in self._run_log)
        total_reward = sum(r.get("reward", 0) for r in self._run_log if r.get("accepted"))
        self.economics.total_spend_usd = total_cost
        self.economics.total_revenue_usd = total_reward
        self.economics.avg_cost_per_run = total_cost / max(1, len(self._run_log))

    def _recompute_processes(self):
        """Recompute process versions from run log."""
        task_counts: dict[str, int] = {}
        for r in self._run_log:
            tf = r.get("task_family", "")
            if tf:
                task_counts[tf] = task_counts.get(tf, 0) + 1

        self.version.process_versions = []
        for tf, count in task_counts.items():
            self.version.process_versions.append({
                "task_family": tf,
                "version": 1,
                "run_count": count,
            })
