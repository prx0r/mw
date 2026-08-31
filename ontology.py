"""Shared ontology — canonical types that cross the Oracle/WorkerKit boundary.

Oracle owns: market intelligence, opportunities, execution analysis
WorkerKit owns: execution records, receipts, capabilities, costs

These types are the ONLY bridge. Import from here, not from each other's internals.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict


# ─── Execution Steps (derived from Pack research) ─────────────────────

STAGES = [
    "discover",    # find the opportunity
    "qualify",     # evaluate fit
    "enter",       # account/identity setup
    "work",        # produce the artifact
    "submit",      # deliver to venue
    "evaluate",    # wait for judgment
    "settle",      # payment/settlement
    "outcome",     # final result
]

ACTORS = ["agent", "human", "hybrid"]

INTERFACES = [
    "api",          # official REST/GraphQL API
    "mcp",          # Model Context Protocol server
    "webmcp",       # browser-native MCP
    "browser",      # browser automation
    "cli",          # command-line tool
    "human_queue",  # RentAHuman or similar
    "manual",       # requires manual action
]

# Human dependency resolution ladder (highest → lowest preference)
RESOLUTION_LADDER = [
    "official_api",
    "official_openapi",
    "official_mcp",
    "official_webmcp",
    "approved_integration",
    "zapier_mcp",
    "community_mcp",
    "browser_automation",
    "human_queue",
]


@dataclass
class ExecutionStep:
    """One step in an opportunity's execution plan."""
    stage: str = ""
    action: str = ""
    actor: str = ""
    interface: str = ""
    credential_ref: str = ""
    human_dependency: str | None = None
    recurrence: str = ""        # once, per_run, per_account
    estimated_seconds: float = 0
    estimated_cost_usd: float = 0

    def to_dict(self): return asdict(self)


@dataclass
class HumanDependency:
    """A specific human-required step, with resolution options."""
    id: str = ""
    stage: str = ""
    recurrence: str = ""
    mandatory: bool = True
    delegatable: bool = False
    estimated_minutes: float = 0
    resolution_options: list[dict] = field(default_factory=list)

    def to_dict(self): return asdict(self)


@dataclass
class CredentialRef:
    """Reference to a credential. Never store secrets."""
    provider: str = ""      # arcade, composio, infisical, manual
    ref: str = ""
    scopes: list[str] = field(default_factory=list)
    auth_type: str = ""     # oauth, api_key, bearer
    human_initial_auth: bool = False

    def to_dict(self): return asdict(self)


# ─── Human Levels (derived from execution steps) ──────────────────────

HUMAN_LEVELS = {
    "H0": "Fully autonomous after secrets provisioned",
    "H1": "One-time human setup; thereafter autonomous",
    "H2": "Human approval required per opportunity",
    "H3": "Human contributes materially to deliverable",
    "H4": "Fundamentally human-only",
}


def derive_human_level(steps: list[ExecutionStep]) -> str:
    """Derive H0-H4 from execution steps."""
    human_steps = [s for s in steps if s.actor in ("human", "hybrid")]
    if not human_steps:
        return "H0"
    mandatory = [s for s in human_steps if s.human_dependency]
    if not mandatory:
        return "H0"
    once_only = all(s.recurrence == "once" for s in mandatory)
    if once_only:
        return "H1"
    if any(s.stage in ("work", "submit", "evaluate") for s in mandatory):
        return "H3"
    if any(s.stage in ("enter", "settle") for s in mandatory):
        return "H2"
    return "H2"
