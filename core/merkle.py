"""Merkle tree — content-addressed tree over event digests.

Allows selective disclosure: prove one event belongs to a receipt
without revealing the full trace.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from core.hashing import sha256, jcs


def _hash_pair(left: str, right: str) -> str:
    """Hash two children. Deterministic ordering."""
    if left < right:
        return sha256(left + right)
    return sha256(right + left)


@dataclass
class MerkleProof:
    """Proof that a leaf belongs to the root."""
    leaf_index: int
    leaf_hash: str
    siblings: list[str]  # sibling hashes from leaf to root
    root: str

    def verify(self) -> bool:
        """Recompute root from leaf + siblings."""
        current = self.leaf_hash
        idx = self.leaf_index
        for sibling in self.siblings:
            if idx % 2 == 0:
                current = _hash_pair(current, sibling)
            else:
                current = _hash_pair(sibling, current)
            idx //= 2
        return current == self.root

    def to_dict(self) -> dict:
        return {
            "leaf_index": self.leaf_index,
            "leaf_hash": self.leaf_hash,
            "siblings": self.siblings,
            "root": self.root,
        }


class MerkleTree:
    """Merkle tree over a list of leaf hashes."""

    def __init__(self, leaves: list[str] | None = None):
        self.leaves: list[str] = leaves or []
        self._nodes: list[str] = []
        self._build()

    def _build(self):
        if not self.leaves:
            self._nodes = []
            return
        # Pad to power of 2
        n = len(self.leaves)
        size = 1
        while size < n:
            size *= 2
        padded = self.leaves + [""] * (size - n)
        self._nodes = list(padded)
        # Build tree bottom-up
        level = size
        offset = 0
        while level > 1:
            for i in range(0, level, 2):
                left = self._nodes[offset + i]
                right = self._nodes[offset + i + 1]
                self._nodes.append(_hash_pair(left, right) if left and right else left or right)
            offset += level
            level //= 2

    @property
    def root(self) -> str:
        """Root hash of the tree."""
        if not self._nodes:
            return ""
        return self._nodes[-1]

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    def proof(self, index: int) -> MerkleProof | None:
        """Generate a proof for the leaf at the given index."""
        if index < 0 or index >= len(self.leaves):
            return None
        if not self.leaves:
            return None

        # Find the level structure
        n = len(self.leaves)
        size = 1
        while size < n:
            size *= 2

        siblings = []
        idx = index
        offset = 0
        level = size

        while level > 1:
            sibling_idx = idx ^ 1  # flip last bit
            if offset + sibling_idx < len(self._nodes):
                sibling = self._nodes[offset + sibling_idx]
                if sibling:
                    siblings.append(sibling)
            offset += level
            idx //= 2
            level //= 2

        return MerkleProof(
            leaf_index=index,
            leaf_hash=self.leaves[index],
            siblings=siblings,
            root=self.root,
        )

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "leaf_count": len(self.leaves),
            "node_count": len(self._nodes),
        }
