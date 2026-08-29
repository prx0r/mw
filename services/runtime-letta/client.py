"""Letta Runtime Service client — talks to services/runtime-letta/.

Uses the new Letta Agent SDK (local backend).
Owns: Worker ID ↔ Letta Agent ID mapping (never "list and pick first")
Each WorkOrder → new Letta session (don't reuse conversations)
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from workerkit.adapters.base import WorkerAdapter, WorkerInspect, WorkerHealth, RunContext, ExecutionResult
from workerkit.evidence.canonical import sha256 as wk_sha256


class LettaRuntimeClient:
    """Client for the runtime-letta TypeScript service.

    Uses Letta Agent SDK with local backend.
    Owns: Worker ID ↔ Letta Agent ID mapping.
    """

    def __init__(self, service_url: str = "http://localhost:3000"):
        self.service_url = service_url.rstrip("/")

    async def create_worker(self, worker_id: str, model: str = "",
                            persona: str = "", skills: list[str] | None = None) -> dict:
        """Create a worker mapping in the service."""
        import httpx
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                f"{self.service_url}/workers",
                json={"worker_id": worker_id, "model": model,
                      "persona": persona, "skills": skills or []},
            )
            r.raise_for_status()
            return r.json()

    async def get_worker(self, worker_id: str) -> dict | None:
        """Get worker mapping from the service."""
        import httpx
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{self.service_url}/workers/{worker_id}")
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json()

    async def execute(self, worker_id: str, task: str, workspace: str = "/tmp/moltwork-run",
                      budget: float = 4.0, timeout: int = 300,
                      allowed_tools: list[str] | None = None) -> dict:
        """Execute a task via the service. Creates a new Letta session."""
        import httpx
        async with httpx.AsyncClient(timeout=timeout + 10) as c:
            r = await c.post(
                f"{self.service_url}/workers/{worker_id}/run",
                json={"task": task, "workspace": workspace, "budget": budget,
                      "timeout": timeout, "allowedTools": allowed_tools},
            )
            r.raise_for_status()
            return r.json()

    async def recall(self, worker_id: str, query: str) -> dict:
        """Search previous conversations via agent recall."""
        import httpx
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                f"{self.service_url}/workers/{worker_id}/recall",
                json={"query": query},
            )
            r.raise_for_status()
            return r.json()

    async def list_memfs(self, worker_id: str) -> dict:
        """List MemFS memory files for a worker."""
        import httpx
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{self.service_url}/workers/{worker_id}/memfs")
            r.raise_for_status()
            return r.json()

    async def apply_learning(self, worker_id: str, patch_type: str,
                             label: str, content: str) -> dict:
        """Apply a memory or skill patch to the worker."""
        import httpx
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                f"{self.service_url}/workers/{worker_id}/learning",
                json={"patch_type": patch_type, "label": label, "content": content},
            )
            r.raise_for_status()
            return r.json()

    async def get_trajectory(self, worker_id: str, conversation_id: str = "") -> dict:
        """Get trajectory for a worker or specific conversation."""
        import httpx
        params = {}
        if conversation_id:
            params["conversation_id"] = conversation_id
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(
                f"{self.service_url}/workers/{worker_id}/trajectory",
                params=params,
            )
            r.raise_for_status()
            return r.json()

    async def health(self) -> dict:
        """Check service health."""
        import httpx
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{self.service_url}/health")
            return r.json()


class LettaServiceAdapter:
    """WorkerAdapter backed by the runtime-letta TypeScript service.

    Uses Letta Agent SDK with local backend.
    Each run creates a new Letta session (don't reuse conversations).
    Worker learning lives in MemFS (git-backed memory).
    """

    runtime = "letta-service"

    def __init__(self, service_url: str = "", worker_id: str = ""):
        self.service_url = service_url or "http://localhost:3000"
        self.worker_id = worker_id
        self._client = LettaRuntimeClient(self.service_url)

    async def inspect(self) -> WorkerInspect:
        if not self.worker_id:
            return WorkerInspect(worker_id="", runtime=self.runtime, state_hash="")
        worker = await self._client.get_worker(self.worker_id)
        if not worker:
            return WorkerInspect(worker_id=self.worker_id, runtime=self.runtime, state_hash="")
        return WorkerInspect(
            worker_id=self.worker_id,
            runtime=self.runtime,
            model=worker.get("model", ""),
            state_hash=worker.get("letta_agent_id", ""),
            tools=[],
            memory_blocks=[],
        )

    async def execute(self, work_order: Any, context: RunContext) -> ExecutionResult:
        t0 = time.time()
        title = getattr(work_order, "title", "") or (work_order.get("title", "") if isinstance(work_order, dict) else str(work_order)[:80])
        desc = getattr(work_order, "description", "") or (work_order.get("description", "") if isinstance(work_order, dict) else "")
        task = f"Task: {title}\n\n{desc}\n\nWorkspace: {context.workspace}\nBudget: ${context.budget_remaining:.2f}"

        try:
            result = await self._client.execute(
                self.worker_id, task,
                workspace=context.workspace,
                budget=context.budget_remaining,
                timeout=context.timeout_seconds,
            )
        except Exception as e:
            return ExecutionResult(ok=False, error=str(e), error_code="FAIL", duration_seconds=time.time() - t0)

        if not result.get("ok"):
            return ExecutionResult(
                ok=False,
                error=result.get("error", "execution failed"),
                error_code=result.get("error_code", "FAIL"),
                duration_seconds=time.time() - t0,
            )

        output = result.get("output_content", "")
        return ExecutionResult(
            ok=True,
            output_content=output,
            output_hash=wk_sha256(output.encode()) if output else "",
            cost_usd=0.0,  # cost tracked by WorkerKit, not Letta
            duration_seconds=result.get("duration_ms", 0) / 1000,
            tokens_input=0,
            tokens_output=0,
            metadata={
                "agent_id": result.get("agent_id", ""),
                "conversation_id": result.get("conversation_id", ""),
                "session_id": result.get("session_id", ""),
                "mode": "letta-service",
            },
            trace_events=[{
                "type": "letta",
                "agent_id": result.get("agent_id", ""),
                "conversation_id": result.get("conversation_id", ""),
                "tool_calls": result.get("tool_calls", []),
            }],
        )

    async def cancel(self, run_id: str) -> bool:
        return False

    async def export_state(self, dest: str) -> str:
        if not self.worker_id:
            return ""
        try:
            trajectory = await self._client.get_trajectory(self.worker_id)
            from pathlib import Path
            Path(dest).write_text(json.dumps(trajectory, indent=2))
            return wk_sha256(json.dumps(trajectory, sort_keys=True).encode())
        except Exception:
            return ""

    async def health(self) -> WorkerHealth:
        t0 = time.time()
        try:
            h = await self._client.health()
            return WorkerHealth(
                ok=h.get("ok", False),
                runtime=self.runtime,
                version=h.get("version", ""),
                detail=f"service: {self.service_url}",
                latency_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return WorkerHealth(
                ok=False,
                runtime=self.runtime,
                detail=str(e)[:200],
                latency_ms=(time.time() - t0) * 1000,
            )
