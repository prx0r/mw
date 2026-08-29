"""Moltwork Market models — AssetVersion, Listing, AccessGrant, etc."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field, asdict


def uid() -> str:
    return f"mw_{int(time.time())}_{os.urandom(4).hex()}" if __import__('os') else f"mw_{int(time.time())}"

import os


def sha256(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()[:16]


@dataclass
class AssetVersion:
    """Immutable production asset. Never changes after creation."""
    id: str = field(default_factory=lambda: f"av_{os.urandom(4).hex()}")
    version: str = "1.0"
    kind: str = ""  # ARTIFACT | DATA | PROCESS | SKILL | WORKER | VERIFIER | SERVICE
    owner_id: str = ""
    name: str = ""
    description: str = ""
    capability_namespace: str = ""
    capability_description: str = ""
    package_digest: str = ""
    package_uri: str = ""
    input_schema: dict = field(default_factory=dict)
    output_schema: dict = field(default_factory=dict)
    parent_assets: list[str] = field(default_factory=list)
    originating_receipts: list[str] = field(default_factory=list)
    license: str = "derivative-commercial"
    disclosure: str = "PUBLIC"
    merkle_root: str = ""
    chunk_count: int = 0
    created_at: float = field(default_factory=time.time)
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Listing:
    """Market terms for an asset."""
    id: str = field(default_factory=lambda: f"lst_{os.urandom(4).hex()}")
    asset_id: str = ""
    status: str = "ACTIVE"
    delivery: str = "DOWNLOAD"  # DOWNLOAD | PROGRESSIVE_REVEAL | HOSTED | LEASED | CONFIDENTIAL
    transport: str = "HTTP"  # HTTP | MCP | A2A
    price_model: str = "FIXED"  # FIXED | PER_CALL | PER_UNIT | PER_PERIOD
    price_amount: str = "0.00"
    price_currency: str = "USDC"
    sample_enabled: bool = True
    sample_units: int = 40
    sample_free_units: int = 1
    assurance_level: str = "SIGNED"
    seller_id: str = ""
    created_at: float = field(default_factory=time.time)
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AccessGrant:
    """Proof of purchase/access."""
    id: str = field(default_factory=lambda: f"ag_{os.urandom(4).hex()}")
    buyer_id: str = ""
    listing_id: str = ""
    asset_id: str = ""
    rights: str = ""  # SAMPLE | FULL_READ | INVOKE | LEASE
    units_owned: list[int] = field(default_factory=list)
    payment_ref: str = ""
    issued_at: float = field(default_factory=time.time)
    def to_dict(self) -> dict:
        return asdict(self)


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


@dataclass
class Review:
    id: str = ""
    listing_id: str = ""
    reviewer_id: str = ""
    rating: float = 0.0
    comment: str = ""
    verified: bool = False
    created_at: float = field(default_factory=time.time)
    def to_dict(self) -> dict:
        return asdict(self)
