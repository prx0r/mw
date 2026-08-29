"""LettaAdapter — DEPRECATED. Use services/runtime-letta/ instead.

This adapter talks to old /v1/agents REST APIs and has stub fallback.
The canonical implementation is services/runtime-letta/ using Letta Agent SDK.

For new code, use:
  from services.runtime-letta.client import LettaServiceAdapter

This file is kept for backward compatibility only.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

from workerkit.adapters.base import WorkerAdapter, WorkerInspect, WorkerHealth, RunContext, ExecutionResult
from workerkit.evidence.canonical import sha256 as wk_sha256


def _af_state_hash(af_path: str | Path) -> str:
    p = Path(af_path)
    if not p.exists():
        return ""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _af_inspect(af_path: str | Path) -> dict:
    """Parse .af JSON for inspect()."""
    try:
        d = json.loads(Path(af_path).read_bytes())
    except Exception:
        return {}
    agents = d.get("agents", [])
    blocks = d.get("blocks", [])
    tools = d.get("tools", [])
    mcp = d.get("mcp_servers", [])
    # Memory block names
    block_names = [b.get("label", b.get("name", "")) for b in blocks] if isinstance(blocks, list) else []
    tool_names = [t.get("name", t.get("label", "")) for t in tools] if isinstance(tools, list) else []
    agent_name = ""
    if agents and isinstance(agents, list):
        agent_name = agents[0].get("name", "") if isinstance(agents[0], dict) else ""
    return {
        "agent_name": agent_name,
        "block_names": block_names,
        "tool_names": tool_names,
        "mcp_servers": mcp if isinstance(mcp, list) else [],
        "raw": d,
    }


class LettaAdapter:
    """Reference adapter: Letta stateful agent + .af portable state."""

    runtime = "letta"

    def __init__(self, af_path: str = "", server_url: str = ""):
        self.af_path = af_path or os.environ.get("LETTA_AF_PATH", "")
        self.server_url = (server_url or os.environ.get("LETTA_SERVER_URL", "")).rstrip("/")
        # Also check letta-code env
        if not self.server_url:
            self.server_url = os.environ.get("LETTA_API_URL", "").rstrip("/")

    @property
    def has_af(self) -> bool:
        return bool(self.af_path and Path(self.af_path).exists())

    @property
    def has_server(self) -> bool:
        return bool(self.server_url)

    async def inspect(self) -> WorkerInspect:
        if self.has_af:
            info = _af_inspect(self.af_path)
            return WorkerInspect(
                worker_id=info.get("agent_name", Path(self.af_path).stem),
                runtime="letta",
                tools=info.get("tool_names", []),
                mcp_servers=info.get("mcp_servers", []),
                memory_blocks=info.get("block_names", []),
                state_hash=_af_state_hash(self.af_path),
            )
        if self.has_server:
            # Try to query Letta server
            try:
                import httpx
                async with httpx.AsyncClient(timeout=5) as c:
                    r = await c.get(f"{self.server_url}/v1/agents")
                    r.raise_for_status()
                    agents = r.json()
                    # Use first agent
                    if isinstance(agents, list) and agents:
                        a = agents[0]
                        return WorkerInspect(
                            worker_id=a.get("id", ""),
                            runtime="letta",
                            model=a.get("llm_config", {}).get("model", ""),
                            tools=[t.get("name", "") for t in a.get("tools", [])],
                            memory_blocks=list(a.get("memory", {}).keys()) if isinstance(a.get("memory"), dict) else [],
                            state_hash="",
                        )
            except Exception:
                pass
        return WorkerInspect(worker_id="", runtime="letta", state_hash="")

    async def execute(self, work_order: Any, context: RunContext, force_stub: bool = False) -> ExecutionResult:
        t0 = time.time()
        # If we have a Letta server, delegate there
        if self.has_server:
            try:
                return await self._execute_via_server(work_order, context)
            except Exception as e:
                return ExecutionResult(ok=False, error=f"letta server error: {e}",
                                       error_code="FAIL", duration_seconds=time.time() - t0)

        # No server — this is a failure, not a success
        title = getattr(work_order, "title", "") or (work_order.get("title", "") if isinstance(work_order, dict) else str(work_order)[:80])

        if force_stub:
            # Only for testing: explicitly request stub execution
            return ExecutionResult(
                ok=True,
                output_content=f"[letta-stub] would execute: {title}",
                output_hash=wk_sha256(f"stub:{title}"),
                cost_usd=0.0,
                duration_seconds=time.time() - t0,
                metadata={"mode": "stub", "af_path": self.af_path, "has_af": self.has_af},
                trace_events=[{"type": "stub", "detail": "no Letta server — stub execution"}],
            )

        if self.has_af:
            return ExecutionResult(
                ok=False,
                error=f"af file found at {self.af_path} but no Letta server to execute against",
                error_code="NOT_EXECUTED",
                duration_seconds=time.time() - t0,
                metadata={"mode": "no-server", "af_path": self.af_path},
            )

        return ExecutionResult(
            ok=False,
            error="no LETTA_SERVER_URL and no LETTA_AF_PATH — cannot execute",
            error_code="NO_RUNTIME",
            duration_seconds=time.time() - t0,
            metadata={"mode": "no-runtime"},
        )

    async def _execute_via_server(self, work_order: Any, context: RunContext) -> ExecutionResult:
        import httpx

        title = getattr(work_order, "title", "") or (work_order.get("title", "") if isinstance(work_order, dict) else "")
        desc = getattr(work_order, "description", "") or (work_order.get("description", "") if isinstance(work_order, dict) else "")
        prompt = f"Task: {title}\n\n{desc}\n\nWorkspace: {context.workspace}\nBudget: ${context.budget_remaining:.2f}"

        # Find agent ID
        agent_id = ""
        if self.has_af:
            info = _af_inspect(self.af_path)
            agent_id = info.get("raw", {}).get("agents", [{}])[0].get("id", "") if info.get("raw", {}).get("agents") else ""

        if not agent_id:
            # List agents, pick first
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{self.server_url}/v1/agents")
                r.raise_for_status()
                agents = r.json()
                if isinstance(agents, list) and agents:
                    agent_id = agents[0].get("id", "")
                elif isinstance(agents, dict) and "agents" in agents:
                    agent_id = agents["agents"][0].get("id", "") if agents["agents"] else ""

        if not agent_id:
            raise RuntimeError("no Letta agent found — import an .af first")

        t0 = time.time()
        async with httpx.AsyncClient(timeout=context.timeout_seconds + 10) as c:
            # Send message to agent
            r = await c.post(
                f"{self.server_url}/v1/agents/{agent_id}/messages",
                json={"messages": [{"role": "user", "content": prompt}]},
                timeout=context.timeout_seconds + 10,
            )
            r.raise_for_status()
            data = r.json()

        # Extract response
        messages = data.get("messages", []) if isinstance(data, dict) else []
        output = ""
        for m in reversed(messages):
            if isinstance(m, dict) and m.get("role") == "assistant":
                content = m.get("content", "")
                if isinstance(content, list):
                    content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
                if content:
                    output = content if isinstance(content, str) else str(content)
                    break
        if not output and isinstance(data, dict):
            output = data.get("output", "") or data.get("content", "") or json.dumps(data)[:2000]

        usage = data.get("usage", {}) if isinstance(data, dict) else {}
        return ExecutionResult(
            ok=True,
            output_content=output,
            output_hash=wk_sha256(output.encode()),
            cost_usd=float(usage.get("cost", 0) or 0),
            duration_seconds=time.time() - t0,
            tokens_input=int(usage.get("prompt_tokens", 0) or 0),
            tokens_output=int(usage.get("completion_tokens", 0) or 0),
            metadata={"agent_id": agent_id, "mode": "letta-server"},
            trace_events=[{"type": "letta", "agent_id": agent_id}],
        )

    async def cancel(self, run_id: str) -> bool:
        return False

    async def export_state(self, dest: str) -> str:
        """Export current agent state to .af file at dest. Returns sha256."""
        if self.has_server:
            try:
                import httpx

                # Export via Letta API
                inspect = await self.inspect()
                agent_id = inspect.worker_id
                if agent_id:
                    async with httpx.AsyncClient(timeout=30) as c:
                        r = await c.get(f"{self.server_url}/v1/agents/{agent_id}/export")
                        r.raise_for_status()
                        Path(dest).write_bytes(r.content)
                        return hashlib.sha256(r.content).hexdigest()
            except Exception:
                pass
        if self.has_af and Path(self.af_path).exists():
            data = Path(self.af_path).read_bytes()
            Path(dest).write_bytes(data)
            return hashlib.sha256(data).hexdigest()
        return ""

    async def health(self) -> WorkerHealth:
        t0 = time.time()
        if self.has_server:
            try:
                import httpx

                async with httpx.AsyncClient(timeout=5) as c:
                    r = await c.get(f"{self.server_url}/v1/health", timeout=5)
                    ok = r.status_code < 500
                    return WorkerHealth(ok=ok, runtime="letta", version="server", detail=f"HTTP {r.status_code}", latency_ms=(time.time() - t0) * 1000)
            except Exception as e:
                return WorkerHealth(ok=False, runtime="letta", detail=str(e)[:200], latency_ms=(time.time() - t0) * 1000)
        if self.has_af:
            return WorkerHealth(ok=True, runtime="letta", version="local-af", detail=f"af: {self.af_path}", latency_ms=(time.time() - t0) * 1000)
        return WorkerHealth(ok=False, runtime="letta", detail="no LETTA_SERVER_URL and no LETTA_AF_PATH", latency_ms=(time.time() - t0) * 1000)

    @staticmethod
    def sanitize_af(src: str | Path, dest: str | Path):
        """Create distributable .af: remove secrets, private conversations, ephemeral state.

        Mirrors spec: private conversations REMOVE, credentials REMOVE,
        customer memory REMOVE, ephemeral REMOVE; expertise KEEP, behavior KEEP.
        """
        data = json.loads(Path(src).read_bytes())
        # Null secrets (Letta behavior on export)
        for agent in data.get("agents", []):
            if isinstance(agent, dict):
                for k in list(agent.keys()):
                    if "secret" in k.lower() or "api_key" in k.lower() or "credential" in k.lower():
                        agent[k] = None
        # Remove private file references if present
        # Keep blocks/tools/mcp_servers (expertise)
        Path(dest).write_text(json.dumps(data, indent=2))
        return dest
