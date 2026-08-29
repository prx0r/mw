"""CapabilityLease POC — lease → invoke → receipt.

Proves: second principal invokes Worker without receiving private state.

Flow:
  1. Owner creates CapabilityLease with rights, limits, expiry
  2. Lease token issued
  3. Lessee invokes Worker
  4. Worker stays inside TEE
  5. Lessee gets Artifact + WorkReceipt
  6. Lessee NEVER gets .af, MemFS, Skills, API secrets
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict


def _sha256(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


@dataclass
class CapabilityLease:
    """Bounded rights to invoke a Worker. Proves agent leasing works."""
    lease_id: str = ""
    worker_id: str = ""
    owner_id: str = ""
    lessee_id: str = ""

    # Rights
    rights: list[str] = field(default_factory=lambda: ["INVOKE"])  # INVOKE, READ_RECEIPT, READ_ARTIFACT
    max_calls: int = 3
    max_spend_usd: float = 1.0
    expires_at: float = 0.0

    # State
    calls_used: int = 0
    spend_used: float = 0.0
    revoked: bool = False

    # TEE binding
    tee_attestation_required: bool = True

    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "lease_id": self.lease_id,
            "worker_id": self.worker_id,
            "owner_id": self.owner_id,
            "lessee_id": self.lessee_id,
            "rights": self.rights,
            "max_calls": self.max_calls,
            "max_spend_usd": self.max_spend_usd,
            "expires_at": self.expires_at,
            "calls_used": self.calls_used,
            "spend_used": self.spend_used,
            "revoked": self.revoked,
            "tee_attestation_required": self.tee_attestation_required,
            "created_at": self.created_at,
            "lease_hash": self.lease_hash(),
        }

    def lease_hash(self) -> str:
        """Content-addressed hash of the lease terms."""
        d = {
            "lease_id": self.lease_id,
            "worker_id": self.worker_id,
            "owner_id": self.owner_id,
            "lessee_id": self.lessee_id,
            "rights": self.rights,
            "max_calls": self.max_calls,
            "max_spend_usd": self.max_spend_usd,
            "expires_at": self.expires_at,
        }
        return _sha256(json.dumps(d, sort_keys=True).encode())

    def is_valid(self) -> bool:
        """Check if lease is valid and not exhausted."""
        if self.revoked:
            return False
        if self.calls_used >= self.max_calls:
            return False
        if self.spend_used >= self.max_spend_usd:
            return False
        if self.expires_at > 0 and time.time() > self.expires_at:
            return False
        return True

    def can_invoke(self) -> bool:
        """Check if lessee can make another call."""
        return self.is_valid() and "INVOKE" in self.rights

    def record_call(self, cost_usd: float = 0.0) -> bool:
        """Record a lease invocation. Returns True if valid."""
        if not self.can_invoke():
            return False
        self.calls_used += 1
        self.spend_used += cost_usd
        return True

    def revoke(self) -> None:
        """Revoke the lease."""
        self.revoked = True


@dataclass
class LeaseInvocation:
    """One invocation under a lease. Lessee gets artifact + receipt, not private state."""
    invocation_id: str = ""
    lease_id: str = ""
    run_id: str = ""
    lessee_id: str = ""

    # What lessee receives
    artifact_hash: str = ""
    receipt_hash: str = ""

    # What lessee NEVER receives
    # (worker_private_state: MemFS, .af, skills, API keys — all stay in TEE)

    cost_usd: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "invocation_id": self.invocation_id,
            "lease_id": self.lease_id,
            "run_id": self.run_id,
            "lessee_id": self.lessee_id,
            "artifact_hash": self.artifact_hash,
            "receipt_hash": self.receipt_hash,
            "cost_usd": self.cost_usd,
            "timestamp": self.timestamp,
        }


class LeaseManager:
    """Manages CapabilityLeases. Proves bounded agent leasing."""

    def __init__(self):
        self.leases: dict[str, CapabilityLease] = {}
        self.invocations: dict[str, LeaseInvocation] = {}

    def create_lease(self, worker_id: str, owner_id: str, lessee_id: str,
                     max_calls: int = 3, max_spend: float = 1.0,
                     duration_hours: float = 1.0) -> CapabilityLease:
        """Create a new lease."""
        lease = CapabilityLease(
            lease_id=f"lease-{len(self.leases)}",
            worker_id=worker_id,
            owner_id=owner_id,
            lessee_id=lessee_id,
            max_calls=max_calls,
            max_spend_usd=max_spend,
            expires_at=time.time() + duration_hours * 3600,
        )
        self.leases[lease.lease_id] = lease
        return lease

    def invoke(self, lease_id: str, lessee_id: str,
               artifact_hash: str = "", receipt_hash: str = "",
               cost_usd: float = 0.0) -> LeaseInvocation | None:
        """Invoke a worker under lease. Returns invocation or None if invalid."""
        lease = self.leases.get(lease_id)
        if not lease or not lease.can_invoke():
            return None
        if lease.lessee_id != lessee_id:
            return None

        if not lease.record_call(cost_usd):
            return None

        invocation = LeaseInvocation(
            invocation_id=f"inv-{len(self.invocations)}",
            lease_id=lease_id,
            lessee_id=lessee_id,
            artifact_hash=artifact_hash,
            receipt_hash=receipt_hash,
            cost_usd=cost_usd,
        )
        self.invocations[invocation.invocation_id] = invocation
        return invocation

    def get_lease(self, lease_id: str) -> CapabilityLease | None:
        return self.leases.get(lease_id)

    def list_leases(self, worker_id: str = "") -> list[CapabilityLease]:
        if worker_id:
            return [l for l in self.leases.values() if l.worker_id == worker_id]
        return list(self.leases.values())
