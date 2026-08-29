"""Canonical Moltwork Taxonomy — the shared ontology.

Every Oracle opportunity, WorkerKit WorkOrder, RunReceipt, Lab query,
School exercise, and Marketplace asset uses exactly these classifications.

This is the data moat. Once taxonomy survives unchanged across the entire
pipeline, every new Run becomes comparable to every previous Run.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


TAXONOMY_VERSION = "mw-taxonomy-v1"


# ─── Enums ────────────────────────────────────────────────────────────

class AutonomyLevel(str, Enum):
    """Human involvement axis — NOT the task category."""
    H0 = "H0"  # Fully autonomous, deterministic/machine-verifiable
    H1 = "H1"  # Mostly autonomous, bounded ambiguity, light human escalation
    H2 = "H2"  # Human-in-the-loop, substantive judgment/review required
    H3 = "H3"  # Human-led work with AI assistance
    H4 = "H4"  # Primarily human, currently not practically automatable


class EconomicSurface(str, Enum):
    """How money flows for this work."""
    BOUNTY = "BOUNTY"  # Fixed reward for completion
    SUBSCRIPTION = "SUBSCRIPTION"  # Recurring payment
    USAGE = "USAGE"  # Pay-per-use / micropayments
    MARKETPLACE = "MARKETPLACE"  # Listing + purchase
    SALARY = "SALARY"  # Time-based compensation
    LICENSE = "LICENSE"  # Usage rights fee
    SPONSORSHIP = "SPONSORSHIP"  # Grant / sponsorship
    AD_REVENUE = "AD_REVENUE"  # Advertising revenue share
    AFFILIATE = "AFFILIATE"  # Commission on referrals
    FREE = "FREE"  # No direct payment


class RevenueModel(str, Enum):
    """How the Worker earns."""
    FIXED_REWARD = "FIXED_REWARD"  # Set amount on success
    TIERED = "TIERED"  # Amount depends on quality tier
    BIDDING = "BIDDING"  # Worker sets price
    AUCTION = "AUCTION"  # Competitive pricing
    SUBSCRIPTION = "SUBSCRIPTION"  # Recurring for ongoing work
    ROYALTY = "ROYALTY"  # Percentage of downstream revenue
    HYBRID = "HYBRID"  # Combination of above


class EvaluationMode(str, Enum):
    """How quality is assessed."""
    DETERMINISTIC = "DETERMINISTIC"  # Automated checks (tests, linting, etc.)
    MACHINE_LEARNING = "MACHINE_LEARNING"  # Model-based scoring
    HUMAN_REVIEW = "HUMAN_REVIEW"  # Human evaluator
    PEER_REVIEW = "PEER_REVIEW"  # Peer evaluation
    EXTERNAL_OUTCOME = "EXTERNAL_OUTCOME"  # Real-world result
    COMPOSITE = "COMPOSITE"  # Combination of above
    REQUIREMENTS_CHECK = "REQUIREMENTS_CHECK"  # Constraint satisfaction
    SUBJECTIVE_REVIEW = "SUBJECTIVE_REVIEW"  # Qualitative assessment


# ─── Canonical task families ──────────────────────────────────────────

# Pre-defined task family paths. Oracle and School use these exact strings.
TASK_FAMILIES = {
    "research.ideation.technical": {
        "description": "Generate technical product/solution ideas",
        "typical_autonomy": "H1",
        "typical_capabilities": ["technical-research", "divergent-ideation", "novelty-ranking"],
    },
    "research.ideation.business": {
        "description": "Generate business/product ideas",
        "typical_autonomy": "H1",
        "typical_capabilities": ["market-research", "divergent-ideation", "business-analysis"],
    },
    "research.analysis.api": {
        "description": "Analyze APIs, documentation, and technical specs",
        "typical_autonomy": "H0",
        "typical_capabilities": ["api-research", "technical-writing", "comparison"],
    },
    "research.analysis.market": {
        "description": "Market research, competitive analysis",
        "typical_autonomy": "H1",
        "typical_capabilities": ["market-research", "data-analysis", "report-writing"],
    },
    "software.api.integration": {
        "description": "Integrate with external APIs",
        "typical_autonomy": "H0",
        "typical_capabilities": ["api-implementation", "debugging", "documentation"],
    },
    "software.api.debugging": {
        "description": "Debug API issues",
        "typical_autonomy": "H0",
        "typical_capabilities": ["debugging", "error-analysis", "fix-implementation"],
    },
    "software.documentation": {
        "description": "Write technical documentation",
        "typical_autonomy": "H1",
        "typical_capabilities": ["technical-writing", "api-documentation", "tutorial-creation"],
    },
    "content.video.shortform": {
        "description": "Produce short-form video content",
        "typical_autonomy": "H2",
        "typical_capabilities": ["video-editing", "script-writing", "audience-analysis"],
    },
    "content.writing.blog": {
        "description": "Write blog posts and articles",
        "typical_autonomy": "H1",
        "typical_capabilities": ["writing", "research", "seo-optimization"],
    },
    "design.ui prototypes": {
        "description": "Design UI prototypes and mockups",
        "typical_autonomy": "H2",
        "typical_capabilities": ["ui-design", "user-research", "prototyping"],
    },
    "data.analysis.reports": {
        "description": "Analyze data and produce reports",
        "typical_autonomy": "H1",
        "typical_capabilities": ["data-analysis", "visualization", "report-writing"],
    },
    "hackathon.technical-submission": {
        "description": "Build hackathon project submission",
        "typical_autonomy": "H1",
        "typical_capabilities": ["implementation", "demo-creation", "pitch-writing"],
    },
}


# ─── Canonical capabilities ───────────────────────────────────────────

CAPABILITIES = {
    "technical-research": "Research technical topics and produce findings",
    "divergent-ideation": "Generate many diverse ideas for a given prompt",
    "novelty-ranking": "Rank ideas by novelty and differentiation",
    "requirements-analysis": "Extract and verify requirements from specifications",
    "market-research": "Research market conditions, competitors, opportunities",
    "data-analysis": "Analyze structured data and derive insights",
    "business-analysis": "Analyze business models, revenue, costs",
    "api-research": "Research APIs, documentation, and integration options",
    "api-implementation": "Implement API integrations",
    "debugging": "Identify and fix software bugs",
    "error-analysis": "Analyze error patterns and root causes",
    "fix-implementation": "Implement bug fixes",
    "technical-writing": "Write clear technical content",
    "api-documentation": "Document APIs and developer tools",
    "tutorial-creation": "Create step-by-step tutorials",
    "writing": "General writing and composition",
    "seo-optimization": "Optimize content for search engines",
    "video-editing": "Edit and produce video content",
    "script-writing": "Write video/audio scripts",
    "audience-analysis": "Analyze audience preferences and behavior",
    "ui-design": "Design user interfaces",
    "user-research": "Research user needs and behaviors",
    "prototyping": "Create interactive prototypes",
    "visualization": "Create data visualizations",
    "report-writing": "Write structured analytical reports",
    "implementation": "Build software features",
    "demo-creation": "Create product demonstrations",
    "pitch-writing": "Write compelling pitches and presentations",
    "comparison": "Compare options and produce structured comparisons",
    "coding": "Write production-quality code",
    "testing": "Write and run tests",
    "review": "Review code, content, or other artifacts",
}


# ─── Canonical evaluation modes ───────────────────────────────────────

EVALUATION_MODES = {
    "DETERMINISTIC": "Automated checks (tests, linting, constraint satisfaction)",
    "MACHINE_LEARNING": "Model-based scoring and evaluation",
    "HUMAN_REVIEW": "Human evaluator assessment",
    "PEER_REVIEW": "Peer evaluation and feedback",
    "EXTERNAL_OUTCOME": "Real-world result measurement",
    "REQUIREMENTS_CHECK": "Explicit constraint verification",
    "SUBJECTIVE_REVIEW": "Qualitative assessment of quality",
}


# ─── The canonical classification object ──────────────────────────────

@dataclass
class Taxonomy:
    """Canonical Moltwork classification. Carried unchanged from Oracle through entire pipeline."""
    taxonomy_version: str = TAXONOMY_VERSION
    task_family_id: str = ""
    task_family_path: list[str] = field(default_factory=list)
    economic_surface: str = "BOUNTY"
    autonomy_level: str = "H1"
    capabilities: list[str] = field(default_factory=list)
    evaluation_modes: list[str] = field(default_factory=list)
    revenue_model: str = "FIXED_REWARD"

    def __post_init__(self):
        if self.task_family_id and not self.task_family_path:
            self.task_family_path = self.task_family_id.split(".")
        if not self.task_family_id and self.task_family_path:
            self.task_family_id = ".".join(self.task_family_path)

    def to_dict(self) -> dict:
        return {
            "taxonomy_version": self.taxonomy_version,
            "task_family_id": self.task_family_id,
            "task_family_path": self.task_family_path,
            "economic_surface": self.economic_surface,
            "autonomy_level": self.autonomy_level,
            "capabilities": self.capabilities,
            "evaluation_modes": self.evaluation_modes,
            "revenue_model": self.revenue_model,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Taxonomy":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in known})

    def content_hash(self) -> str:
        """Deterministic hash of the taxonomy. Used for RunCommitment."""
        return hashlib.sha256(
            json.dumps(self.to_dict(), sort_keys=True).encode()
        ).hexdigest()

    def matches(self, other: "Taxonomy") -> bool:
        """Check if two taxonomies are compatible for comparison."""
        return self.task_family_id == other.task_family_id

    @classmethod
    def from_task_family(cls, task_family_id: str) -> "Taxonomy":
        """Create taxonomy from a known task family."""
        info = TASK_FAMILIES.get(task_family_id, {})
        return cls(
            task_family_id=task_family_id,
            task_family_path=task_family_id.split("."),
            autonomy_level=info.get("typical_autonomy", "H1"),
            capabilities=info.get("typical_capabilities", []),
            evaluation_modes=["REQUIREMENTS_CHECK", "SUBJECTIVE_REVIEW"],
            revenue_model="FIXED_REWARD",
        )
