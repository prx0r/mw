"""Skill Builder — extract reusable skill candidates from trajectories.

MVP implementation: loops trajectories, extracts failure/review/decision strings,
dedupes, formats Markdown. NOT a full Trace2Skill synthesizer.

For the full algorithm, see upstream Trace2Skill paper.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from core.hashing import sha256, jcs


@dataclass
class TrajectoryLesson:
    """One lesson from a single trajectory."""
    lesson_id: str = ""
    trajectory_id: str = ""
    content: str = ""
    lesson_type: str = ""  # procedure / constraint / failure / decision
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "lesson_id": self.lesson_id,
            "trajectory_id": self.trajectory_id,
            "content": self.content,
            "lesson_type": self.lesson_type,
            "confidence": self.confidence,
        }


@dataclass
class SkillCandidate:
    """A candidate skill produced from trajectory analysis."""
    skill_id: str = ""
    name: str = ""
    description: str = ""
    content: str = ""  # SKILL.md content
    source_trajectories: list[str] = field(default_factory=list)
    lessons: list[TrajectoryLesson] = field(default_factory=list)
    hypothesis: str = ""
    status: str = "CANDIDATE"  # CANDIDATE / TESTING / PROMOTED / REJECTED
    created_at: float = field(default_factory=time.time)

    def content_hash(self) -> str:
        return sha256(jcs({
            "name": self.name,
            "content": self.content,
            "source_trajectories": self.source_trajectories,
        }))

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "content": self.content,
            "source_trajectories": self.source_trajectories,
            "hypothesis": self.hypothesis,
            "status": self.status,
        }


class SkillSynthesizer:
    """Trace2Skill-style synthesis: many trajectories → one skill.

    Flow:
      1. Analyze each trajectory in parallel → local lessons
      2. Dedupe and resolve conflicts
      3. Consolidate into SKILL.md candidate
      4. Submit for cg validation
    """

    def __init__(self):
        self._candidates: list[SkillCandidate] = []

    def synthesize(self, trajectories: list[dict], task_family: str = "") -> SkillCandidate:
        """Synthesize a skill from related trajectories."""
        # 1. Extract lessons from each trajectory
        all_lessons = []
        for traj in trajectories:
            traj_id = traj.get("run_id", traj.get("id", ""))
            lessons = self._extract_lessons(traj)
            for lesson in lessons:
                lesson.trajectory_id = traj_id
            all_lessons.extend(lessons)

        # 2. Dedupe
        deduped = self._dedupe_lessons(all_lessons)

        # 3. Consolidate into SKILL.md
        skill_content = self._consolidate(deduped, task_family)

        # 4. Create candidate
        candidate = SkillCandidate(
            skill_id=f"skill-{len(self._candidates)}",
            name=f"{task_family}-learned" if task_family else "learned-skill",
            description=f"Learned from {len(trajectories)} trajectories",
            content=skill_content,
            source_trajectories=[t.get("run_id", t.get("id", "")) for t in trajectories],
            lessons=deduped,
            hypothesis=f"Consolidated experience from {len(trajectories)} runs on {task_family}",
        )

        self._candidates.append(candidate)
        return candidate

    def _extract_lessons(self, trajectory: dict) -> list[TrajectoryLesson]:
        """Extract lessons from a single trajectory."""
        lessons = []
        run_id = trajectory.get("run_id", "")

        # Extract from events
        events = trajectory.get("events", [])
        for e in events:
            if e.get("type") == "failure" or e.get("outcome") == "lost":
                lessons.append(TrajectoryLesson(
                    content=f"Avoid: {e.get('reason', e.get('detail', 'unknown'))}",
                    lesson_type="failure",
                    confidence=0.8,
                ))

        # Extract from review
        review = trajectory.get("review", {})
        if review.get("feedback"):
            lessons.append(TrajectoryLesson(
                content=f"Review: {review['feedback'][:200]}",
                lesson_type="constraint",
                confidence=0.7,
            ))

        # Extract from decisions
        decisions = trajectory.get("decisions", [])
        for d in decisions:
            if d.get("outcome") == "rejected":
                lessons.append(TrajectoryLesson(
                    content=f"Decision rejected: {d.get('reason', '')}",
                    lesson_type="decision",
                    confidence=0.6,
                ))

        return lessons

    def _dedupe_lessons(self, lessons: list[TrajectoryLesson]) -> list[TrajectoryLesson]:
        """Deduplicate and merge similar lessons."""
        seen = {}
        for lesson in lessons:
            # Simple dedupe by content prefix
            key = lesson.content[:50].lower()
            if key in seen:
                # Merge: increase confidence
                existing = seen[key]
                existing.confidence = min(1.0, existing.confidence + 0.1)
                existing.content = lesson.content  # keep latest
            else:
                seen[key] = lesson
        return list(seen.values())

    def _consolidate(self, lessons: list[TrajectoryLesson], task_family: str) -> str:
        """Consolidate lessons into SKILL.md content."""
        lines = [f"# {task_family} Skill" if task_family else "# Learned Skill", ""]

        # Group by type
        by_type: dict[str, list[TrajectoryLesson]] = {}
        for lesson in lessons:
            by_type.setdefault(lesson.lesson_type, []).append(lesson)

        # Procedures
        if "procedure" in by_type:
            lines.append("## Procedure")
            for l in by_type["procedure"]:
                lines.append(f"- {l.content}")
            lines.append("")

        # Constraints
        if "constraint" in by_type:
            lines.append("## Constraints")
            for l in by_type["constraint"]:
                lines.append(f"- {l.content}")
            lines.append("")

        # Failure patterns
        if "failure" in by_type:
            lines.append("## Known Failures")
            for l in by_type["failure"]:
                lines.append(f"- {l.content}")
            lines.append("")

        # Decisions
        if "decision" in by_type:
            lines.append("## Decision Patterns")
            for l in by_type["decision"]:
                lines.append(f"- {l.content}")
            lines.append("")

        return "\n".join(lines)

    def list_candidates(self) -> list[SkillCandidate]:
        return list(self._candidates)
