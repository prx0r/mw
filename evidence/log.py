"""Evidence log — append-only Merkle log with periodic Ethereum checkpoints.

Do NOT shove every receipt onto Ethereum.
Maintain an append-only Moltwork evidence log with periodic root anchoring.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from evidence.canonical import sha256, canonical_json


@dataclass
class CheckpointV1:
    """Periodic checkpoint anchoring evidence log root to Ethereum."""
    epoch: int = 0
    root: str = ""
    receipt_count: int = 0
    previous_root: str = ""
    ethereum_tx: str = ""  # tx hash of root anchor
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "epoch": self.epoch,
            "root": self.root,
            "receiptCount": self.receipt_count,
            "previousRoot": self.previous_root,
            "ethereumTx": self.ethereum_tx,
            "timestamp": self.timestamp,
        }


class EvidenceLog:
    """Append-only Merkle log of run receipts.

    Periodically anchors root to Ethereum.
    Provides inclusion proofs for individual receipts.
    """

    def __init__(self):
        self._leaves: list[str] = []
        self._tree: list[list[str]] = []
        self._root: str = ""
        self._checkpoints: list[CheckpointV1] = []
        self._receipts: list[dict] = []  # stored receipts (for inclusion proofs)

    def append(self, receipt_digest: str) -> int:
        """Append a receipt to the log. Returns leaf index."""
        self._leaves.append(receipt_digest)
        self._rebuild_tree()
        return len(self._leaves) - 1

    def _rebuild_tree(self):
        """Rebuild Merkle tree from leaves."""
        if not self._leaves:
            self._root = sha256("empty-evidence-log")
            self._tree = []
            return

        layer = self._leaves[:]
        self._tree = [layer]

        while len(layer) > 1:
            next_layer = []
            for i in range(0, len(layer), 2):
                left = layer[i]
                right = layer[i + 1] if i + 1 < len(layer) else ""
                if right:
                    pair = f"{left}:{right}" if left < right else f"{right}:{left}"
                    next_layer.append(sha256(pair))
                else:
                    next_layer.append(left)
            layer = next_layer
            self._tree.append(layer)

        self._root = layer[0] if layer else sha256("empty")

    @property
    def root(self) -> str:
        return self._root

    @property
    def count(self) -> int:
        return len(self._leaves)

    def get_proof(self, index: int) -> list[dict]:
        """Get inclusion proof for leaf at index."""
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

    def verify_inclusion(self, leaf: str, proof: list[dict]) -> bool:
        """Verify a leaf is included in the current root."""
        current = leaf
        for step in proof:
            sibling = step["hash"]
            if step["side"] == "right":
                if sibling:
                    pair = f"{current}:{sibling}" if current < sibling else f"{sibling}:{current}"
                    current = sha256(pair)
            else:
                if sibling:
                    pair = f"{sibling}:{current}" if sibling < current else f"{current}:{sibling}"
                    current = sha256(pair)
        return current == self._root

    def checkpoint(self, ethereum_tx: str = "") -> CheckpointV1:
        """Create a checkpoint anchoring current root."""
        cp = CheckpointV1(
            epoch=len(self._checkpoints),
            root=self._root,
            receipt_count=len(self._leaves),
            previous_root=self._checkpoints[-1].root if self._checkpoints else "",
            ethereum_tx=ethereum_tx,
        )
        self._checkpoints.append(cp)
        return cp

    @property
    def checkpoints(self) -> list[CheckpointV1]:
        return self._checkpoints
