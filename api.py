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


class MarketAPI:
    """Marketplace API with full commerce lifecycle."""

    def __init__(self, db_path: str = "data/market.db"):
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

    # ─── Listings ──────────────────────────────────────────────────────

    def publish_listing(self, listing: Listing) -> str:
        if not listing.id:
            listing.id = f"lst-{os.urandom(4).hex()}" if __import__('os') else f"lst-{int(time.time())}"
        self.listings[listing.id] = listing
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
        return request.id

    def fund_request(self, request_id: str) -> bool:
        r = self.requests.get(request_id)
        if r and r.status == "open":
            r.status = "funded"
            return True
        return False

    def submit_request(self, request_id: str, receipt_hash: str, deliverable: str) -> bool:
        r = self.requests.get(request_id)
        if r and r.status == "funded":
            r.status = "submitted"
            r.receipt_hash = receipt_hash
            r.deliverable = deliverable
            return True
        return False

    def complete_request(self, request_id: str) -> bool:
        r = self.requests.get(request_id)
        if r and r.status == "submitted":
            r.status = "completed"
            return True
        return False

    def list_requests(self, status: str = "open") -> list[dict]:
        return [r.to_dict() for r in self.requests.values() if r.status == status]

    # ─── Access Grants ─────────────────────────────────────────────────

    def issue_grant(self, grant: AccessGrant) -> str:
        self.grants[grant.id] = grant
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
        return receipt.id

    # ─── Invocations ───────────────────────────────────────────────────

    def create_invocation(self, invocation: Invocation) -> str:
        self.invocations[invocation.id] = invocation
        return invocation.id

    def complete_invocation(self, inv_id: str, result_hash: str, cost: str) -> bool:
        inv = self.invocations.get(inv_id)
        if inv and inv.status in ("pending", "executing"):
            inv.status = "completed"
            inv.result_hash = result_hash
            inv.cost = cost
            return True
        return False

    # ─── Capability Leases ─────────────────────────────────────────────

    def issue_lease(self, lease: CapabilityLease) -> str:
        self.leases[lease.id] = lease
        return lease.id

    def check_lease(self, lease_id: str) -> bool:
        l = self.leases.get(lease_id)
        return l.is_valid() if l else False

    def revoke_lease(self, lease_id: str) -> bool:
        l = self.leases.get(lease_id)
        if l:
            l.revoked = True
            return True
        return False

    # ─── Boards ────────────────────────────────────────────────────────

    def create_board(self, board: Board) -> str:
        self.boards[board.id] = board
        return board.id

    def list_boards(self, visibility: str = "PUBLIC") -> list[dict]:
        return [b.to_dict() for b in self.boards.values() if b.visibility == visibility]

    def place_on_board(self, grant: DistributionGrant) -> str:
        self.distribution_grants[grant.id] = grant
        return grant.id

    # ─── Assets ────────────────────────────────────────────────────────

    def register_asset(self, asset: AssetVersion) -> str:
        self.assets[asset.id] = asset
        return asset.id

    def get_asset(self, asset_id: str) -> dict | None:
        a = self.assets.get(asset_id)
        return a.to_dict() if a else None

    # ─── Settlement ────────────────────────────────────────────────────

    def settle(self, plan: SettlementPlan) -> str:
        self.settlements.append(plan)
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
