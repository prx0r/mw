"""Moltwork Market API — comprehensive marketplace."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from mwmarket.schema import Listing, Transaction, WorkerProfile, Review, Request


class MarketAPI:
    """Marketplace API with progressive reveal, reviews, requests."""

    def __init__(self, db_path: str = "data/market.db"):
        self.listings: dict[str, Listing] = {}
        self.workers: dict[str, WorkerProfile] = {}
        self.reviews: dict[str, list[Review]] = {}
        self.requests: dict[str, Request] = {}
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

    def list_listings(self, category: str = "", type_filter: str = "", limit: int = 50) -> list[dict]:
        results = []
        for l in self.listings.values():
            if category and l.category != category: continue
            if type_filter and l.type != type_filter: continue
            results.append(l.to_dict())
        return sorted(results, key=lambda x: x.get("created_at", 0), reverse=True)[:limit]

    def get_listing(self, listing_id: str) -> dict | None:
        l = self.listings.get(listing_id)
        return l.to_dict() if l else None

    def publish_listing(self, listing: Listing) -> str:
        if not listing.id:
            listing.id = f"lst-{int(time.time())}"
        self.listings[listing.id] = listing
        return listing.id

    def import_work(self, title: str, content: str, seller_id: str = "", price: float = 0.0, category: str = "report") -> str:
        from mwmarket.commitment import create_envelope
        envelope, chunks = create_envelope(content, title, price, "USD")
        listing = Listing(
            id=envelope.artifact_id, seller_id=seller_id, type="product",
            title=title, abstract=content[:200], price=price,
            merkle_root=envelope.merkle_root, chunk_count=envelope.total_units,
            category=category, license="derivative-commercial",
        )
        self.listings[listing.id] = listing
        return listing.id

    def get_worker(self, worker_id: str) -> dict | None:
        w = self.workers.get(worker_id)
        return w.to_dict() if w else None

    def upsert_worker(self, worker: WorkerProfile):
        self.workers[worker.worker_id] = worker

    def record_transaction(self, tx: Transaction):
        self.transactions.append(tx)

    def add_review(self, review: Review):
        self.reviews.setdefault(review.listing_id, []).append(review)
        listing = self.listings.get(review.listing_id)
        if listing:
            reviews = self.reviews[review.listing_id]
            listing.review_count = len(reviews)
            listing.avg_rating = sum(r.rating for r in reviews) / len(reviews)

    def get_reviews(self, listing_id: str) -> list[dict]:
        return [r.to_dict() for r in self.reviews.get(listing_id, [])]

    def create_request(self, request: Request) -> str:
        if not request.id:
            request.id = f"req-{len(self.requests)}"
        self.requests[request.id] = request
        return request.id

    def list_requests(self, status: str = "open") -> list[dict]:
        return [r.to_dict() for r in self.requests.values() if r.status == status]

    def stats(self) -> dict:
        return {
            "listings": len(self.listings), "workers": len(self.workers),
            "reviews": sum(len(v) for v in self.reviews.values()),
            "requests": len(self.requests), "transactions": len(self.transactions),
        }

    def save(self, db_path: str = "data/market.db"):
        self._save(db_path)
