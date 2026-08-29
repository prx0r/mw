"""x402 Payment Provider — micropayment adapter.

Uses x402 v2 protocol for per-invocation payments.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from core.hashing import sha256, jcs


@dataclass
class PaymentRequirements:
    """What the seller requires for a payment."""
    amount: str = ""  # e.g. "1.00"
    currency: str = "USDC"
    network: str = "base"
    recipient: str = ""
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "amount": self.amount,
            "currency": self.currency,
            "network": self.network,
            "recipient": self.recipient,
            "description": self.description,
        }


@dataclass
class PaymentPayload:
    """The client's payment proof."""
    tx_hash: str = ""
    from_address: str = ""
    amount: str = ""
    currency: str = ""
    network: str = ""
    timestamp: float = 0.0

    def to_dict(self) -> dict:
        return {
            "tx_hash": self.tx_hash,
            "from_address": self.from_address,
            "amount": self.amount,
            "currency": self.currency,
            "network": self.network,
            "timestamp": self.timestamp,
        }


@dataclass
class PaymentReceipt:
    """Proof of payment linked to an invocation."""
    payment_id: str = ""
    invocation_id: str = ""
    requirements: PaymentRequirements = field(default_factory=PaymentRequirements)
    payload: PaymentPayload = field(default_factory=PaymentPayload)
    verified: bool = False
    settled: bool = False
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "payment_id": self.payment_id,
            "invocation_id": self.invocation_id,
            "requirements": self.requirements.to_dict(),
            "payload": self.payload.to_dict(),
            "verified": self.verified,
            "settled": self.settled,
        }


class X402Provider:
    """x402 v2 payment adapter.

    Handles: quote → verify → settle → refund
    """

    def __init__(self, facilitator_url: str = ""):
        self.facilitator_url = facilitator_url
        self._payments: dict[str, PaymentReceipt] = {}

    def quote(self, amount: str, currency: str = "USDC", network: str = "base",
              recipient: str = "", description: str = "") -> PaymentRequirements:
        """Generate payment requirements for a given amount."""
        return PaymentRequirements(
            amount=amount,
            currency=currency,
            network=network,
            recipient=recipient,
            description=description,
        )

    def verify(self, requirements: PaymentRequirements, payload: PaymentPayload) -> bool:
        """Verify a payment payload against requirements.

        In production, calls x402 facilitator /verify endpoint.
        """
        # Basic validation
        if payload.amount != requirements.amount:
            return False
        if payload.currency != requirements.currency:
            return False
        if payload.network != requirements.network:
            return False
        if not payload.tx_hash:
            return False

        # In production: verify on-chain
        return True

    def settle(self, payment_id: str) -> bool:
        """Settle a verified payment.

        In production, calls x402 facilitator /settle endpoint.
        """
        receipt = self._payments.get(payment_id)
        if not receipt or not receipt.verified:
            return False
        receipt.settled = True
        return True

    def refund(self, payment_id: str) -> bool:
        """Refund a payment."""
        receipt = self._payments.get(payment_id)
        if not receipt:
            return False
        receipt.settled = False
        return True

    def record_payment(self, invocation_id: str, requirements: PaymentRequirements,
                       payload: PaymentPayload) -> PaymentReceipt:
        """Record a payment for an invocation."""
        payment_id = f"pay-{len(self._payments)}"
        receipt = PaymentReceipt(
            payment_id=payment_id,
            invocation_id=invocation_id,
            requirements=requirements,
            payload=payload,
            verified=self.verify(requirements, payload),
        )
        self._payments[payment_id] = receipt
        return receipt

    def get_payment(self, payment_id: str) -> PaymentReceipt | None:
        return self._payments.get(payment_id)

    def list_payments(self, invocation_id: str = "") -> list[PaymentReceipt]:
        if invocation_id:
            return [p for p in self._payments.values() if p.invocation_id == invocation_id]
        return list(self._payments.values())
