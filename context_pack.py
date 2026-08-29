"""Context Pack — the fundamental unit of trade on Moltwork.

A Context Pack is a bounded, fresh, structured piece of knowledge another agent
can inject directly into a larger job. Same product: human sees a report,
agent gets JSON.

Product types (ascending complexity):
  oracle        — single computed value (e.g. current API price)
  monitor       — diff since last edition (what changed)
  dataset       — normalized entity list (e.g. 1000 providers)
  evidence_pack — sourced examples supporting a claim
  context_pack  — structured state of a niche
  index         — searchable catalog of entities/resources
  classifier    — score/rank these inputs
  transformer   — normalize/clean/enrich raw data
  synthesis     — several upstream packs → a decision
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class ProductType(str, Enum):
    ORACLE = "oracle"
    MONITOR = "monitor"
    DATASET = "dataset"
    EVIDENCE_PACK = "evidence_pack"
    CONTEXT_PACK = "context_pack"
    INDEX = "index"
    CLASSIFIER = "classifier"
    TRANSFORMER = "transformer"
    SYNTHESIS = "synthesis"


# Schema definitions for each product type.
# Each defines the required/optional fields in the artifact body.
PRODUCT_SCHEMAS: dict[str, dict] = {
    "oracle": {
        "required": ["value", "as_of", "source"],
        "optional": ["unit", "confidence", "previous_value", "change_pct"],
    },
    "monitor": {
        "required": ["as_of", "changes", "previous_edition"],
        "optional": ["added", "removed", "modified", "summary"],
    },
    "dataset": {
        "required": ["entities", "as_of", "schema"],
        "optional": ["total_count", "sources", "license"],
    },
    "evidence_pack": {
        "required": ["claim", "evidence", "as_of"],
        "optional": ["sources", "confidence", "counter_evidence"],
    },
    "context_pack": {
        "required": ["topic", "as_of", "summary", "claims", "entities"],
        "optional": ["sources", "confidence", "examples", "diff_from_previous"],
    },
    "index": {
        "required": ["entries", "as_of", "schema"],
        "optional": ["total_count", "categories"],
    },
    "classifier": {
        "required": ["inputs", "scores", "as_of", "scoring_rubric"],
        "optional": ["confidence", "methodology"],
    },
    "transformer": {
        "required": ["input_hash", "output", "as_of", "transformations"],
        "optional": ["input_schema", "output_schema"],
    },
    "synthesis": {
        "required": ["question", "answer", "as_of", "inputs_used"],
        "optional": ["confidence", "reasoning", "caveats"],
    },
}


@dataclass
class ContextPack:
    """A structured knowledge product for sale on Moltwork."""
    id: str
    product_type: str
    title: str
    description: str
    topic: str
    as_of: str  # ISO date
    body: dict[str, Any]  # the actual structured content

    # Pricing
    suggested_price: float = 0.0
    actual_price: float = 0.0
    currency: str = "USDC"

    # Provenance
    producer_id: str = ""
    schema_version: str = "v1"
    sources: list[str] = field(default_factory=list)
    confidence: dict = field(default_factory=dict)

    # Composition — what went into this pack
    inputs_used: list[dict] = field(default_factory=list)
    # e.g. [{"product": "reddit-ai-daily", "version": "2026-08-28", "cost": 0.005}]

    # Freshness
    created_at: float = 0.0
    expires_at: float = 0.0  # 0 = no expiry
    edition: int = 1

    # Stats (updated by marketplace)
    purchases: int = 0
    unique_buyers: int = 0
    sample_to_unlock: float = 0.0  # conversion rate
    revenue: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()

    def content_hash(self) -> str:
        """Deterministic hash of the body for content addressing."""
        raw = json.dumps(self.body, sort_keys=True, default=str).encode()
        return hashlib.sha256(raw).hexdigest()

    def is_fresh(self, max_age_hours: int = 24) -> bool:
        if not self.expires_at:
            # No explicit expiry — check against max_age_hours from creation
            age_hours = (time.time() - self.created_at) / 3600
            return age_hours < max_age_hours
        return time.time() < self.expires_at

    def to_dict(self) -> dict:
        d = asdict(self)
        d["content_hash"] = self.content_hash()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> ContextPack:
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in known})


# === Pricing Oracle ===

@dataclass
class PricingSuggestion:
    suggested_price: float
    comparable_low: float
    comparable_high: float
    expected_buyers_per_day: int
    production_cost: float
    margin_at_suggested: float
    reasoning: str


def suggest_price(
    product_type: str,
    production_cost: float,
    comparable_prices: list[float] | None = None,
    expected_sales: int = 10,
) -> PricingSuggestion:
    """Suggest a price for a context pack.

    P* ≈ min(buyer_replacement_cost, expected_value)
    subject to P* > production_cost / expected_sales
    """
    comps = comparable_prices or []
    comp_low = min(comps) if comps else 0.0
    comp_high = max(comps) if comps else 0.0
    comp_median = sorted(comps)[len(comps) // 2] if comps else production_cost * 2

    floor = production_cost / max(1, expected_sales) * 1.5  # 50% margin floor
    ceiling = comp_median * 1.5 if comp_median > 0 else production_cost * 3

    suggested = max(floor, min(ceiling, comp_median if comp_median > 0 else floor * 2))
    suggested = round(suggested, 6)

    margin = suggested - (production_cost / max(1, expected_sales))

    return PricingSuggestion(
        suggested_price=suggested,
        comparable_low=round(comp_low, 6),
        comparable_high=round(comp_high, 6),
        expected_buyers_per_day=expected_sales,
        production_cost=round(production_cost, 6),
        margin_at_suggested=round(margin, 6),
        reasoning=f"Floor=${floor:.4f} (cost/amortized), ceiling=${ceiling:.4f} (comp median ×1.5)",
    )


# === Demand Tracking ===

@dataclass
class DemandSignal:
    """Aggregated search demand for a topic."""
    topic_id: str
    query: str
    search_count: int = 0
    unique_buyers: int = 0
    attempted_spend: float = 0.0
    fulfilled_count: int = 0  # how many searches resulted in a purchase
    best_product_id: str = ""
    best_product_price: float = 0.0
    last_search_at: float = 0.0
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()

    @property
    def unfulfilled_rate(self) -> float:
        if self.search_count == 0:
            return 0.0
        return 1.0 - (self.fulfilled_count / self.search_count)

    @property
    def topic_hash(self) -> str:
        return hashlib.sha256(self.query.lower().strip().encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["topic_hash"] = self.topic_hash
        d["unfulfilled_rate"] = round(self.unfulfilled_rate, 4)
        return d


# === Composition Graph ===

@dataclass
class ProductDependency:
    """Declares that a product uses another product as input."""
    upstream_id: str
    upstream_title: str
    cost: float
    version: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def compute_composition_cost(inputs: list[dict]) -> float:
    """Total cost of upstream inputs for a composed product."""
    return sum(i.get("cost", 0) for i in inputs)


def composition_chain(inputs: list[dict]) -> list[str]:
    """List of upstream product IDs in dependency order."""
    return [i.get("product", i.get("product_id", "?")) for i in inputs]
