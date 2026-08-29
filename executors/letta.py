"""LettaSDKExecutor — execute work via Letta Agent SDK.

Each execution creates a new session (conversation).
The agent persists across sessions via MemFS.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionResult:
    ok: bool = False
    output_content: str = ""
    cost_usd: float = 0.0
    duration_seconds: float = 0.0
    error: str = ""
    error_code: str = ""
    metadata: dict = field(default_factory=dict)


class LettaSDKExecutor:
    def __init__(self, agent_id: str = "", model: str = "opencode-go/mimo-v2.5"):
        self.agent_id = agent_id
        self.model = model

    async def execute(self, task: str, budget: float = 4.0, timeout: int = 300) -> ExecutionResult:
        t0 = time.time()
        try:
            from letta_agent_sdk import LettaAgentClient
            client = LettaAgentClient(backend="local")
            session = await client.createSession(self.agent_id)
            await session.send(task)
            output = ""
            for msg in session.stream():
                if msg.type == "assistant" and msg.content:
                    output += msg.content
                if msg.type == "result":
                    break
            return ExecutionResult(ok=bool(output), output_content=output,
                                   duration_seconds=(time.time() - t0) / 1000,
                                   metadata={"agent_id": self.agent_id, "mode": "letta-sdk"})
        except Exception as e:
            return ExecutionResult(ok=False, error=str(e), error_code="FAIL",
                                   duration_seconds=(time.time() - t0) / 1000)
