"""Moltwork Market API — unified marketplace primitives.

Uses models.py as canonical (no more schema.py duplicates).
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from mwmarket.models import (
    Listing, WorkerProfile, Review, Request,
    AccessGrant, SampleReceipt, Invocation, CapabilityLease,
    Board, DistributionGrant, SettlementPlan, AssetVersion,
)
from mwmarket.store import MarketStore


class MarketAPI:
    """Marketplace API — SQLite-backed, dict-cached."""

    def __init__(self, db_path: str = "data/market.db"):
        self._store = MarketStore(db_path)
        # In-memory cache for fast access, hydrated from SQLite
        self.listings: dict[str, Listing] = {}
        self.workers: dict[str, WorkerProfile] = {}
        self.reviews: dict[str, list[Review]] = {}
        self.requests: dict[str, Request] = {}
        self.grants: dict[str, AccessGrant] = {}
        self.receipts: list[SampleReceipt] = []
        self.invocations: dict[str, Invocation] = {}
        self.leases: dict[str, CapabilityLease] = {}
        self.boards: dict[str, Board] = {}
        self.distribution_grants: dict[str, DistributionGrant] = {}
        self.assets: dict[str, AssetVersion] = {}
        self.settlements: list[SettlementPlan] = []
        self._hydrate()

    def _hydrate(self):
        """Load all persisted state from SQLite into cache."""
        for d in self._store.list_all("assets", 1000):
            try: self.assets[d["id"]] = AssetVersion(**{k: v for k, v in d.items() if k in AssetVersion.__dataclass_fields__})
            except Exception: pass
        for d in self._store.list_all("listings", 1000):
            try: self.listings[d["id"]] = Listing(**{k: v for k, v in d.items() if k in Listing.__dataclass_fields__})
            except Exception: pass
        for d in self._store.list_all("boards", 1000):
            try: self.boards[d["id"]] = Board(**{k: v for k, v in d.items() if k in Board.__dataclass_fields__})
            except Exception: pass
        for d in self._store.list_all("leases", 1000):
            try: self.leases[d["id"]] = CapabilityLease(**{k: v for k, v in d.items() if k in CapabilityLease.__dataclass_fields__})
            except Exception: pass
        for d in self._store.list_all("requests", 1000):
            try: self.requests[d["id"]] = Request(**{k: v for k, v in d.items() if k in Request.__dataclass_fields__})
            except Exception: pass

    def _persist(self, table: str, obj_id: str, data: dict):
        try: self._store.put(table, obj_id, data)
        except Exception: pass

    # ─── Listings ──────────────────────────────────────────────────────

    def publish_listing(self, listing: Listing) -> str:
        if not listing.id:
            listing.id = f"lst-{os.urandom(4).hex()}" if __import__('os') else f"lst-{int(time.time())}"
        self.listings[listing.id] = listing
        self._persist("listings", listing.id, listing.to_dict())
        return listing.id

    def get_listing(self, listing_id: str) -> dict | None:
        l = self.listings.get(listing_id)
        return l.to_dict() if l else None

    def list_listings(self, kind: str = "", limit: int = 50) -> list[dict]:
        results = []
        for l in self.listings.values():
            if kind and l.status != kind:
                continue
            results.append(l.to_dict())
        return sorted(results, key=lambda x: x.get("created_at", 0), reverse=True)[:limit]

    # ─── Workers ───────────────────────────────────────────────────────

    def get_worker(self, worker_id: str) -> dict | None:
        w = self.workers.get(worker_id)
        return w.to_dict() if w else None

    def upsert_worker(self, worker: WorkerProfile):
        self.workers[worker.worker_id] = worker

    # ─── Reviews ───────────────────────────────────────────────────────

    def add_review(self, review: Review):
        self.reviews.setdefault(review.listing_id, []).append(review)

    def get_reviews(self, listing_id: str) -> list[dict]:
        return [r.to_dict() for r in self.reviews.get(listing_id, [])]

    # ─── Requests (ERC-8183 lifecycle) ─────────────────────────────────

    def create_request(self, request: Request) -> str:
        self.requests[request.id] = request
        self._persist("requests", request.id, request.to_dict())
        return request.id

    def fund_request(self, request_id: str) -> bool:
        r = self.requests.get(request_id)
        if r and r.status == "open":
            r.status = "funded"
            self._persist("requests", r.id, r.to_dict())
            return True
        return False

    def submit_request(self, request_id: str, receipt_hash: str, deliverable: str) -> bool:
        r = self.requests.get(request_id)
        if r and r.status == "funded":
            r.status = "submitted"
            r.receipt_hash = receipt_hash
            r.deliverable = deliverable
            self._persist("requests", r.id, r.to_dict())
            return True
        return False

    def complete_request(self, request_id: str) -> bool:
        r = self.requests.get(request_id)
        if r and r.status == "submitted":
            r.status = "completed"
            self._persist("requests", r.id, r.to_dict())
            return True
        return False

    def list_requests(self, status: str = "open") -> list[dict]:
        return [r.to_dict() for r in self.requests.values() if r.status == status]

    # ─── Access Grants ─────────────────────────────────────────────────

    def issue_grant(self, grant: AccessGrant) -> str:
        self.grants[grant.id] = grant
        self._persist("grants", grant.id, grant.to_dict())
        return grant.id

    def check_grant(self, grant_id: str, right: str = "") -> bool:
        g = self.grants.get(grant_id)
        if not g:
            return False
        if not g.is_valid():
            return False
        if right and g.rights != right:
            return False
        return True

    def consume_grant(self, grant_id: str) -> bool:
        g = self.grants.get(grant_id)
        if not g or not g.is_valid():
            return False
        return g.consume_call()

    # ─── Sample Receipts ───────────────────────────────────────────────

    def issue_sample_receipt(self, receipt: SampleReceipt) -> str:
        self.receipts.append(receipt)
        self._persist("receipts", receipt.id, receipt.to_dict())
        return receipt.id

    # ─── Invocations ───────────────────────────────────────────────────

    def create_invocation(self, invocation: Invocation) -> str:
        self.invocations[invocation.id] = invocation
        self._persist("invocations", invocation.id, invocation.to_dict())
        return invocation.id

    def complete_invocation(self, inv_id: str, result_hash: str, cost: str) -> bool:
        inv = self.invocations.get(inv_id)
        if inv and inv.status in ("pending", "executing"):
            inv.status = "completed"
            inv.result_hash = result_hash
            inv.cost = cost
            self._persist("invocations", inv.id, inv.to_dict())
            return True
        return False

    # ─── Capability Leases ─────────────────────────────────────────────

    def issue_lease(self, lease: CapabilityLease) -> str:
        self.leases[lease.id] = lease
        self._persist("leases", lease.id, lease.to_dict())
        return lease.id

    def check_lease(self, lease_id: str) -> bool:
        l = self.leases.get(lease_id)
        return l.is_valid() if l else False

    def revoke_lease(self, lease_id: str) -> bool:
        l = self.leases.get(lease_id)
        if l:
            l.revoked = True
            self._persist("leases", l.id, l.to_dict())
            return True
        return False

    # ─── Boards ────────────────────────────────────────────────────────

    def create_board(self, board: Board) -> str:
        self.boards[board.id] = board
        self._persist("boards", board.id, board.to_dict())
        return board.id

    def list_boards(self, visibility: str = "PUBLIC") -> list[dict]:
        return [b.to_dict() for b in self.boards.values() if b.visibility == visibility]

    def place_on_board(self, grant: DistributionGrant) -> str:
        self.distribution_grants[grant.id] = grant
        self._persist("distribution_grants", grant.id, grant.to_dict())
        return grant.id

    # ─── Assets ────────────────────────────────────────────────────────

    def register_asset(self, asset: AssetVersion) -> str:
        self.assets[asset.id] = asset
        self._persist("assets", asset.id, asset.to_dict())
        return asset.id

    def get_asset(self, asset_id: str) -> dict | None:
        a = self.assets.get(asset_id)
        return a.to_dict() if a else None

    # ─── Settlement ────────────────────────────────────────────────────

    def settle(self, plan: SettlementPlan) -> str:
        self.settlements.append(plan)
        self._persist("settlements", plan.id, plan.to_dict())
        return plan.id

    # ─── Stats ─────────────────────────────────────────────────────────

    def stats(self) -> dict:
        return {
            "assets": len(self.assets),
            "listings": len(self.listings),
            "workers": len(self.workers),
            "reviews": sum(len(v) for v in self.reviews.values()),
            "requests": len(self.requests),
            "grants": len(self.grants),
            "leases": len(self.leases),
            "boards": len(self.boards),
        }
