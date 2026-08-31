"""VirtualsACPVenue — wraps Virtuals ACP behind WorkVenue interface.

Virtuals' agent-commerce-protocol is MIT licensed.
This adapter reuses their job lifecycle semantics without forking.

Key Virtuals concepts reused:
- Account → Job → Memos separation
- Service discovery
- Job accept/reject/perform/deliver lifecycle

NOT reused:
- Their wallet infrastructure
- Chain-specific assumptions
- Token-centric worldview
"""
from __future__ import annotations

import json
import time
from typing import Any

from .base import Opportunity, SubmissionRef, Outcome, Settlement


class VirtualsACPVenue:
    """Virtuals ACP adapter. Thin wrapper around their API.

    In production, this calls the Virtuals ACP API.
    For now, it's a structural placeholder that shows the interface.
    """

    def __init__(self, api_key: str = "", base_url: str = "https://acp.virtuals.io"):
        self.venue_id = "virtuals-acp"
        self.api_key = api_key
        self.base_url = base_url

    def discover(self) -> list[Opportunity]:
        """Discover ACP job opportunities.

        In production: GET /v1/jobs?status=open
        Maps Virtuals job format → Moltwork Opportunity.
        """
        # Structural placeholder — real implementation calls their API
        # Virtuals ACP jobs have: provider, offering, price, requirements, evaluator
        return []

    def inspect(self, opportunity_id: str) -> Opportunity | None:
        """Inspect an ACP job.

        In production: GET /v1/jobs/{id}
        """
        return None

    def submit(self, opportunity_id: str, artifact_hash: str = "",
               artifact_content: bytes = b"") -> SubmissionRef | None:
        """Submit to an ACP job.

        In production: POST /v1/jobs/{id}/submit
        Virtuals flow: accept job → perform → deliver artifact
        """
        return SubmissionRef(
            submission_id=f"v-acp:{opportunity_id}",
            venue=self.venue_id,
            opportunity_id=opportunity_id,
            artifact_hash=artifact_hash,
            status="submitted",
        )

    def status(self, submission_id: str) -> Outcome | None:
        """Check ACP job outcome.

        In production: GET /v1/submissions/{id}
        """
        return Outcome(submission_id=submission_id, status="pending")

    def settle(self, submission_id: str) -> Settlement | None:
        """Settle ACP payment.

        In production: POST /v1/submissions/{id}/settle
        Virtuals uses on-chain settlement (x402/ACP tokens).
        """
        return Settlement(
            submission_id=submission_id,
            method="virtuals-acp",
            settled_at=time.time(),
        )
