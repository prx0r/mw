"""ProviderRegistry — secure API key storage + cost lookup via LiveLLM.

Keys stored in env vars (never in code).
Costs looked up from LiveLLM or fallback pricing.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


# Default pricing (used when LiveLLM is unavailable)
DEFAULT_PRICING = {
    "opencode-go/mimo-v2.5": {
        "input_per_m": 0.0,  # free tier
        "output_per_m": 0.0,
        "free": True,
        "provider": "opencode-go",
    },
    "groq/llama-3.3-70b-versatile": {
        "input_per_m": 0.59,
        "output_per_m": 0.79,
        "free": False,
        "provider": "groq",
    },
    "groq/llama-3.1-8b-instant": {
        "input_per_m": 0.05,
        "output_per_m": 0.08,
        "free": False,
        "provider": "groq",
    },
    "groq/gemma2-9b-it": {
        "input_per_m": 0.20,
        "output_per_m": 0.20,
        "free": False,
        "provider": "groq",
    },
    "anthropic/claude-3.5-sonnet": {
        "input_per_m": 3.0,
        "output_per_m": 15.0,
        "free": False,
        "provider": "anthropic",
    },
    "openai/gpt-4o-mini": {
        "input_per_m": 0.15,
        "output_per_m": 0.60,
        "free": False,
        "provider": "openai",
    },
}


class ProviderRegistry:
    """Secure provider registry with cost lookup."""

    def __init__(self, livellm_url: str = "http://localhost:3847"):
        self.livellm_url = livellm_url
        self._pricing_cache: dict[str, dict] = {}
        self._load_env_keys()

    def _load_env_keys(self):
        """Load API keys from .env files."""
        env_files = [
            Path("/root/workerkit/.env"),
            Path("/root/.env"),
        ]
        for env_file in env_files:
            if env_file.exists():
                for line in env_file.read_text().splitlines():
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())

    def get_key(self, provider: str) -> str:
        """Get API key for a provider (from env vars)."""
        key_map = {
            "opencode-go": "OPENCODE_API_KEY",
            "groq": "GROQ_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "cloudflare": "CF_API_TOKEN",
        }
        env_var = key_map.get(provider, "")
        return os.environ.get(env_var, "")

    def get_pricing(self, model: str) -> dict:
        """Get pricing for a model (LiveLLM or fallback)."""
        # Try LiveLLM first
        try:
            import urllib.request
            resp = urllib.request.urlopen(f"{self.livellm_url}/v1/economics/{model}", timeout=5)
            data = json.loads(resp.read())
            return {
                "input_per_m": data.get("input_per_m", 0),
                "output_per_m": data.get("output_per_m", 0),
                "free": data.get("free", False),
                "provider": data.get("provider", ""),
                "source": "livellm",
            }
        except Exception:
            pass

        # Fallback to defaults
        pricing = DEFAULT_PRICING.get(model, {})
        if pricing:
            pricing["source"] = "default"
            return pricing

        return {"input_per_m": 0, "output_per_m": 0, "free": True, "source": "unknown"}

    def estimate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost in USD for a model call."""
        pricing = self.get_pricing(model)
        input_cost = (prompt_tokens / 1_000_000) * pricing.get("input_per_m", 0)
        output_cost = (completion_tokens / 1_000_000) * pricing.get("output_per_m", 0)
        return input_cost + output_cost

    def cheapest_model(self, task_type: str = "general") -> str:
        """Find cheapest model for a task type."""
        # For now, return free models
        return "opencode-go/mimo-v2.5"

    def list_providers(self) -> list[dict]:
        """List all configured providers."""
        providers = []
        for provider, env_var in [("opencode-go", "OPENCODE_API_KEY"), ("groq", "GROQ_API_KEY")]:
            key = os.environ.get(env_var, "")
            providers.append({
                "provider": provider,
                "configured": bool(key),
                "key_preview": f"{key[:10]}..." if key else "not set",
            })
        return providers

    def status(self) -> dict:
        """Get registry status."""
        return {
            "providers": self.list_providers(),
            "livellm": self._check_livellm(),
            "pricing_models": len(DEFAULT_PRICING),
        }

    def _check_livellm(self) -> bool:
        try:
            import urllib.request
            urllib.request.urlopen(f"{self.livellm_url}/v1/health", timeout=2)
            return True
        except Exception:
            return False
