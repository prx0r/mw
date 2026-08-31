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
    """A work opportunity — canonical from Oracle through entire pipeline."""
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

    # Taxonomy (carried from Oracle through entire pipeline)
    task_family: str = ""           # e.g. "competition.technical_submission"
    capabilities: list[str] = field(default_factory=list)
    economic_surface: str = ""      # bounty, service, api, subnet
    evaluation_modes: list[str] = field(default_factory=list)
    human_level: str = "H0"         # H0-H4 autonomy axis

    # Execution analysis (from Pack research)
    execution_steps: list[dict] = field(default_factory=list)
    human_dependencies: list[dict] = field(default_factory=list)
    eligibility: dict = field(default_factory=dict)
    venue_policy: dict = field(default_factory=dict)

    # Evidence
    source_evidence: list[dict] = field(default_factory=list)
    market_signals: dict = field(default_factory=dict)
    requirements: list[str] = field(default_factory=list)

    capital_required_usd: float = 0
    raw_latest: dict = field(default_factory=dict)
    first_seen_at: str = ""
    last_seen_at: str = ""
    extra: dict = field(default_factory=dict)

    def to_dict(self): return asdict(self)


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


# === Execution Step (from Pack research) ===

@dataclass
class ExecutionStep:
    """One step in an opportunity's execution plan."""
    stage: str = ""         # discover, qualify, enter, work, submit, evaluate, settle, outcome
    action: str = ""
    actor: str = ""         # agent, human, hybrid
    interface: str = ""     # api, mcp, webmcp, browser, human_queue, cli
    credential_ref: str = ""
    human_dependency: str = None
    recurrence: str = ""    # once, per_run, per_account
    estimated_seconds: float = 0
    estimated_cost_usd: float = 0

    def to_dict(self): return asdict(self)


# === Human Dependency (structured, normalized IDs) ===

@dataclass
class HumanDependency:
    """A specific human-required step, with resolution options."""
    id: str = ""            # human.account_create, human.oauth_consent, etc.
    stage: str = ""
    recurrence: str = ""    # once, per_account, per_run
    mandatory: bool = True
    delegatable: bool = False
    estimated_minutes: float = 0
    resolution_options: list[dict] = field(default_factory=list)

    def to_dict(self): return asdict(self)


# === Credential Reference (never store secrets, only refs) ===

@dataclass
class CredentialRef:
    """Reference to a credential managed by Arcade/Composio/Infisical."""
    provider: str = ""      # arcade, composio, infisical, manual
    ref: str = ""           # stable name like "roblox-main"
    scopes: list[str] = field(default_factory=list)
    auth_type: str = ""     # oauth, api_key, bearer
    human_initial_auth: bool = False

    def to_dict(self): return asdict(self)


# === Canonical shared types (Oracle ↔ WorkerKit bridge) ===

# These are the ONLY types that cross the Oracle/WorkerKit boundary.
# WorkerKit owns execution records; Oracle owns market intelligence.

# Oracle -> WorkerKit:
#   Opportunity (with taxonomy, execution_steps, requirements)
#   CredentialRef
#
# WorkerKit -> Oracle:
#   WorkReceiptRef (receipt digest, cost, outcome)
#   CapabilityEvidence (what the worker can do)

# Human dependency resolution ladder:
# 1. Official API
# 2. Official OpenAPI
# 3. Official MCP
# 4. Official WebMCP
# 5. Existing approved integration
# 6. Zapier MCP
# 7. Community MCP
# 8. Compliant browser automation
# 9. Human Queue (RentAHuman)
