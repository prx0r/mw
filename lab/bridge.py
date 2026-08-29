"""Live Event Bridge — stream Letta events into WorkerKit EventLedger.

Converts Letta SDK stream events into WorkerKit canonical events.
"""
from __future__ import annotations

import json
import time
from typing import Any, Callable

from core.hashing import sha256, jcs, SCHEMA_EVENT


class EventBridge:
    """Bridge between Letta SDK stream and WorkerKit EventLedger.

    Translates:
      Letta assistant message → WorkerKit model.call event
      Letta tool_call → WorkerKit tool.invoked event
      Letta tool_result → WorkerKit tool.result event
      Letta usage → WorkerKit cost.recorded event
    """

    def __init__(self, ledger: Any = None):
        self.ledger = ledger
        self._event_count = 0

    def bridge_event(self, run_id: str, letta_event: dict) -> str | None:
        """Convert a Letta event to a WorkerKit event and record it."""
        if not self.ledger:
            return None

        event_type = letta_event.get("type", "")
        payload = {}

        if event_type == "assistant":
            content = letta_event.get("content", "")
            payload = {
                "model": letta_event.get("model", ""),
                "content_length": len(content),
                "content_hash": sha256(content) if content else "",
            }
            wk_event_type = "model.call.completed"

        elif event_type == "tool_call":
            payload = {
                "tool_name": letta_event.get("toolName", ""),
                "tool_args": letta_event.get("toolInput", {}),
                "tool_call_id": letta_event.get("toolCallId", ""),
            }
            wk_event_type = "tool.invoked"

        elif event_type == "tool_result":
            content = letta_event.get("content", "")
            payload = {
                "tool_name": letta_event.get("toolName", ""),
                "result_length": len(content) if isinstance(content, str) else 0,
                "is_error": letta_event.get("isError", False),
            }
            wk_event_type = "tool.result"

        elif event_type == "result":
            payload = {
                "success": letta_event.get("success", False),
                "duration_ms": letta_event.get("durationMs", 0),
                "stop_reason": letta_event.get("stopReason", ""),
                "conversation_id": letta_event.get("conversationId", ""),
            }
            wk_event_type = "run.completed"

        elif event_type == "error":
            payload = {
                "error_code": letta_event.get("errorCode", ""),
                "message": letta_event.get("message", "")[:200],
                "recoverable": letta_event.get("recoverable", False),
            }
            wk_event_type = "run.error"

        else:
            return None

        self._event_count += 1
        return self.ledger.append(run_id, wk_event_type, payload)

    def bridge_stream(self, run_id: str, stream: Any) -> dict:
        """Bridge an entire Letta stream into WorkerKit events."""
        stats = {"events": 0, "assistant": 0, "tool_calls": 0, "errors": 0}

        for event in stream:
            event_type = event.get("type", "")
            if event_type == "assistant":
                stats["assistant"] += 1
            elif event_type in ("tool_call", "tool_result"):
                stats["tool_calls"] += 1
            elif event_type == "error":
                stats["errors"] += 1

            result = self.bridge_event(run_id, event)
            if result:
                stats["events"] += 1

        return stats
