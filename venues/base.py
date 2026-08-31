"""WorkVenue — the abstraction for where work happens.

Every marketplace, bounty board, ACP network, or direct client
implements this interface. WorkerKit dispatches work through venues
without caring which one generated the demand.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Protocol, Any


@dataclass
class Opportunity:
    """A work opportunity from any venue."""
    id: str = ""
    venue: str = ""  # which venue this came from
    title: str = ""
    description: str = ""
    task_family: str = ""  # canonical task family
    capabilities: list[str] = field(default_factory=list)
    reward_usd: float = 0.0
    currency: str = "USD"
    deadline: str = ""
    status: str = "open"  # open, in_progress, closed
    evaluation_criteria: list[str] = field(default_factory=list)
    benchmarks_required: dict[str, float] = field(default_factory=dict)  # benchmark_id → min_score
    source_url: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "venue": self.venue, "title": self.title,
            "description": self.description[:200],
            "task_family": self.task_family, "capabilities": self.capabilities,
            "reward_usd": self.reward_usd, "currency": self.currency,
            "deadline": self.deadline, "status": self.status,
            "benchmarks_required": self.benchmarks_required,
            "source_url": self.source_url,
        }


@dataclass
class SubmissionRef:
    """Reference to a submitted piece of work."""
    submission_id: str = ""
    venue: str = ""
    opportunity_id: str = ""
    submitted_at: float = field(default_factory=time.time)
    artifact_hash: str = ""
    status: str = "submitted"  # submitted, accepted, rejected, paid

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class Outcome:
    """What happened after submission."""
    submission_id: str = ""
    status: str = ""  # won, lost, pending, partial
    score: float = 0.0
    feedback: str = ""
    payout_usd: float = 0.0
    settled: bool = False

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class Settlement:
    """Payment settlement."""
    submission_id: str = ""
    amount_usd: float = 0.0
    currency: str = "USD"
    tx_hash: str = ""
    settled_at: float = 0.0
    method: str = ""  # x402, erc8183, invoice, internal

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


class WorkVenue(Protocol):
    """Interface for any place work happens."""

    def discover(self) -> list[Opportunity]:
        """Find available work opportunities."""
        ...

    def inspect(self, opportunity_id: str) -> Opportunity | None:
        """Get details of one opportunity."""
        ...

    def submit(self, opportunity_id: str, artifact_hash: str = "",
               artifact_content: bytes = b"") -> SubmissionRef | None:
        """Submit work to an opportunity."""
        ...

    def status(self, submission_id: str) -> Outcome | None:
        """Check submission outcome."""
        ...

    def settle(self, submission_id: str) -> Settlement | None:
        """Settle payment for accepted work."""
        ...
