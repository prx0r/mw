"""Adapters — execution, telemetry, marketplaces, payments.

Canonical runtime: services/runtime-letta/ (Letta Agent SDK)
Legacy: adapters/letta.py (deprecated, kept for backward compatibility)
"""
try:
    from workerkit.adapters.base import WorkerAdapter, WorkerInspect, WorkerHealth, RunContext, ExecutionResult
except ImportError:
    from adapters.base import WorkerAdapter, WorkerInspect, WorkerHealth, RunContext, ExecutionResult

try:
    from services.runtime_letta.client import LettaServiceAdapter as LettaAdapter
except ImportError:
    try:
        from workerkit.adapters.letta import LettaAdapter
    except ImportError:
        from adapters.letta import LettaAdapter

__all__ = ["WorkerAdapter", "LettaAdapter", "WorkerInspect", "WorkerHealth", "RunContext", "ExecutionResult"]

ADAPTERS: dict[str, type] = {
    "letta": LettaAdapter,
}

def get_adapter(runtime: str, **kwargs):
    """Instantiate adapter by runtime name."""
    cls = ADAPTERS.get(runtime, LettaAdapter)
    return cls(**kwargs)
