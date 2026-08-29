"""Trace Merkle tree — commitment over trace events.

Don't publish full chain-of-thought. Every material event gets a record.
receipt contains only traceRoot. Selective reveal with Merkle proof later.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from evidence.canonical import sha256, canonical_json


@dataclass
class TraceEvent:
    """A single material event in a run."""
    sequence: int = 0
    event_type: str = ""  # aci_inference, http, tool, x402, artifact
    request_hash: str = ""
    response_hash: str = ""
    provider: str = ""
    cost: str = "0"
    timestamp: float = 0.0
    metadata: dict = field(default_factory=dict)

    def leaf_hash(self) -> str:
        """SHA-256 leaf for Merkle tree."""
        return sha256(canonical_json({
            "seq": self.sequence,
            "type": self.event_type,
            "req": self.request_hash,
            "res": self.response_hash,
            "provider": self.provider,
            "cost": self.cost,
            "ts": self.timestamp,
        }))

    def to_dict(self) -> dict:
        return {
            "sequence": self.sequence,
            "eventType": self.event_type,
            "requestHash": self.request_hash,
            "responseHash": self.response_hash,
            "provider": self.provider,
            "cost": self.cost,
            "timestamp": self.timestamp,
        }


def _hash_pair(a: str, b: str) -> str:
    """Hash two nodes together. If b is empty, return a."""
    if not b:
        return a
    if a < b:
        return sha256(f"{a}:{b}")
    return sha256(f"{b}:{a}")


class TraceMerkleTree:
    """Merkle tree over trace events.

    For v1: simple binary tree with sorted pair hashing.
    Later: proper incremental Merkle if needed.
    """

    def __init__(self, events: list[TraceEvent] = None):
        self.events = events or []
        self._leaves: list[str] = []
        self._tree: list[list[str]] = []
        self._root: str = ""
        self._build()

    def _build(self):
        if not self.events:
            self._root = sha256("")
            return

        self._leaves = [e.leaf_hash() for e in self.events]

        # Build tree layers
        layer = self._leaves[:]
        self._tree = [layer]

        while len(layer) > 1:
            next_layer = []
            for i in range(0, len(layer), 2):
                left = layer[i]
                right = layer[i + 1] if i + 1 < len(layer) else ""
                next_layer.append(_hash_pair(left, right))
            layer = next_layer
            self._tree.append(layer)

        self._root = layer[0] if layer else sha256("")

    @property
    def root(self) -> str:
        return self._root

    @property
    def leaf_count(self) -> int:
        return len(self._leaves)

    def get_proof(self, index: int) -> list[dict]:
        """Get Merkle proof for a leaf at index."""
        if index < 0 or index >= len(self._leaves):
            return []

        proof = []
        idx = index
        for layer in self._tree[:-1]:
            if idx % 2 == 0:
                sibling_idx = idx + 1
                side = "right"
            else:
                sibling_idx = idx - 1
                side = "left"

            if sibling_idx < len(layer):
                proof.append({"hash": layer[sibling_idx], "side": side})
            else:
                proof.append({"hash": "", "side": side})

            idx = idx // 2

        return proof

    def verify_proof(self, leaf_hash: str, proof: list[dict], root: str) -> bool:
        """Verify a Merkle proof."""
        current = leaf_hash
        for step in proof:
            sibling = step["hash"]
            if step["side"] == "right":
                current = _hash_pair(current, sibling) if sibling else current
            else:
                current = _hash_pair(sibling, current) if sibling else current
        return current == root
