"""Adapters — execution, telemetry, marketplaces, payments."""
from workerkit.adapters.base import WorkerAdapter, WorkerInspect, WorkerHealth, RunContext, ExecutionResult
from workerkit.adapters.letta import LettaAdapter
from workerkit.adapters.execution import WorkerAdapter as LegacyWorkerAdapter

__all__ = ["WorkerAdapter", "LegacyWorkerAdapter", "LettaAdapter", "WorkerInspect", "WorkerHealth", "RunContext", "ExecutionResult"]

# Runtime registry — add new adapters here
ADAPTERS: dict[str, type] = {
    "letta": LettaAdapter,
}

def get_adapter(runtime: str, **kwargs):
    """Instantiate adapter by runtime name. Falls back to Letta."""
    cls = ADAPTERS.get(runtime, LettaAdapter)
    return cls(**kwargs)
