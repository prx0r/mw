from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Literal

Recurrence = Literal["per_run", "once", "occasional", "never"]
Actor = Literal["agent", "human", "service"]


@dataclass(frozen=True)
class HumanDependency:
    id: str
    reason: str = ""
    recurrence: Recurrence = "per_run"
    delegatable: bool = False
    estimated_minutes: float = 0.0
    mandatory: bool = True


@dataclass(frozen=True)
class ExecutionStep:
    stage: str
    action: str
    actor: Actor
    interface: str = ""
    human_dependency: HumanDependency | None = None
    credential_ref: str = ""
    policy_notes: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def derive_autonomy_level(steps: list[ExecutionStep]) -> str:
    """Derive the existing Moltwork H0-H4 axis; no second taxonomy.

    H0: no mandatory human step per normal run (one-time provisioning allowed)
    H1: occasional/bounded human action or one-time setup only
    H2: substantive human action on normal runs
    H3: humans perform a large fraction of execution
    H4: task is fundamentally human/physical in its core action
    """
    if not steps:
        return "H1"
    human = [s for s in steps if s.actor == "human" or s.human_dependency]
    if not human:
        return "H0"
    per_run = [s for s in human if s.human_dependency and s.human_dependency.recurrence == "per_run" and s.human_dependency.mandatory]
    one_time = [s for s in human if s.human_dependency and s.human_dependency.recurrence in {"once", "occasional"}]
    physical_core = any((s.human_dependency and "physical" in s.human_dependency.id) for s in human)
    if physical_core and len(human) >= max(1, len(steps) // 2):
        return "H4"
    # H3 means the human is the primary task performer, not merely that a
    # workflow contains setup/approval steps. Count normal per-run execution
    # separately from one-time provisioning.
    recurring_human_actor = [
        s for s in steps
        if s.actor == "human" and (
            s.human_dependency is None
            or s.human_dependency.recurrence == "per_run"
        )
    ]
    if len(recurring_human_actor) / len(steps) >= 0.5:
        return "H3"
    if per_run:
        return "H2"
    if one_time or human:
        return "H1"
    return "H0"


AUTOMATION_PRIORITY = (
    "official_api", "official_openapi", "official_mcp", "official_webmcp",
    "approved_integration", "zapier_mcp", "community_mcp", "browser", "human_queue",
)


@dataclass(frozen=True)
class AutomationCandidate:
    dependency_id: str
    method: str
    provider: str
    policy_compliant: bool
    confidence: float
    notes: str = ""


def choose_automation(candidates: list[AutomationCandidate]) -> AutomationCandidate | None:
    valid = [c for c in candidates if c.policy_compliant]
    if not valid:
        return None
    priority = {name: i for i, name in enumerate(AUTOMATION_PRIORITY)}
    return min(valid, key=lambda c: (priority.get(c.method, 999), -c.confidence))
