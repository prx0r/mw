"""ExecutionAdapter — protocol for arbitrary workers.

WorkerKit doesn't care how the work happens.
It only cares about: input → output → cost → evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Any


@dataclass
class RunContext:
    """What the worker can access."""
    workspace: str = ""
    budget_remaining: float = 0.0
    timeout_seconds: int = 300
    authorize_callback: Any = None  # async callable for expensive actions


@dataclass
class ExecutionResult:
    """What the worker produced."""
    ok: bool = False
    output_content: str = ""
    output_hash: str = ""
    artifacts: list[str] = field(default_factory=list)
    cost_usd: float = 0.0
    duration_seconds: float = 0.0
    error: str = ""
    metadata: dict = field(default_factory=dict)


class WorkerAdapter(Protocol):
    """Protocol for arbitrary worker adapters."""

    async def execute(self, work_order: Any, context: RunContext) -> ExecutionResult:
        """Execute the work and return results."""
        ...
