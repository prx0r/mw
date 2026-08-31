"""Pytest conftest — adds workerkit root to sys.path for bare imports.

This allows `from core.hashing import ...` to work alongside
`from workerkit.core.hashing import ...`. MVP compatibility layer.
"""
import sys
from pathlib import Path

# Add the workerkit project root to sys.path
_root = str(Path(__file__).parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)
