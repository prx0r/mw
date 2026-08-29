"""Opportunity schema — normalized economic opportunity.

The Oracle discovers opportunities. This schema normalizes them
across venues (hackathons, gigs, bounties, products, content).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from core.hashing import sha256, jcs


class OpportunityKind(str, Enum):
    COMPETITION = "COMPETITION"
    GIG = "GIG"
    BOUNTY = "BOUNTY"
    PRODUCT = "PRODUCT"
    CONTENT = "CONTENT"
    SERVICE = "SERVICE"


class Domain(str, Enum):
    CODE = "CODE"
    RESEARCH = "RESEARCH"
    AUTOMATION = "AUTOMATION"
    GAME_DEV = "GAME_DEV"
    CONTENT = "CONTENT"
    ECOMMERCE = "ECOMMERCE"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    DATA = "DATA"
    DESIGN = "DESIGN"


class RewardModel(str, Enum):
    FIXED = "FIXED"
    BOUNTY = "BOUNTY"
    COMPETITION_PRIZE = "COMPETITION_PRIZE"
    PER_SALE = "PER_SALE"
    USAGE_BASED = "USAGE_BASED"
    SUBSCRIPTION = "SUBSCRIPTION"
    REV_SHARE = "REV_SHARE"
    AUDIENCE = "AUDIENCE"


class AcceptanceModel(str, Enum):
    AUTOMATED = "AUTOMATED"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    PEER_REVIEW = "PEER_REVIEW"
    OUTCOME_BASED = "OUTCOME_BASED"
    MIXED = "MIXED"


@dataclass
class OpportunityRoute:
    """One route into an opportunity (e.g., sponsor track)."""
    route_id: str = ""
    name: str = ""
    description: str = ""
    reward_usd: float = 0.0
    deadline: str = ""
    judging_criteria: list[str] = field(default_factory=list)
    eligibility: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "route_id": self.route_id,
            "name": self.name,
            "description": self.description,
            "reward_usd": self.reward_usd,
            "deadline": self.deadline,
            "judging_criteria": self.judging_criteria,
            "eligibility": self.eligibility,
            "required_capabilities": self.required_capabilities,
        }


@dataclass
class Opportunity:
    """Normalized economic opportunity discovered by Oracle."""
    id: str = ""
    source: str = ""  # hackathonhelp, oracle, manual
    external_id: str = ""
    url: str = ""

    kind: str = "BOUNTY"  # OpportunityKind
    domain: str = "CODE"  # Domain
    work_shapes: list[str] = field(default_factory=list)

    title: str = ""
    description: str = ""
    deadline: str = ""

    eligibility: list[str] = field(default_factory=list)
    venue_policy: list[str] = field(default_factory=list)

    reward_model: str = "FIXED"  # RewardModel
    reward_usd: float = 0.0
    reward_currency: str = "USD"

    acceptance_model: str = "HUMAN_REVIEW"  # AcceptanceModel
    judging_criteria: list[str] = field(default_factory=list)

    human_dependencies: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)

    routes: list[OpportunityRoute] = field(default_factory=list)

    source_evidence: dict = field(default_factory=dict)
    market_signals: dict = field(default_factory=dict)

    created_at: float = field(default_factory=time.time)

    def content_hash(self) -> str:
        d = {
            "source": self.source,
            "external_id": self.external_id,
            "kind": self.kind,
            "domain": self.domain,
            "title": self.title,
            "reward_usd": self.reward_usd,
            "deadline": self.deadline,
        }
        return sha256(jcs(d))

    def best_route(self) -> OpportunityRoute | None:
        if not self.routes:
            return None
        return max(self.routes, key=lambda r: r.reward_usd)

    def estimated_ev(self, win_probability: float = 0.1) -> float:
        best = self.best_route()
        if not best:
            return 0.0
        return best.reward_usd * win_probability

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source,
            "external_id": self.external_id,
            "url": self.url,
            "kind": self.kind,
            "domain": self.domain,
            "work_shapes": self.work_shapes,
            "title": self.title,
            "description": self.description[:200],
            "deadline": self.deadline,
            "reward_model": self.reward_model,
            "reward_usd": self.reward_usd,
            "acceptance_model": self.acceptance_model,
            "judging_criteria": self.judging_criteria,
            "routes": [r.to_dict() for r in self.routes],
            "required_capabilities": self.required_capabilities,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Opportunity":
        routes = [OpportunityRoute(**r) for r in d.get("routes", [])]
        return cls(
            id=d.get("id", ""),
            source=d.get("source", ""),
            external_id=d.get("external_id", ""),
            url=d.get("url", ""),
            kind=d.get("kind", "BOUNTY"),
            domain=d.get("domain", "CODE"),
            work_shapes=d.get("work_shapes", []),
            title=d.get("title", ""),
            description=d.get("description", ""),
            deadline=d.get("deadline", ""),
            reward_model=d.get("reward_model", "FIXED"),
            reward_usd=d.get("reward_usd", 0),
            acceptance_model=d.get("acceptance_model", "HUMAN_REVIEW"),
            judging_criteria=d.get("judging_criteria", []),
            routes=routes,
            required_capabilities=d.get("required_capabilities", []),
        )
