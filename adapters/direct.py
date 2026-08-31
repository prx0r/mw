"""Direct adapter — calls mimo-v2.5 via opencode-go, with Groq fallback.

ALWAYS use mimo-v2.5. NEVER use kimi or expensive models.
Groq free models (gpt-oss) as fallback for testing only.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from workerkit.adapters.base import WorkerAdapter, WorkerInspect, WorkerHealth, RunContext, ExecutionResult
from workerkit.core.hashing import sha256

# Load .env if present
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

OPENCODE_API_URL = os.environ.get("OPENCODE_API_URL", "https://opencode.ai/zen/go/v1/chat/completions")
OPENCODE_API_KEY = os.environ.get("OPENCODE_API_KEY", "")
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "mimo-v2.5")

GROQ_API_URL = os.environ.get("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
FALLBACK_MODEL = os.environ.get("FALLBACK_MODEL", "openai/gpt-oss-120b")


class DirectAdapter:
    """WorkerAdapter that calls opencode-go directly.

    Bypasses Letta App Server. Uses the same API the opencode CLI uses.
    """

    runtime = "direct-opencode-go"

    def __init__(self, worker_id: str = "", model: str = "",
                 api_url: str = "", api_key: str = ""):
        self.worker_id = worker_id
        self.model = model or DEFAULT_MODEL
        self.api_url = api_url or OPENCODE_API_URL
        self.api_key = api_key or OPENCODE_API_KEY

    async def inspect(self) -> WorkerInspect:
        return WorkerInspect(
            worker_id=self.worker_id,
            runtime=self.runtime,
            model=self.model,
        )

    async def execute(self, work_order: Any, context: RunContext) -> ExecutionResult:
        """Execute via mimo-v2.5 (opencode-go), with Groq fallback."""
        t0 = time.time()

        # Extract task from work_order
        if hasattr(work_order, "objective"):
            task = work_order.objective
        elif isinstance(work_order, dict):
            task = work_order.get("description", work_order.get("title", str(work_order)))
        else:
            task = str(work_order)

        messages = [
            {"role": "system", "content": "You are a specialist Moltwork worker. Complete the task precisely. Output your final answer clearly. Do not use thinking tags."},
            {"role": "user", "content": task},
        ]

        # Try mimo-v2.5 first
        if OPENCODE_API_KEY:
            result = self._call_api(OPENCODE_API_URL, OPENCODE_API_KEY, DEFAULT_MODEL,
                                     messages, context.timeout_seconds or 120)
            if result and result.ok:
                result.duration_seconds = time.time() - t0
                return result

        # Fallback to Groq
        if GROQ_API_KEY:
            result = self._call_api(GROQ_API_URL, GROQ_API_KEY, FALLBACK_MODEL,
                                     messages, context.timeout_seconds or 120)
            if result and result.ok:
                result.duration_seconds = time.time() - t0
                return result

        return ExecutionResult(
            ok=False,
            error="no API key configured or all providers failed",
            error_code="NO_API",
            duration_seconds=time.time() - t0,
        )

    def _call_api(self, url: str, key: str, model: str,
                  messages: list, timeout: int) -> ExecutionResult | None:
        """Call a chat completions API and parse the response."""
        try:
            payload = json.dumps({
                "model": model,
                "messages": messages,
                "max_tokens": 4096,
            }).encode()

            req = urllib.request.Request(url, data=payload, headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "User-Agent": "moltwork-workerkit/0.1.0",
            })

            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            return ExecutionResult(ok=False, error=str(e), error_code="FAIL")

        choices = data.get("choices", [])
        if not choices:
            return None

        msg = choices[0].get("message", {})
        content = msg.get("content") or ""
        reasoning = msg.get("reasoning_content") or msg.get("reasoning") or ""

        # Reasoning models: if content is empty, use reasoning as content
        if not content and reasoning:
            content = reasoning

        if not content or len(content.strip()) < 5:
            return None

        usage = data.get("usage", {})
        output_hash = sha256(content.encode())

        return ExecutionResult(
            ok=True,
            output_content=content,
            output_hash=output_hash,
            cost_usd=0.0,
            duration_seconds=0.0,
            tokens_input=usage.get("prompt_tokens", 0),
            tokens_output=usage.get("completion_tokens", 0),
            metadata={"model": model, "provider": url.split("/")[2]},
        )

    async def cancel(self, run_id: str) -> bool:
        return False

    async def export_state(self, dest: str) -> str:
        return ""

    async def health(self) -> WorkerHealth:
        return WorkerHealth(
            ok=True,
            runtime=self.runtime,
            version="0.1.0",
            detail=f"model: {self.model}",
        )
