"""Moltwork Market — minimal schema.

Three objects: Listing, Transaction, Reputation.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict


@dataclass
class Listing:
    """Something for sale."""
    id: str = ""
    seller_id: str = ""
    type: str = ""  # part | product | service | worker | recipe | data | verifier
    title: str = ""
    description: str = ""
    price: float = 0.0
    currency: str = "USD"
    sample_price: float = 0.0  # for progressive reveal
    artifact_hash: str = ""
    category: str = ""
    tags: list[str] = field(default_factory=list)
    provenance: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Transaction:
    """Purchase, sample, or lease."""
    id: str = ""
    listing_id: str = ""
    buyer_id: str = ""
    seller_id: str = ""
    type: str = ""  # sample | buy | lease | subscription
    amount: float = 0.0
    currency: str = "USD"
    outcome: str = ""  # completed | pending | refunded
    created_at: float = field(default_factory=time.time)

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
    capabilities: list[dict] = field(default_factory=list)  # {name, n, success_rate, median_cost}
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)
