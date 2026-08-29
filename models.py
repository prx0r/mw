"""Oracle data models — 12 core entities + relationships.

From backendbuild.md:
1. Source
2. Market
3. Actor
4. Capability
5. Opportunity
6. Service
7. IncentiveMarket
8. Observation
9. Submission
10. Outcome
11. Payment
12. Prediction
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


# === 12 Core Entities ===

@dataclass
class Source:
    """Where data comes from."""
    id: str = ""
    name: str = ""
    type: str = ""  # api, chain, marketplace, manual
    url: str = ""
    auth_type: str = ""
    agent_native: bool = False
    extra: dict = field(default_factory=dict)

    def to_dict(self): return asdict(self)


@dataclass
class Market:
    """A marketplace or venue."""
    id: str = ""
    name: str = ""
    market_type: str = ""  # bounty, service, incentive, compute, agent_market
    chain: str = ""
    url: str = ""
    agent_native: bool = False
    auth_type: str = ""
    submission_method: str = ""
    extra: dict = field(default_factory=dict)

    def to_dict(self): return asdict(self)


@dataclass
class Actor:
    """An agent, worker, buyer, or participant."""
    id: str = ""
    name: str = ""
    actor_type: str = ""  # agent, worker, buyer, seller, validator, miner
    network: str = ""
    wallet: str = ""
    capabilities: list[str] = field(default_factory=list)
    reputation: float = 0
    extra: dict = field(default_factory=dict)

    def to_dict(self): return asdict(self)


@dataclass
class Capability:
    """A skill, tool, or capability."""
    id: str = ""
    slug: str = ""
    name: str = ""
    parent_id: str = ""
    description: str = ""
    extra: dict = field(default_factory=dict)

    def to_dict(self): return asdict(self)


@dataclass
class Opportunity:
    """A work opportunity."""
    id: str = ""
    source_id: str = ""
    market_id: str = ""
    external_id: str = ""
    kind: str = ""  # bounty, job, competition, request, subnet, paid_api
    title: str = ""
    description: str = ""
    status: str = ""  # open, claimed, completed, expired
    reward_model: str = ""
    reward_asset: str = ""
    reward_usd: float = 0
    created_at: str = ""
    deadline_at: str = ""
    closed_at: str = ""
    competition_count: int = 0
    human_level: str = "H0"
    capital_required_usd: float = 0
    raw_latest: dict = field(default_factory=dict)
    first_seen_at: str = ""
    last_seen_at: str = ""
    extra: dict = field(default_factory=dict)

    def to_dict(self): return asdict(self)


@dataclass
class Service:
    """A tool/API/capability for sale."""
    id: str = ""
    name: str = ""
    description: str = ""
    category: str = ""
    price_per_call: float = 0
    currency: str = "USDC"
    platform: str = ""
    uptime: float = 0
    rating: float = 0
    total_calls: int = 0
    extra: dict = field(default_factory=dict)

    def to_dict(self): return asdict(self)


@dataclass
class IncentiveMarket:
    """Bittensor subnet or similar."""
    id: str = ""
    name: str = ""
    network: str = ""
    category: str = ""
    emission_pct: float = 0
    daily_reward_usd: float = 0
    miners: int = 0
    validators: int = 0
    extra: dict = field(default_factory=dict)

    def to_dict(self): return asdict(self)


@dataclass
class Observation:
    """Immutable raw observation."""
    id: str = ""
    source_id: str = ""
    entity_type: str = ""
    entity_external_id: str = ""
    observed_at: str = ""
    schema_version: str = ""
    payload: dict = field(default_factory=dict)
    raw_hash: str = ""
    collector_version: str = ""

    def to_dict(self): return asdict(self)


@dataclass
class Submission:
    """An attempt to do work."""
    id: str = ""
    agent_id: str = ""
    opportunity_id: str = ""
    recipe_id: str = ""
    started_at: str = ""
    submitted_at: str = ""
    compute_cost_usd: float = 0
    api_cost_usd: float = 0
    human_minutes: float = 0
    artifact_hash: str = ""
    judge_score: float = 0
    extra: dict = field(default_factory=dict)

    def to_dict(self): return asdict(self)


@dataclass
class Outcome:
    """What actually happened."""
    submission_id: str = ""
    status: str = ""  # won, accepted, rejected, pending
    rank: int = 0
    gross_payout_usd: float = 0
    net_payout_usd: float = 0
    feedback: str = ""
    settled_at: str = ""
    extra: dict = field(default_factory=dict)

    def to_dict(self): return asdict(self)


@dataclass
class Payment:
    """A payment event."""
    id: str = ""
    payer_id: str = ""
    payee_id: str = ""
    amount: float = 0
    currency: str = "USD"
    tx_hash: str = ""
    chain: str = ""
    status: str = ""
    observed_at: str = ""
    extra: dict = field(default_factory=dict)

    def to_dict(self): return asdict(self)


@dataclass
class Prediction:
    """Derived prediction about an opportunity."""
    opportunity_id: str = ""
    worker_id: str = ""
    model_version: str = ""
    computed_at: str = ""
    p_entry: float = 0
    p_award: float = 0
    p_accept: float = 0
    estimated_cost_usd: float = 0
    expected_payout_usd: float = 0
    expected_net_usd: float = 0
    confidence_low: float = 0
    confidence_high: float = 0
    features: dict = field(default_factory=dict)

    def to_dict(self): return asdict(self)


# === WorkReceiptRef (bridge to WorkerKit) ===

@dataclass
class WorkReceiptRef:
    """Reference to a WorkerKit receipt."""
    opportunity_id: str = ""
    worker_id: str = ""
    receipt_digest: str = ""
    settlement_amount: float = 0
    settlement_currency: str = "USD"
    observed_at: str = ""
    extra: dict = field(default_factory=dict)

    def to_dict(self): return asdict(self)


# === H0-H4 Human Intervention ===

HUMAN_LEVELS = {
    "H0": "Fully autonomous after secrets provisioned",
    "H1": "One-time human setup; thereafter autonomous",
    "H2": "Human approval required per opportunity",
    "H3": "Human contributes materially to deliverable",
    "H4": "Fundamentally human-only",
}
