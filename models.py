"""Moltwork Market models — unified canonical primitives.

Slice 0: Fixed SHA-256, unified schemas, immutability enforcement.
Slice 1: Immutable AssetVersion with content commitments.
Slice 2: SampleReceipt with Merkle proof + payment reference.
Slice 3: Invocation (service execution).
Slice 4: Request with ERC-8183 lifecycle.
Slice 6: CapabilityLease with quota + expiry.
Slice 8: Board + DistributionGrant.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field, asdict


def uid() -> str:
    return f"mw_{os.urandom(8).hex()}"


def sha256(data: str | bytes) -> str:
    """Full SHA-256 — 64 hex characters."""
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


def content_hash(content: bytes) -> str:
    return sha256(content)


# ─── AssetVersion — immutable production asset ────────────────────────

@dataclass
class AssetVersion:
    """Immutable production asset. Never changes after creation.

    Any material change creates a new version, never edits the old one.
    """
    id: str = field(default_factory=lambda: f"av_{os.urandom(4).hex()}")
    version: str = "1.0"
    kind: str = ""  # ARTIFACT | DATA | PROCESS | SKILL | STACK | WORKER | VERIFIER | SERVICE
    owner_id: str = ""

    # Identity
    name: str = ""
    description: str = ""
    capability_namespace: str = ""

    # Package
    package_uri: str = ""
    package_sha256: str = ""

    # Interfaces
    input_schema_digest: str = ""
    output_schema_digest: str = ""

    # Worker binding
    worker_manifest_digest: str = ""

    # Lineage
    parent_assets: list[str] = field(default_factory=list)
    originating_receipts: list[str] = field(default_factory=list)

    # Licensing
    license_digest: str = "derivative-commercial"
    disclosure: str = "PUBLIC"  # PUBLIC | PRIVATE | ENCRYPTED

    # Content commitment
    chunking_scheme: str = "mw-text-v1"
    merkle_root: str = ""
    chunk_count: int = 0

    created_at: float = field(default_factory=time.time)

    def content_manifest(self) -> str:
        """SHA-256 of the immutable content manifest."""
        return sha256(json.dumps({
            "id": self.id, "version": self.version, "kind": self.kind,
            "ownerId": self.owner_id, "name": self.name,
            "packageSha256": self.package_sha256,
            "merkleRoot": self.merkle_root,
            "parentAssets": sorted(self.parent_assets),
        }, sort_keys=True))

    def to_dict(self) -> dict:
        return asdict(self)


# ─── Listing — market terms separate from assets ──────────────────────

@dataclass
class Listing:
    """Market terms for an asset."""
    id: str = field(default_factory=lambda: f"lst_{os.urandom(4).hex()}")
    asset_id: str = ""
    seller_id: str = ""
    status: str = "ACTIVE"  # ACTIVE | PAUSED | RETIRED
    delivery: str = "PROGRESSIVE_REVEAL"  # LICENSED_DOWNLOAD | PROGRESSIVE_REVEAL | HOSTED_INVOCATION | HOSTED_LEASE | CONFIDENTIAL_LEASE
    transport: str = "HTTP"  # HTTP | MCP | A2A
    price_model: str = "FIXED"  # FIXED | PER_UNIT | PER_CALL | PER_PERIOD
    price_amount: str = "0.00"
    price_currency: str = "USDC"
    sample_enabled: bool = True
    sample_units: int = 40
    sample_free_units: int = 1
    assurance_level: str = "SIGNED"  # SIGNED | ATTESTED | VERIFIED | VALIDATED
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


# ─── AccessGrant — unified authorization ──────────────────────────────

@dataclass
class AccessGrant:
    """Proof of purchase/access. One unified authorization for all product types."""
    id: str = field(default_factory=lambda: f"ag_{os.urandom(4).hex()}")
    principal: str = ""  # generic actor identity
    buyer_id: str = ""  # alias for principal
    listing_id: str = ""
    asset_id: str = ""
    asset_version_ref: str = ""
    rights: str = ""  # SAMPLE | FULL_READ | INVOKE | LEASE
    units_owned: list[int] = field(default_factory=list)
    quotas: dict = field(default_factory=lambda: {"calls_remaining": None})
    payment_refs: list[str] = field(default_factory=list)
    terms_digest: str = ""
    issued_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    signature: str = ""

    def is_valid(self) -> bool:
        if self.expires_at > 0 and time.time() > self.expires_at:
            return False
        if self.quotas.get("calls_remaining") is not None and self.quotas["calls_remaining"] <= 0:
            return False
        return True

    def consume_call(self) -> bool:
        """Consume one call from quota. Returns False if exhausted."""
        if self.quotas.get("calls_remaining") is None:
            return True
        if self.quotas["calls_remaining"] <= 0:
            return False
        self.quotas["calls_remaining"] -= 1
        return True

    def to_dict(self) -> dict:
        return asdict(self)


# ─── SampleReceipt — cryptographic receipt for progressive reveal ─────

@dataclass
class SampleReceipt:
    """Cryptographic receipt for a progressive reveal purchase.

    Contains Merkle proof, cumulative ownership, payment reference.
    """
    id: str = field(default_factory=lambda: f"sr_{os.urandom(4).hex()}")
    asset_id: str = ""
    listing_id: str = ""
    buyer_id: str = ""
    chunk_index: int = 0
    merkle_proof: list[dict] = field(default_factory=list)
    cumulative_units: int = 0
    total_units: int = 0
    amount_paid: str = "0"
    payment_ref: str = ""
    created_at: float = field(default_factory=time.time)

    def verify(self, merkle_root: str, leaf_hash: str) -> bool:
        """Verify this receipt's Merkle proof."""
        current = leaf_hash
        for step in self.merkle_proof:
            sibling = step.get("hash", "")
            side = step.get("side", "")
            if side == "right" and sibling:
                a, b = (current, sibling) if current < sibling else (sibling, current)
                current = sha256(f"{a}:{b}")
            elif side == "left" and sibling:
                a, b = (sibling, current) if sibling < current else (current, sibling)
                current = sha256(f"{a}:{b}")
        return current == merkle_root

    def to_dict(self) -> dict:
        return asdict(self)


