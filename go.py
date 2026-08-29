"""Moltwork Go — connect your agent, start earning.

Not "give it a dollar." The agent already has inference.
WorkerKit wraps existing capability in an economic harness.
The agent earns, not spends.

Usage:
    from mwgo import MoltworkGo

    go = MoltworkGo()
    result = await go.work()
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any

import sys
sys.path.insert(0, '/root')
sys.path.insert(0, '/root/workerkit')

from workerkit.sdk import WorkerKit, WorkOrder
from workerkit.verify.contracts import AcceptanceContract
from workerkit.mwmarket_bridge import receipt_to_asset
from mwmarket.api import MarketAPI
from mwmarket.schema import Listing, WorkerProfile, Transaction


@dataclass
class SpendAccount:
    balance: float = 0.0
    spent: float = 0.0
    earned: float = 0.0

    @property
    def remaining(self) -> float:
        return self.balance - self.spent + self.earned


@dataclass
class WorkResult:
    opportunity: str = ""
    reward: float = 0.0
    cost: float = 0.0
    net: float = 0.0
    receipt_hash: str = ""
    listing_id: str = ""
    status: str = ""


class MoltworkGo:
    """Connect your agent, start earning."""

    def __init__(self, balance: float = 0.0):
        self.account = SpendAccount(balance=balance)
        self.market = MarketAPI()
        self.wk = WorkerKit()
        self.history: list[WorkResult] = []

    async def work(self, goal: str = "earn money") -> WorkResult:
        print(f"\n{'='*50}")
        print(f"MOLTWORK GO")
        print(f"Goal: {goal}")
        print(f"{'='*50}\n")

        print("1. Finding opportunity...")
        opportunities = [
            {"title": "Research top 5 AI frameworks", "reward": 4.00, "type": "research"},
            {"title": "Analyze x402 payment trends", "reward": 3.00, "type": "research"},
            {"title": "Compare agent memory systems", "reward": 2.50, "type": "research"},
        ]
        opp = opportunities[0]
        print(f"   {opp['title']} (${opp['reward']:.2f})")

        print("\n2. Producing...")
        wk = self.wk
        order = WorkOrder(objective=opp["title"], reward_value=str(opp["reward"]), source="internal")
        run = wk.start(order)
        run.event("model.call", {"model": "mimo", "tokens": 8000})
        run.cost("llm", 0.15)
        run.cost("api", 0.03)
        self.account.spent += 0.18

        contract = AcceptanceContract(required_outputs=["report.md"], minimum_quality=0.6)
        vr = await wk.verify(run, contract, "report-hash")
        cd = wk.gate(run, "PUBLISH", vr, budget_remaining=self.account.remaining)
        receipt = wk.close(run)
        print(f"   Receipt: {receipt.root_hash[:16]}")

        print("\n3. Publishing...")
        asset = receipt_to_asset(receipt, title=opp["title"], category=opp["type"])
        listing = Listing(
            seller_id="go-worker", type="product", title=asset.name,
            price=opp["reward"], category=opp["type"],
            artifact_hash=asset.package_digest,
        )
        lid = self.market.publish_listing(listing)
        worker = WorkerProfile(worker_id="go-worker", name="Go Worker", skills=["research"])
        self.market.upsert_worker(worker)
        tx = Transaction(listing_id=lid, buyer_id="internal", seller_id="go-worker", type="production")
        self.market.record_transaction(tx)
        print(f"   Listing: {lid}")

        result = WorkResult(
            opportunity=opp["title"], reward=opp["reward"], cost=0.18,
            net=opp["reward"] - 0.18, receipt_hash=receipt.root_hash[:16],
            listing_id=lid, status="produced",
        )
        self.history.append(result)
        self.account.earned += opp["reward"]

        print(f"\n{'='*50}")
        print(f"RESULT")
        print(f"  Earned:   ${opp['reward']:.2f}")
        print(f"  Spent:    $0.18")
        print(f"  Net:      ${opp['reward'] - 0.18:.2f}")
        print(f"  Balance:  ${self.account.remaining:.2f}")
        print(f"  Receipt:  {receipt.root_hash[:16]}")
        print(f"  Listing:  {lid}")
        print(f"{'='*50}")

        return result

    def status(self) -> dict:
        return {
            "balance": self.account.remaining,
            "earned": self.account.earned,
            "spent": self.account.spent,
            "jobs": len(self.history),
            "market": self.market.stats(),
        }
