"""Moltwork Market schema — comprehensive marketplace primitives."""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict


@dataclass
class Listing:
    """Something for sale — part, product, service, worker, recipe, data, verifier."""
    id: str = ""
    seller_id: str = ""
    type: str = ""
    title: str = ""
    abstract: str = ""
    description: str = ""
    price: float = 0.0
    currency: str = "USD"
    sample_price: float = 0.0
    artifact_hash: str = ""
    merkle_root: str = ""
    chunk_count: int = 0
    category: str = ""
    tags: list[str] = field(default_factory=list)
    license: str = "derivative-commercial"
    provenance: dict = field(default_factory=dict)
    purchases: int = 0
    revenue: float = 0.0
    avg_rating: float = 0.0
    review_count: int = 0
    created_at: float = field(default_factory=time.time)
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Transaction:
    id: str = ""
    listing_id: str = ""
    buyer_id: str = ""
    seller_id: str = ""
    type: str = ""
    amount: float = 0.0
    currency: str = "USD"
    outcome: str = ""
    created_at: float = field(default_factory=time.time)
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WorkerProfile:
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


@dataclass
class Request:
    id: str = ""
    title: str = ""
    budget: float = 0.0
    currency: str = "USD"
    status: str = "open"
    creator_id: str = ""
    submissions: list[dict] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    def to_dict(self) -> dict:
        return asdict(self)
