"""Bridge: WorkerKit → Moltwork Market.

Produces an AssetVersion from a completed WorkReceipt.
"""
from __future__ import annotations

import sys
sys.path.insert(0, '/root')

from workerkit.core.schema import WorkReceipt
from mwmarket.models import AssetVersion


def receipt_to_asset(receipt: WorkReceipt, title: str = "", category: str = "report") -> AssetVersion:
    """Convert a WorkReceipt into an AssetVersion for the market."""
    return AssetVersion(
        kind="ARTIFACT",
        name=title,
        description=f"Produced by WorkerKit run {receipt.run_id}",
        capability_namespace=f"work.{category}",
        package_digest=receipt.root_hash,
        disclosure="PUBLIC",
        originating_receipts=[receipt.run_id],
    )
