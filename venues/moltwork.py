"""MoltworkVenue — native Moltwork marketplace.

The internal venue. Opportunities come from the Oracle.
Submissions go through WorkerKit. Settlement is internal.
"""
from __future__ import annotations

import json
import time
from typing import Any

from .base import Opportunity, SubmissionRef, Outcome, Settlement


class MoltworkVenue:
    """Native Moltwork marketplace venue.

    Opportunities are sourced from the Oracle.
    Submissions produce WorkerKit receipts.
    Settlement is internal accounting.
    """

    def __init__(self, oracle_db: str = "data/oracle.db"):
        self.venue_id = "moltwork"
        self.oracle_db = oracle_db

    def discover(self) -> list[Opportunity]:
        """Find opportunities from the Oracle."""
        try:
            from oracle.store import get_opps_by_task_family, q
            rows = q("""SELECT * FROM oracle_opps WHERE status = 'open'
                ORDER BY reward_usd DESC LIMIT 50""")
            return [self._row_to_opp(r) for r in rows]
        except Exception:
            return []

    def inspect(self, opportunity_id: str) -> Opportunity | None:
        """Get one opportunity from the Oracle."""
        try:
            from oracle.store import q1
            row = q1("SELECT * FROM oracle_opps WHERE id=?", (opportunity_id,))
            if row:
                return self._row_to_opp(row)
        except Exception:
            pass
        return None

    def submit(self, opportunity_id: str, artifact_hash: str = "",
               artifact_content: bytes = b"") -> SubmissionRef | None:
        """Submit work through WorkerKit.

        In practice, the orchestrator handles this.
        This method is for direct venue interaction.
        """
        return SubmissionRef(
            submission_id=f"mw-sub:{opportunity_id}",
            venue=self.venue_id,
            opportunity_id=opportunity_id,
            artifact_hash=artifact_hash,
            status="submitted",
        )

    def status(self, submission_id: str) -> Outcome | None:
        """Check outcome via WorkerKit receipt."""
        # In production, query the receipt database
        return Outcome(
            submission_id=submission_id,
            status="pending",
        )

    def settle(self, submission_id: str) -> Settlement | None:
        """Settle internally."""
        return Settlement(
            submission_id=submission_id,
            method="internal",
            settled_at=time.time(),
        )

    def _row_to_opp(self, row: dict) -> Opportunity:
        caps = []
        try:
            caps = json.loads(row.get("canonical_capabilities", "[]"))
        except:
            pass
        return Opportunity(
            id=row.get("id", ""),
            venue=self.venue_id,
            title=row.get("canonical_title", ""),
            description=row.get("canonical_description", ""),
            task_family=row.get("task_family", ""),
            capabilities=caps,
            reward_usd=row.get("reward_usd", 0) or 0,
            currency=row.get("reward_currency", "USD"),
            source_url=row.get("canonical_url", ""),
        )