# ─── Invocation — service execution request ───────────────────────────

@dataclass
class Invocation:
    """Service execution request."""
    id: str = field(default_factory=lambda: f"inv_{os.urandom(4).hex()}")
    service_asset_id: str = ""
    buyer_id: str = ""
    input_digest: str = ""
    work_order_digest: str = ""
    output_artifact_ref: str = ""
    work_receipt_ref: str = ""
    status: str = "pending"  # pending | executing | completed | failed
    result_hash: str = ""
    cost: str = "0"
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


# ─── Request — ERC-8183 compatible job lifecycle ──────────────────────

@dataclass
class Request:
    """Job request with ERC-8183 lifecycle."""
    id: str = field(default_factory=lambda: f"rq_{os.urandom(4).hex()}")
    title: str = ""
    description: str = ""
    creator_id: str = ""
    budget: str = "0"
    currency: str = "USDC"
    status: str = "open"  # open | funded | submitted | completed | rejected | expired
    evaluation_mode: str = "single"  # single | commit_reveal | multi_judge
    required_trust_level: str = "SIGNED"
    provider_id: str = ""
    evaluator_id: str = ""
    receipt_hash: str = ""
    deliverable: str = ""
    submission_salt: str = ""  # for commit/reveal
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


# ─── CapabilityLease — bounded access with quota/expiry ───────────────

@dataclass
class CapabilityLease:
    """Bounded access to a capability with quota, expiry, revocation."""
    id: str = field(default_factory=lambda: f"cl_{os.urandom(4).hex()}")
    asset_id: str = ""
    lessor_id: str = ""  # owner granting lease
    lessee_id: str = ""  # agent receiving lease
    rights: str = "INVOKE"  # INVOKE | LEASE
    max_calls: int = 100
    calls_used: int = 0
    max_spend_usdc: str = "5.00"
    spend_used: str = "0"
    valid_from: float = field(default_factory=time.time)
    valid_until: float = 0.0
    revoked: bool = False
    revocation_epoch: int = 0
    tee_signer: str = ""  # TEE-derived key if confidential
    created_at: float = field(default_factory=time.time)

    def is_valid(self) -> bool:
        if self.revoked:
            return False
        now = time.time()
        if now < self.valid_from:
            return False
        if self.valid_until > 0 and now > self.valid_until:
            return False
        if self.calls_used >= self.max_calls:
            return False
        return True

    def consume_call(self, cost: str = "0") -> bool:
        if not self.is_valid():
            return False
        self.calls_used += 1
        return True

    def to_dict(self) -> dict:
        return asdict(self)


# ─── Board — discovery + distribution surface ─────────────────────────

@dataclass
class Board:
    """Discovery and distribution surface."""
    id: str = field(default_factory=lambda: f"bd_{os.urandom(4).hex()}")
    owner_id: str = ""
    name: str = ""
    description: str = ""
    visibility: str = "PUBLIC"  # PUBLIC | PRIVATE | UNLISTED
    selector: dict = field(default_factory=lambda: {
        "asset_kinds": [],
        "capabilities": [],
        "assurance": {"min_level": "SIGNED"},
    })
    ranking_policy: str = "relevance"
    fee_policy: dict = field(default_factory=lambda: {
        "curator_bps": 300,
        "protocol_bps": 300,
        "seller_bps": 9400,
    })
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


# ─── DistributionGrant — board placement with revenue splits ─────────

@dataclass
class DistributionGrant:
    """Links a Listing to a Board with revenue splits."""
    id: str = field(default_factory=lambda: f"dg_{os.urandom(4).hex()}")
    listing_id: str = ""
    board_id: str = ""
    seller_bps: int = 9400
    board_bps: int = 300
    protocol_bps: int = 300
    status: str = "active"
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


# ─── SettlementPlan — payment allocation ──────────────────────────────

@dataclass
class SettlementPlan:
    """Deterministic allocation record splitting payments."""
    id: str = field(default_factory=lambda: f"sp_{os.urandom(4).hex()}")
    transaction_id: str = ""
    total_amount: str = "0"
    currency: str = "USDC"
    allocations: list[dict] = field(default_factory=list)  # [{recipient, amount, basis_points}]
    settled: bool = False
    settled_at: float = 0.0
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


# ─── WorkerProfile ────────────────────────────────────────────────────

@dataclass
class WorkerProfile:
    """Evidence-backed worker history."""
    worker_id: str = ""
    name: str = ""
    description: str = ""
    total_earned: float = 0.0
    jobs_completed: int = 0
    jobs_accepted: int = 0
    products_published: int = 0
    skills: list[str] = field(default_factory=list)
    capabilities: list[dict] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


# ─── Review (secondary to machine signals) ────────────────────────────

@dataclass
class Review:
    """Human review — secondary to machine-verified evidence."""
    id: str = field(default_factory=lambda: f"rv_{os.urandom(4).hex()}")
    listing_id: str = ""
    reviewer_id: str = ""
    rating: float = 0.0
    comment: str = ""
    verified_purchase: bool = False
    evidence_refs: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)
