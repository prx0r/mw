"""Lab intelligence — reflection, promotion, discovery."""
try:
    from lab.reflection import ReflectionPipeline
    from lab.discovery import LabDiscovery
except ImportError:
    from workerkit.lab.reflection import ReflectionPipeline
    from workerkit.lab.discovery import LabDiscovery

__all__ = ["ReflectionPipeline", "LabDiscovery"]
