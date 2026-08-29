"""Hackathon Pack — domain intelligence for hackathon participation.

Extracted from hackathonhelp. Handles:
- Opportunity normalization
- Judging criteria → rubric
- Sponsor track → route
- Task generation
- Submission tracking
- Outcome recording
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from core.hashing import sha256, jcs
from opportunities.schema import Opportunity, OpportunityRoute


@dataclass
class Rubric:
    """Judging rubric extracted from criteria."""
    criteria: list[dict] = field(default_factory=list)  # [{name, weight, description}]
    total_weight: float = 1.0

    def score(self, dimension_scores: dict[str, float]) -> float:
        """Weighted score from dimension scores."""
        total = 0.0
        for c in self.criteria:
            name = c.get("name", "")
            weight = c.get("weight", 1.0)
            score = dimension_scores.get(name, 0.5)
            total += weight * score
        return total / self.total_weight if self.total_weight else 0

    def to_dict(self) -> dict:
        return {"criteria": self.criteria, "total_weight": self.total_weight}


@dataclass
class HackathonEvent:
    """Normalized hackathon event."""
    slug: str = ""
    name: str = ""
    url: str = ""
    deadline: str = ""
    sponsors: list[dict] = field(default_factory=list)
    tracks: list[dict] = field(default_factory=list)
    judging_criteria: list[str] = field(default_factory=list)
    eligibility: list[str] = field(default_factory=list)
    total_prize: float = 0.0

    def to_dict(self) -> dict:
        return {
            "slug": self.slug, "name": self.name, "url": self.url,
            "deadline": self.deadline, "sponsors": self.sponsors,
            "tracks": self.tracks, "judging_criteria": self.judging_criteria,
            "total_prize": self.total_prize,
        }


class HackathonPack:
    """Domain intelligence for hackathon participation."""

    def __init__(self):
        self._events: dict[str, HackathonEvent] = {}
        self._rubrics: dict[str, Rubric] = {}

    def normalize_event(self, raw: dict) -> Opportunity:
        """Convert raw hackathon data to normalized Opportunity."""
        event = HackathonEvent(
            slug=raw.get("slug", ""),
            name=raw.get("name", raw.get("title", "")),
            url=raw.get("url", ""),
            deadline=raw.get("deadline", ""),
            judging_criteria=raw.get("judging_criteria", []),
            total_prize=raw.get("total_prize", 0),
        )
        self._events[event.slug] = event

        # Create routes from tracks/sponsors
        routes = []
        for track in raw.get("tracks", []):
            routes.append(OpportunityRoute(
                route_id=track.get("id", track.get("name", "")),
                name=track.get("name", ""),
                description=track.get("description", ""),
                reward_usd=track.get("prize", 0),
                deadline=event.deadline,
                judging_criteria=event.judging_criteria,
            ))

        if not routes and event.total_prize > 0:
            routes.append(OpportunityRoute(
                route_id="main",
                name=event.name,
                reward_usd=event.total_prize,
                judging_criteria=event.judging_criteria,
            ))

        return Opportunity(
            id=event.slug,
            source="hackathonhelp",
            external_id=event.slug,
            url=event.url,
            kind="COMPETITION",
            domain="CODE",
            title=event.name,
            deadline=event.deadline,
            reward_model="COMPETITION_PRIZE",
            reward_usd=event.total_prize,
            acceptance_model="HUMAN_REVIEW",
            judging_criteria=event.judging_criteria,
            routes=routes,
        )

    def extract_rubric(self, judging_criteria: list[str]) -> Rubric:
        """Convert judging criteria into weighted rubric."""
        criteria = []
        weight = 1.0 / max(1, len(judging_criteria))
        for criterion in judging_criteria:
            criteria.append({
                "name": criterion,
                "weight": weight,
                "description": f"Score on {criterion}",
            })
        rubric = Rubric(criteria=criteria, total_weight=1.0)
        return rubric

    def score_submission(self, rubric: Rubric, scores: dict[str, float]) -> float:
        """Score a submission against a rubric."""
        return rubric.score(scores)

    def list_events(self) -> list[HackathonEvent]:
        return list(self._events.values())

    def get_event(self, slug: str) -> HackathonEvent | None:
        return self._events.get(slug)
