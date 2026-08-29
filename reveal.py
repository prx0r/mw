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

    def reveal_next(self, artifact_id: str, buyer_id: str,
                    payment_proof: str | None = None) -> RevealResult | None:
        """Reveal the next chunk. Requires payment_proof — no fake paid state."""
        state = self._states.get(artifact_id, {}).get(buyer_id)
        if not state:
            return None

        if state.units_purchased >= len(state.reveal_order):
            return None

        # Payment verification — reject if no proof provided
        if payment_proof is None:
            raise PaymentRequired(
                artifact_id=artifact_id,
                amount=self._reveal_prices[artifact_id],
                message="x402 payment required for reveal",
            )

        if not self._verify_payment(payment_proof, artifact_id, buyer_id):
            raise PaymentVerificationFailed(
                artifact_id=artifact_id,
                payment_proof=payment_proof,
            )

        next_idx = state.reveal_order[state.units_purchased]

        chunks = self._chunks[artifact_id]
        tree = self._trees[artifact_id]
        reveal = reveal_chunk(chunks, tree, next_idx, buyer_id)

        state.units_purchased += 1
        state.chunks_revealed.append(next_idx)
        state.last_reveal_at = time.time()
        state.total_paid += self._reveal_prices[artifact_id]
        _append(REVEALS_DB, {
            "artifact_id": artifact_id, "buyer_id": buyer_id,
            "chunk_index": next_idx, "payment_proof": payment_proof,
            "total_paid": state.total_paid,
        })

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

    def reveal_next_unverified(self, artifact_id: str, buyer_id: str) -> RevealResult | None:
        """Dev/test helper — reveal without payment. Never use in production."""
        import warnings
        warnings.warn("reveal_next_unverified: no payment verification — dev only", UserWarning)
        return self._reveal_next_inner(artifact_id, buyer_id)

    def _reveal_next_inner(self, artifact_id: str, buyer_id: str) -> RevealResult | None:
        state = self._states.get(artifact_id, {}).get(buyer_id)
        if not state or state.units_purchased >= len(state.reveal_order):
            return None
        next_idx = state.reveal_order[state.units_purchased]
        chunks = self._chunks[artifact_id]
        tree = self._trees[artifact_id]
        reveal = reveal_chunk(chunks, tree, next_idx, buyer_id)
        state.units_purchased += 1
        state.chunks_revealed.append(next_idx)
        state.last_reveal_at = time.time()
        state.total_paid += self._reveal_prices[artifact_id]
        price_per = self._reveal_prices[artifact_id]
        remaining = len(state.reveal_order) - state.units_purchased
        return RevealResult(
            chunk_index=next_idx, content=reveal["content"], proof=reveal["proof"],
            verified=reveal["verified"], units_purchased=state.units_purchased,
            fraction_revealed=state.fraction_purchased,
            remaining_to_full=remaining * price_per,
            cost_this_reveal=price_per, total_paid=state.total_paid,
        )

    def _verify_payment(self, payment_proof: str, artifact_id: str, buyer_id: str) -> bool:
        """Verify x402 payment proof. In production: call facilitator.

        For now: accept any non-empty proof that hasn't been replayed.
        Production must replace with: x402.verify(payment_proof, expected_amount).
        """
        if not payment_proof or not payment_proof.strip():
            return False
        # Replay protection — same proof can't be used twice
        if not hasattr(self, "_used_proofs"):
            self._used_proofs: set[str] = set()
        if payment_proof in self._used_proofs:
            return False
        self._used_proofs.add(payment_proof)
        return True

    def unlock_full(self, artifact_id: str, buyer_id: str,
                    payment_proof: str | None = None) -> dict | None:
        """Buyer pays remaining balance to unlock full artifact."""
        state = self._states.get(artifact_id, {}).get(buyer_id)
        if not state:
            return None

        remaining = len(state.reveal_order) - state.units_purchased
        if remaining <= 0:
            return {"chunks": self._chunks.get(artifact_id, []), "already_unlocked": True}

        if payment_proof is None:
            raise PaymentRequired(
                artifact_id=artifact_id,
                amount=remaining * self._reveal_prices[artifact_id],
                message="x402 payment required to unlock",
            )
        if not self._verify_payment(payment_proof, artifact_id, buyer_id):
            raise PaymentVerificationFailed(artifact_id=artifact_id, payment_proof=payment_proof)

        remaining_cost = remaining * self._reveal_prices[artifact_id]
        state.total_paid += remaining_cost
        state.units_purchased = len(state.reveal_order)
        state.chunks_revealed = list(range(len(state.reveal_order)))
        state.last_reveal_at = time.time()
        _append(REVEALS_DB, {
            "artifact_id": artifact_id, "buyer_id": buyer_id,
            "action": "unlock_full", "payment_proof": payment_proof,
            "total_paid": state.total_paid,
        })

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

class PaymentRequired(Exception):
    def __init__(self, artifact_id: str, amount: float, message: str = ""):
        self.artifact_id = artifact_id
        self.amount = amount
        super().__init__(message or f"Payment of {amount} required for {artifact_id}")
        # x402-compatible headers for HTTP 402 response
        self.x402_headers = {
            "X-Payment-Required": str(amount),
            "X-Artifact-Id": artifact_id,
        }


class PaymentVerificationFailed(Exception):
    def __init__(self, artifact_id: str, payment_proof: str):
        super().__init__(f"Payment verification failed for {artifact_id}: {payment_proof[:16]}...")
        self.artifact_id = artifact_id


def _append(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(record, default=str) + "\n")
