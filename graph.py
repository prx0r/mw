"""Asset dependency graph — what composes into what.

Tracks the supply chain: which assets use which other assets.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict


@dataclass
class Dependency:
    parent_id: str = ""
    child_id: str = ""
    role: str = ""  # "uses", "derived_from", "improves"
    position: int = 0
    configuration: dict = field(default_factory=dict)


class AssetGraph:
    """Track asset dependencies — the production graph."""

    def __init__(self):
        self.edges: list[Dependency] = []
        self.nodes: dict[str, dict] = {}

    def add_asset(self, asset_id: str, asset_type: str, name: str = ""):
        self.nodes[asset_id] = {"type": asset_type, "name": name, "created_at": time.time()}

    def add_dependency(self, parent_id: str, child_id: str, role: str = "uses"):
        self.edges.append(Dependency(parent_id=parent_id, child_id=child_id, role=role))

    def get_components(self, asset_id: str) -> list[str]:
        """What does this asset use?"""
        return [e.child_id for e in self.edges if e.parent_id == asset_id]

    def get_dependents(self, asset_id: str) -> list[str]:
        """What uses this asset?"""
        return [e.parent_id for e in self.edges if e.child_id == asset_id]

    def get_upstream(self, asset_id: str, depth: int = 3) -> set[str]:
        """Get all upstream assets (recursive)."""
        visited = set()
        queue = [asset_id]
        for _ in range(depth):
            next_queue = []
            for aid in queue:
                for e in self.edges:
                    if e.parent_id == aid and e.child_id not in visited:
                        visited.add(e.child_id)
                        next_queue.append(e.child_id)
            queue = next_queue
        return visited

    def save(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        data = {
            "nodes": self.nodes,
            "edges": [asdict(e) for e in self.edges],
        }
        (path / "graph.json").write_text(json.dumps(data, indent=2))

    def load(self, path: Path):
        p = path / "graph.json"
        if p.exists():
            data = json.loads(p.read_text())
            self.nodes = data.get("nodes", {})
            self.edges = [Dependency(**e) for e in data.get("edges", [])]

