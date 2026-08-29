"""Lease — cryptographic lease object.

Bounded rights to invoke a Worker without exposing private state.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from core.hashing import sha256, jcs, SCHEMA_LEASE


@dataclass
class LeaseLimits:
    """What the lessee is allowed to do."""
    max_invocations: int = 10
    max_spend_usd: float = 10.0
    max_run_spend_usd: float = 5.0
    max_duration_hours: float = 24.0


@dataclass
class LeasePermissions:
    """Tool and network permissions."""
    tools: list[str] = field(default_factory=list)
    network_domains: list[str] = field(default_factory=list)
    wallet_max_value_usd: float = 0.0


@dataclass
class LeaseRevenue:
    """Revenue split between owner and renter."""
    owner_bps: int = 8000  # basis points (80%)
    renter_bps: int = 2000  # basis points (20%)


@dataclass
class Lease:
    """Cryptographic lease object.

    Proves: second principal invokes Worker without receiving private state.
    """
    schema: str = SCHEMA_LEASE
    lease_id: str = ""
    asset_version_digest: str = ""  # which worker version

    lessor: str = ""  # owner address/ID
    lessee: str = ""  # renter address/ID

    valid_from: float = 0.0
    valid_until: float = 0.0

    limits: LeaseLimits = field(default_factory=LeaseLimits)
    permissions: LeasePermissions = field(default_factory=LeasePermissions)
    revenue: LeaseRevenue = field(default_factory=LeaseRevenue)

    nonce: str = ""  # prevents replay
    created_at: float = field(default_factory=time.time)

    # State
    invocations_used: int = 0
    spend_used: float = 0.0
    revoked: bool = False

    def lease_hash(self) -> str:
        """Content-addressed hash of the lease terms."""
        d = {
            "schema": self.schema,
            "lease_id": self.lease_id,
            "asset_version_digest": self.asset_version_digest,
            "lessor": self.lessor,
            "lessee": self.lessee,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            "limits": {
                "max_invocations": self.limits.max_invocations,
                "max_spend_usd": self.limits.max_spend_usd,
                "max_run_spend_usd": self.limits.max_run_spend_usd,
            },
            "permissions": {
                "tools": self.permissions.tools,
                "network_domains": self.permissions.network_domains,
            },
            "nonce": self.nonce,
        }
        return sha256(jcs(d))

    def is_valid(self) -> bool:
        """Check if lease is valid and not exhausted."""
        if self.revoked:
            return False
        now = time.time()
        if now < self.valid_from:
            return False
        if self.valid_until > 0 and now > self.valid_until:
            return False
        if self.invocations_used >= self.limits.max_invocations:
            return False
        if self.spend_used >= self.limits.max_spend_usd:
            return False
        return True

    def can_invoke(self) -> bool:
        """Check if lessee can make another call."""
        return self.is_valid()

    def record_invocation(self, cost_usd: float = 0.0) -> bool:
        """Record a lease invocation. Returns True if valid."""
        if not self.can_invoke():
            return False
        self.invocations_used += 1
        self.spend_used += cost_usd
        return True

    def revoke(self) -> None:
        """Revoke the lease."""
        self.revoked = True

    def to_dict(self) -> dict:
        d = {
            "schema": self.schema,
            "lease_id": self.lease_id,
            "asset_version_digest": self.asset_version_digest,
            "lessor": self.lessor,
            "lessee": self.lessee,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            "limits": {
                "max_invocations": self.limits.max_invocations,
                "max_spend_usd": self.limits.max_spend_usd,
                "max_run_spend_usd": self.limits.max_run_spend_usd,
            },
            "permissions": {
                "tools": self.permissions.tools,
                "network_domains": self.permissions.network_domains,
                "wallet_max_value_usd": self.permissions.wallet_max_value_usd,
            },
            "revenue": {
                "owner_bps": self.revenue.owner_bps,
                "renter_bps": self.revenue.renter_bps,
            },
            "nonce": self.nonce,
            "invocations_used": self.invocations_used,
            "spend_used": self.spend_used,
            "revoked": self.revoked,
        }
        d["lease_hash"] = self.lease_hash()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Lease":
        limits = LeaseLimits(**d.get("limits", {}))
        permissions = LeasePermissions(**d.get("permissions", {}))
        revenue = LeaseRevenue(**d.get("revenue", {}))
        return cls(
            lease_id=d.get("lease_id", ""),
            asset_version_digest=d.get("asset_version_digest", ""),
            lessor=d.get("lessor", ""),
            lessee=d.get("lessee", ""),
            valid_from=d.get("valid_from", 0),
            valid_until=d.get("valid_until", 0),
            limits=limits,
            permissions=permissions,
            revenue=revenue,
            nonce=d.get("nonce", ""),
            invocations_used=d.get("invocations_used", 0),
            spend_used=d.get("spend_used", 0),
            revoked=d.get("revoked", False),
        )


class LeaseManager:
    """Manage CapabilityLeases."""

    def __init__(self):
        self.leases: dict[str, Lease] = {}
        self.invocations: dict[str, dict] = {}

    def create_lease(self, worker_id: str, owner_id: str, lessee_id: str,
                     max_calls: int = 3, max_spend: float = 1.0,
                     duration_hours: float = 1.0) -> Lease:
        lease = Lease(
            lease_id=f"lease-{len(self.leases)}",
            asset_version_digest=worker_id,
            lessor=owner_id,
            lessee=lessee_id,
            valid_until=time.time() + duration_hours * 3600,
        )
        lease.limits.max_invocations = max_calls
        lease.limits.max_spend_usd = max_spend
        self.leases[lease.lease_id] = lease
        return lease

    def invoke(self, lease_id: str, lessee_id: str,
               artifact_hash: str = "", cost_usd: float = 0.0) -> dict | None:
        lease = self.leases.get(lease_id)
        if not lease or not lease.can_invoke():
            return None
        if lease.lessee != lessee_id:
            return None
        if not lease.record_invocation(cost_usd):
            return None
        inv = {"lease_id": lease_id, "lessee_id": lessee_id,
               "artifact_hash": artifact_hash, "cost_usd": cost_usd}
        self.invocations[f"inv-{len(self.invocations)}"] = inv
        return inv

    def get_lease(self, lease_id: str) -> Lease | None:
        return self.leases.get(lease_id)
