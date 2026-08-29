"""Progressive paid reveal — the economic mechanism.

Core: buyer pays per unit, each payment reveals one random chunk.
All payments count toward total price. At 100%: full artifact unlocked.

Invariants:
- money_paid / total_price = content_revealed / total_units
- Neither party controls reveal order
- Every cent spent reduces remaining unlock price
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .commitment import ArtifactEnvelope, MerkleTree, derive_reveal_order, reveal_chunk


REVEALS_DB = Path(__file__).parent.parent / "data" / "reveals.jsonl"
ASSETS_DB = Path(__file__).parent.parent / "data" / "assets.jsonl"


@dataclass
class PurchaseState:
    """Tracks how much of an artifact a buyer has purchased."""
    artifact_id: str
    buyer_id: str
    units_purchased: int = 0
    total_paid: float = 0.0
    chunks_revealed: list[int] = field(default_factory=list)
    reveal_order: list[int] = field(default_factory=list)
    started_at: float = 0.0
    last_reveal_at: float = 0.0

    @property
    def fraction_purchased(self) -> float:
        """0.0 to 1.0 — how much has been paid for."""
        total = len(self.reveal_order) or 1
        return self.units_purchased / total

    @property
    def remaining_cost(self) -> float:
        """Remaining cost to unlock everything."""
        remaining = len(self.reveal_order) - self.units_purchased
        if not self.reveal_order:
            return 0.0
        total = len(self.reveal_order)
        # Read price from asset
        return self._price_per_unit * remaining if hasattr(self, '_price_per_unit') else 0.0

    def to_dict(self) -> dict:
        return {
            "artifact_id": self.artifact_id,
            "buyer_id": self.buyer_id,
            "units_purchased": self.units_purchased,
            "total_paid": self.total_paid,
            "chunks_revealed": self.chunks_revealed,
            "fraction_purchased": round(self.fraction_purchased, 4),
            "started_at": self.started_at,
            "last_reveal_at": self.last_reveal_at,
        }


@dataclass
class RevealResult:
    """Result of revealing one chunk."""
    chunk_index: int
    content: str
    proof: list[tuple[str, bool]]
    verified: bool
    units_purchased: int
    fraction_revealed: float
    remaining_to_full: float
    cost_this_reveal: float
    total_paid: float


class ProgressiveReveal:
    """The core paid-reveal mechanism.

    Flow:
    1. Seller creates artifact, commits, publishes envelope
    2. Buyer searches, finds artifact, sees metadata + free abstract
    3. Buyer pays for first reveal → gets random chunk + proof
    4. Each subsequent payment reveals another random chunk
    5. At any point: [REVEAL NEXT 2.5% — $0.025] or [UNLOCK REMAINING — $X]
    6. At 100%: full artifact unlocked
    """

    def __init__(self):
        self._envelopes: dict[str, ArtifactEnvelope] = {}
        self._chunks: dict[str, list[str]] = {}
        self._trees: dict[str, MerkleTree] = {}
        self._states: dict[str, dict[str, PurchaseState]] = {}  # artifact_id → buyer_id → state
        self._reveal_prices: dict[str, float] = {}  # artifact_id → price per unit

    def publish(self, envelope: ArtifactEnvelope, chunks: list[str],
                tree: MerkleTree) -> None:
        """Seller publishes artifact envelope."""
        self._envelopes[envelope.artifact_id] = envelope
        self._chunks[envelope.artifact_id] = chunks
        self._trees[envelope.artifact_id] = tree
        self._reveal_prices[envelope.artifact_id] = envelope.total_price / len(chunks)
        self._states[envelope.artifact_id] = {}

        # Persist envelope
        _append(ASSETS_DB, envelope.to_dict())

    def get_price_per_unit(self, artifact_id: str) -> float:
        return self._reveal_prices.get(artifact_id, 0.0)

    def start_purchase(self, artifact_id: str, buyer_id: str) -> PurchaseState:
        """Buyer starts inspecting an artifact. Derives reveal order."""
        envelope = self._envelopes.get(artifact_id)
        if not envelope:
            raise ValueError(f"Artifact {artifact_id} not found")

        tree = self._trees[artifact_id]
        order = derive_reveal_order(tree.root, buyer_id, tree.size)

        state = PurchaseState(
            artifact_id=artifact_id,
            buyer_id=buyer_id,
            reveal_order=order,
            started_at=time.time(),
        )
        state._price_per_unit = self._reveal_prices[artifact_id]

        self._states.setdefault(artifact_id, {})[buyer_id] = state
        return state

    def reveal_next(self, artifact_id: str, buyer_id: str) -> RevealResult | None:
        """Reveal the next chunk in the buyer's random order."""
        state = self._states.get(artifact_id, {}).get(buyer_id)
        if not state:
            return None

        if state.units_purchased >= len(state.reveal_order):
            return None  # Already fully revealed

        # Get next chunk index from the pre-determined order
        next_idx = state.reveal_order[state.units_purchased]

        # Reveal it
        chunks = self._chunks[artifact_id]
        tree = self._trees[artifact_id]
        reveal = reveal_chunk(chunks, tree, next_idx, buyer_id)

        # Update state
        state.units_purchased += 1
        state.chunks_revealed.append(next_idx)
        state.last_reveal_at = time.time()
        state.total_paid += self._reveal_prices[artifact_id]

        price_per = self._reveal_prices[artifact_id]
        remaining = len(state.reveal_order) - state.units_purchased

        return RevealResult(
            chunk_index=next_idx,
            content=reveal["content"],
            proof=reveal["proof"],
            verified=reveal["verified"],
            units_purchased=state.units_purchased,
            fraction_revealed=state.fraction_purchased,
            remaining_to_full=remaining * price_per,
            cost_this_reveal=price_per,
            total_paid=state.total_paid,
        )

    def unlock_full(self, artifact_id: str, buyer_id: str) -> dict | None:
        """Buyer pays remaining balance to unlock full artifact."""
        state = self._states.get(artifact_id, {}).get(buyer_id)
        if not state:
            return None

        remaining = len(state.reveal_order) - state.units_purchased
        if remaining <= 0:
            # Already fully unlocked
            return {"chunks": self._chunks.get(artifact_id, []), "already_unlocked": True}

        # Pay remaining
        remaining_cost = remaining * self._reveal_prices[artifact_id]
        state.total_paid += remaining_cost
        state.units_purchased = len(state.reveal_order)
        state.chunks_revealed = list(range(len(state.reveal_order)))
        state.last_reveal_at = time.time()

        return {
            "chunks": self._chunks.get(artifact_id, []),
            "total_paid": state.total_paid,
            "unlocked": True,
        }

    def get_state(self, artifact_id: str, buyer_id: str) -> PurchaseState | None:
        return self._states.get(artifact_id, {}).get(buyer_id)

    def get_options(self, artifact_id: str, buyer_id: str) -> dict:
        """Get what buyer can do next."""
        state = self._states.get(artifact_id, {}).get(buyer_id)
        if not state:
            return {"action": "start", "cost": self.get_price_per_unit(artifact_id)}

        total = len(state.reveal_order)
        purchased = state.units_purchased
        remaining = total - purchased
        price_per = self._reveal_prices[artifact_id]

        if remaining <= 0:
            return {"action": "fully_unlocked", "total_paid": state.total_paid}

        return {
            "action": "continue",
            "units_purchased": purchased,
            "total_units": total,
            "fraction_purchased": round(purchased / total, 4),
            "next_reveal_cost": round(price_per, 6),
            "remaining_to_full": round(remaining * price_per, 6),
            "total_paid": round(state.total_paid, 6),
        }


# === Convenience functions ===

def _append(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(record, default=str) + "\n")
