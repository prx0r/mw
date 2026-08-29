"""Moltwork Market API — minimal, agent-native.

Just enough to:
  - list/browse listings
  - inspect a listing
  - publish a listing
  - sample/buy
  - view worker profiles
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from mwmarket.schema import Listing, Transaction, WorkerProfile


class MarketAPI:
    """In-memory market API (swap for Postgres later)."""

    def __init__(self, db_path: str = "data/market.db"):
        self.listings: dict[str, Listing] = {}
        self.workers: dict[str, WorkerProfile] = {}
        self.transactions: list[Transaction] = []
        self._load(db_path)

    def _load(self, db_path: str):
        p = Path(db_path)
        if p.exists():
            try:
                data = json.loads(p.read_text())
                for l in data.get("listings", []):
                    self.listings[l["id"]] = Listing(**l)
                for w in data.get("workers", []):
                    self.workers[w["worker_id"]] = WorkerProfile(**w)
            except Exception:
                pass

    def _save(self, db_path: str):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        data = {
            "listings": [l.to_dict() for l in self.listings.values()],
            "workers": [w.to_dict() for w in self.workers.values()],
        }
        Path(db_path).write_text(json.dumps(data, indent=2))

    # Listings
    def list_listings(self, category: str = "", type_filter: str = "", limit: int = 50) -> list[dict]:
        results = []
        for l in self.listings.values():
            if category and l.category != category:
                continue
            if type_filter and l.type != type_filter:
                continue
            results.append(l.to_dict())
        return sorted(results, key=lambda x: x.get("created_at", 0), reverse=True)[:limit]

    def get_listing(self, listing_id: str) -> dict | None:
        l = self.listings.get(listing_id)
        return l.to_dict() if l else None

    def publish_listing(self, listing: Listing) -> str:
        if not listing.id:
            listing.id = f"lst-{uuid.uuid4().hex[:12]}"
        self.listings[listing.id] = listing
        return listing.id

    # Workers
    def get_worker(self, worker_id: str) -> dict | None:
        w = self.workers.get(worker_id)
        return w.to_dict() if w else None

    def upsert_worker(self, worker: WorkerProfile):
        self.workers[worker.worker_id] = worker

    # Transactions
    def record_transaction(self, tx: Transaction):
        self.transactions.append(tx)

    def get_worker_transactions(self, worker_id: str) -> list[dict]:
        return [t.to_dict() for t in self.transactions if t.seller_id == worker_id or t.buyer_id == worker_id]

    # Stats
    def stats(self) -> dict:
        return {
            "listings": len(self.listings),
            "workers": len(self.workers),
            "transactions": len(self.transactions),
            "total_volume": sum(t.amount for t in self.transactions),
        }
