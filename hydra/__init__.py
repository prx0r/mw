"""Hydra package."""
try:
    from hydra.store import HydraStore
except ImportError:
    from workerkit.hydra.store import HydraStore
__all__ = ["HydraStore"]
