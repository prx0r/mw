"""WorkerAdapter — runtime-agnostic worker interface.

Moltwork agents are runtime-agnostic. Letta is the reference stateful runtime;
Agent File (.af) is the preferred portable state representation;
Agent Skills (SKILL.md) are the preferred portable capability representation;
dstack is the reference confidential execution environment.

This module defines the minimal interface every worker must implement.
Real adapters: Letta, OpenClaw, Hermes, OpenHands, custom.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Protocol, Any


@dataclass
class WorkerHealth:
    ok: bool = False
    runtime: str = ""
    version: str = ""
    detail: str = ""
    latency_ms: float = 0.0


@dataclass
class WorkerInspect:
    worker_id: str = ""
    runtime: str = ""
    model: str = ""
    memory_blocks: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    mcp_servers: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    state_hash: str = ""  # hash of current .af or equivalent


@dataclass
class RunContext:
    workspace: str = ""
    budget_remaining: float = 0.0
    timeout_seconds: int = 300
    authorize_callback: Any = None


@dataclass
class ExecutionResult:
    ok: bool = False
    output_content: str = ""
    output_hash: str = ""
    artifacts: list[str] = field(default_factory=list)
    cost_usd: float = 0.0
    duration_seconds: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0
    error: str = ""
    error_code: str = ""  # NO_RUNTIME, NOT_EXECUTED, FAIL, TIMEOUT
    metadata: dict = field(default_factory=dict)
    trace_events: list[dict] = field(default_factory=list)


class WorkerAdapter(Protocol):
    """Minimal interface every Moltwork worker must implement."""

    @property
    def runtime(self) -> str: ...

    async def inspect(self) -> WorkerInspect: ...

    async def execute(self, work_order: Any, context: RunContext) -> ExecutionResult: ...

    async def cancel(self, run_id: str) -> bool: ...

    async def export_state(self, dest: str) -> str: ...  # returns path or .af content hash

    async def health(self) -> WorkerHealth: ...
