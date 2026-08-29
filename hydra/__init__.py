"""Hydra package — lab projection over WorkerKit events."""
try:
    from hydra.store import LabProjection, HydraStore
except ImportError:
    from workerkit.hydra.store import LabProjection, HydraStore
__all__ = ["LabProjection", "HydraStore"]
