"""Venues — where work happens. Chain-neutral, runtime-neutral.

Every marketplace, bounty board, ACP network, or direct client
is a Venue. WorkerKit doesn't care which one generated the demand.

Usage:
    venue = VirtualsACPVenue(api_key="...")
    opps = venue.discover()
    ref = venue.submit(work_order, artifact)
    outcome = venue.status(ref)
"""
from __future__ import annotations

from .base import WorkVenue, Opportunity, SubmissionRef, Outcome, Settlement
from .moltwork import MoltworkVenue
from .virtuals import VirtualsACPVenue
from .github import GitHubVenue

__all__ = [
    "WorkVenue", "Opportunity", "SubmissionRef", "Outcome", "Settlement",
    "MoltworkVenue", "VirtualsACPVenue", "GitHubVenue",
]
