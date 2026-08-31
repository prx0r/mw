"""MiMo wiring — disable thinking for fast tasks."""
from __future__ import annotations

import json
from typing import Any


class MiMoWiring:
    """Wire MiMo thinking control."""

    @staticmethod
    def disable_thinking() -> dict:
        """Return MiMo payload with thinking disabled."""
        return {"thinking": {"type": "disabled"}}

    @staticmethod
    def enable_thinking(budget_tokens: int = 4096) -> dict:
        """Return MiMo payload with thinking enabled."""
        return {"thinking": {"type": "enabled", "budget_tokens": budget_tokens}}

    @staticmethod
    def translate_letta_reasoning_effort(effort: str) -> dict:
        """Translate Letta reasoning_effort to MiMo thinking config."""
        mapping = {
            "none": {"type": "disabled"},
            "minimal": {"type": "enabled", "budget_tokens": 512},
            "low": {"type": "enabled", "budget_tokens": 1024},
            "medium": {"type": "enabled", "budget_tokens": 2048},
            "high": {"type": "enabled", "budget_tokens": 4096},
        }
        return {"thinking": mapping.get(effort, {"type": "disabled"})}
