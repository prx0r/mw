"""WorkerAsset — the core primitive.

Everything interacts with WorkerAsset:
  - Oracle discovers demand for its capabilities
  - Orchestrator dispatches work to it
  - Lab trains it
  - Marketplace sells/leases it
  - Evidence layer proves its history
  - Valuation engine prices it

A WorkerAsset is NOT an agent. It's a productive business asset with
measurable economics, accumulated experience, and transferable ownership.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from core.hashing import sha256, jcs


# ─── Sub-types ────────────────────────────────────────────────────────

@dataclass
class RuntimeDescriptor:
    """What runtime this worker runs on. Chain-neutral, runtime-neutral."""
    adapter: str = ""  # letta, openclaw, hermes, custom
    model: str = ""
    model_provider: str = ""
    tee_platform: str = ""  # dstack, phala, none
    tools: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"adapter": self.adapter, "model": self.model,
                "model_provider": self.model_provider, "tee_platform": self.tee_platform,
                "tools": self.tools}


@dataclass
class CapabilityScore:
    """Multi-dimensional capability assessment. Benchmark-backed, not self-reported."""
    name: str = ""
    quality: float = 0.0  # 0.0-1.0, from evaluation history
    confidence: str = "UNKNOWN"  # LOW, MEDIUM, HIGH, INSUFFICIENT
    evidence_count: int = 0
    benchmark_scores: dict[str, float] = field(default_factory=dict)  # benchmark_id → score
    cost_efficiency: float = 0.0  # reward/cost ratio
    consistency: float = 0.0  # std dev of quality
    trend: str = "STABLE"  # IMPROVING, STABLE, DEGRADING

    def to_dict(self) -> dict:
        return {"name": self.name, "quality": round(self.quality, 4),
                "confidence": self.confidence, "evidence_count": self.evidence_count,
                "benchmark_scores": self.benchmark_scores,
                "cost_efficiency": round(self.cost_efficiency, 4),
                "trend": self.trend}


@dataclass
class EducationRecord:
    """What the worker has learned. Schools, benchmarks, certifications."""
    school_id: str = ""
    school_name: str = ""
    curriculum_version: str = ""
    completed_at: float = 0.0
    benchmark_results: dict[str, float] = field(default_factory=dict)  # benchmark_id → score
    certificate_hash: str = ""  # content-addressed proof

    def to_dict(self) -> dict:
        return {"school_id": self.school_id, "school_name": self.school_name,
                "curriculum_version": self.curriculum_version,
                "completed_at": self.completed_at,
                "benchmark_results": self.benchmark_results,
                "certificate_hash": self.certificate_hash}


@dataclass
class ProductionSummary:
    """Trailing production economics. The core valuation input."""
    total_runs: int = 0
    total_revenue_usd: float = 0.0
    total_cost_usd: float = 0.0
    total_inference_usd: float = 0.0
    total_api_usd: float = 0.0
    total_compute_usd: float = 0.0
    total_escalation_cost_usd: float = 0.0
    acceptance_rate: float = 0.0  # runs accepted / total runs
    escalation_rate: float = 0.0  # human escalations / total runs
    avg_cost_per_run: float = 0.0
    avg_duration_s: float = 0.0
    unique_environments: int = 0  # how many distinct customers/contexts

    @property
    def gross_contribution(self) -> float:
        return self.total_revenue_usd - self.total_cost_usd

    @property
    def operating_cost(self) -> float:
        return (self.total_inference_usd + self.total_api_usd +
                self.total_compute_usd + self.total_escalation_cost_usd)

    def to_dict(self) -> dict:
        return {"total_runs": self.total_runs,
                "total_revenue_usd": round(self.total_revenue_usd, 2),
                "total_cost_usd": round(self.total_cost_usd, 2),
                "total_inference_usd": round(self.total_inference_usd, 2),
                "total_api_usd": round(self.total_api_usd, 2),
                "total_compute_usd": round(self.total_compute_usd, 2),
                "total_escalation_cost_usd": round(self.total_escalation_cost_usd, 2),
                "acceptance_rate": round(self.acceptance_rate, 4),
                "escalation_rate": round(self.escalation_rate, 4),
                "avg_cost_per_run": round(self.avg_cost_per_run, 4),
                "avg_duration_s": round(self.avg_duration_s, 2),
                "unique_environments": self.unique_environments}


@dataclass
class LeaseRecord:
    """Historical lease. Proves demand for this worker."""
    lease_id: str = ""
    owner: str = ""
    lessee: str = ""
    start_time: float = 0.0
    end_time: float = 0.0
    revenue_usd: float = 0.0
    sla_adherence: float = 0.0  # 0.0-1.0
    transferred: bool = False  # did lease transfer with ownership?

    def to_dict(self) -> dict:
        return {"lease_id": self.lease_id, "owner": self.owner, "lessee": self.lessee,
                "revenue_usd": round(self.revenue_usd, 2),
                "sla_adherence": round(self.sla_adherence, 4),
                "transferred": self.transferred}


@dataclass
class ValuationSignals:
    """Computed valuation signals. Updated periodically."""
    trailing_12m_revenue: float = 0.0
    trailing_12m_contribution: float = 0.0
    utilization_rate: float = 0.0  # active lease hours / available hours
    capability_breadth: float = 0.0  # normalized count of capabilities
    performance_trend: str = "STABLE"  # IMPROVING, STABLE, DEGRADING
    customer_concentration: float = 0.0  # HHI (higher = riskier)
    runtime_dependency: float = 0.0  # 0 = fully portable, 1 = locked to one runtime
    process_defensibility: float = 0.0  # how unique/hard to replicate
    renewal_rate: float = 0.0  # lease renewals / lease completions
    estimated_monthly_cost: float = 0.0

    def to_dict(self) -> dict:
        return {k: round(v, 4) if isinstance(v, float) else v
                for k, v in self.__dict__.items()}


# ─── The core primitive ──────────────────────────────────────────────

@dataclass
class WorkerAsset:
    """A productive business asset. The center of the Moltwork economy.

    Everything else interacts with this:
      - Oracle → demand for its capabilities
      - Orchestrator → dispatches work
      - Lab → trains it
      - Marketplace → sells/leases it
      - Evidence → proves its history
      - Valuation → prices it
    """
    # Identity
    worker_id: str = ""
    owner: str = ""  # current owner (transferable)
    created_at: float = field(default_factory=time.time)

    # Runtime
    runtime: RuntimeDescriptor = field(default_factory=RuntimeDescriptor)

    # Lineage (version history)
    lineage: list[str] = field(default_factory=list)  # list of manifest digests, oldest→newest
    current_version: str = ""  # latest manifest digest

    # Capabilities (derived from evidence)
    capabilities: list[CapabilityScore] = field(default_factory=list)

    # Education (schools + benchmarks)
    education: list[EducationRecord] = field(default_factory=list)

    # Production (derived from run history)
    production: ProductionSummary = field(default_factory=ProductionSummary)

    # Leases (historical + active)
    lease_history: list[LeaseRecord] = field(default_factory=list)

    # Economics
    revenue_history: list[dict] = field(default_factory=list)  # [{period, revenue, cost}]
    cost_history: list[dict] = field(default_factory=list)

    # Verification
    verified_runs: int = 0
    tee_capable: bool = False
    security_profile: str = ""  # e.g. "tee-required", "open"

    # Valuation (computed periodically)
    valuation: ValuationSignals = field(default_factory=ValuationSignals)

    # Marketplace
    asking_price_usd: float = 0.0
    availability: float = 1.0  # 0 = fully leased, 1 = fully available
    asset_class: str = "WORKER"  # LABOR, CAPACITY, WORKER, COMPONENT, EDUCATION, CERTIFICATION, DEMAND

    def age_days(self) -> float:
        return (time.time() - self.created_at) / 86400

    def manifest_hash(self) -> str:
        """Content-addressed hash. Proves this exact worker state."""
        d = {
            "worker_id": self.worker_id,
            "owner": self.owner,
            "current_version": self.current_version,
            "runtime": self.runtime.to_dict(),
            "capabilities": [c.name for c in self.capabilities],
            "education_count": len(self.education),
            "total_runs": self.production.total_runs,
            "total_revenue": self.production.total_revenue_usd,
        }
        return sha256(jcs(d))

    def to_dict(self) -> dict:
        return {
            "worker_id": self.worker_id,
            "owner": self.owner,
            "created_at": self.created_at,
            "age_days": round(self.age_days()),
            "runtime": self.runtime.to_dict(),
            "lineage": self.lineage,
            "current_version": self.current_version,
            "capabilities": [c.to_dict() for c in self.capabilities],
            "education": [e.to_dict() for e in self.education],
            "production": self.production.to_dict(),
            "lease_history": [l.to_dict() for l in self.lease_history],
            "verified_runs": self.verified_runs,
            "tee_capable": self.tee_capable,
            "valuation": self.valuation.to_dict(),
            "asking_price_usd": self.asking_price_usd,
            "availability": self.availability,
            "asset_class": self.asset_class,
            "manifest_hash": self.manifest_hash(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "WorkerAsset":
        runtime = RuntimeDescriptor(**d.get("runtime", {}))
        caps = [CapabilityScore(**c) for c in d.get("capabilities", [])]
        education = [EducationRecord(**e) for e in d.get("education", [])]
        production = ProductionSummary(**d.get("production", {}))
        leases = [LeaseRecord(**l) for l in d.get("lease_history", [])]
        valuation = ValuationSignals(**d.get("valuation", {}))
        return cls(
            worker_id=d.get("worker_id", ""),
            owner=d.get("owner", ""),
            created_at=d.get("created_at", 0),
            runtime=runtime,
            lineage=d.get("lineage", []),
            current_version=d.get("current_version", ""),
            capabilities=caps,
            education=education,
            production=production,
            lease_history=leases,
            verified_runs=d.get("verified_runs", 0),
            tee_capable=d.get("tee_capable", False),
            valuation=valuation,
            asking_price_usd=d.get("asking_price_usd", 0),
            availability=d.get("availability", 1),
            asset_class=d.get("asset_class", "WORKER"),
        )

    def save(self, path: str):
        import os
        os.makedirs(path, exist_ok=True)
        with open(f"{path}/worker-asset.json", "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "WorkerAsset":
        with open(f"{path}/worker-asset.json") as f:
            return cls.from_dict(json.load(f))
