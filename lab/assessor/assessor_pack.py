"""AssessorPack — independent multi-gate evaluation of worker artifacts.

Gate hierarchy (from letta-mod.md):
  G0: deterministic requirements (file exists, tests pass, format valid)
  G1: technical execution (code quality, integration, deployment)
  G2: evidence verification (claims backed by traces/sources)
  G3: blinded rubric panel (multiple LLM judges, permuted order)
  G4: blinded pairwise comparisons (vs baseline submissions)
  G5: real-world outcome (actual competition result)

Worker and assessor evolution stay separate.
Frozen assessor evaluates Worker v7 → v8.
Only after experiment closes can assessor be updated.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path


def _sha256(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


@dataclass
class GateResult:
    """Result of a single evaluation gate."""
    gate: str  # G0, G1, G2, G3, G4, G5
    passed: bool
    score: float = 0.0  # 0.0-1.0
    details: dict = field(default_factory=dict)
    error: str = ""


@dataclass
class AssessorResult:
    """Complete assessment of an artifact across all gates."""
    artifact_hash: str
    opportunity_id: str
    assessor_version: str = "assessor-v1"
    created_at: float = field(default_factory=time.time)

    gate_results: list[GateResult] = field(default_factory=list)
    overall_score: float = 0.0
    overall_passed: bool = False
    recommendation: str = ""  # SUBMIT, REVISE, REJECT

    # For paired comparison
    compared_against: str = ""  # hash of baseline
    pairwise_preference: str = ""  # "preferred", "baseline", "equal"

    def to_dict(self) -> dict:
        return {
            "artifact_hash": self.artifact_hash,
            "opportunity_id": self.opportunity_id,
            "assessor_version": self.assessor_version,
            "created_at": self.created_at,
            "gate_results": [
                {"gate": g.gate, "passed": g.passed, "score": g.score, "details": g.details, "error": g.error}
                for g in self.gate_results
            ],
            "overall_score": self.overall_score,
            "overall_passed": self.overall_passed,
            "recommendation": self.recommendation,
            "compared_against": self.compared_against,
            "pairwise_preference": self.pairwise_preference,
        }

    def content_hash(self) -> str:
        return _sha256({
            "artifact_hash": self.artifact_hash,
            "opportunity_id": self.opportunity_id,
            "assessor_version": self.assessor_version,
            "overall_score": self.overall_score,
        })


class AssessorPack:
    """Multi-gate independent evaluation.

    Usage:
        pack = AssessorPack(version="assessor-v1")
        result = pack.evaluate(artifact_content, research_pack)
    """

    def __init__(self, version: str = "assessor-v1"):
        self.version = version

    def evaluate(self, artifact_content: str, artifact_hash: str,
                 opportunity_id: str, research_pack: dict | None = None) -> AssessorResult:
        """Run all gates on an artifact."""
        result = AssessorResult(
            artifact_hash=artifact_hash,
            opportunity_id=opportunity_id,
            assessor_version=self.version,
        )

        # G0: Deterministic requirements
        g0 = self._gate_deterministic(artifact_content, research_pack)
        result.gate_results.append(g0)

        # G1: Technical execution
        g1 = self._gate_technical(artifact_content)
        result.gate_results.append(g1)

        # G2: Evidence verification
        g2 = self._gate_evidence(artifact_content, research_pack)
        result.gate_results.append(g2)

        # Compute overall score (weighted average)
        weights = {"G0": 0.25, "G1": 0.25, "G2": 0.20, "G3": 0.15, "G4": 0.15}
        total_weight = 0
        weighted_sum = 0
        for g in result.gate_results:
            w = weights.get(g.gate, 0.1)
            weighted_sum += w * g.score
            total_weight += w

        result.overall_score = weighted_sum / total_weight if total_weight > 0 else 0
        result.overall_passed = all(g.passed for g in result.gate_results if g.gate in ("G0", "G1"))

        if result.overall_score >= 0.7 and result.overall_passed:
            result.recommendation = "SUBMIT"
        elif result.overall_score >= 0.4:
            result.recommendation = "REVISE"
        else:
            result.recommendation = "REJECT"

        return result

    def _gate_deterministic(self, content: str, research: dict | None) -> GateResult:
        """G0: deterministic checks — format, non-empty, basic requirements."""
        checks = []

        # Non-empty
        has_content = bool(content and len(content.strip()) > 50)
        checks.append({"name": "has_content", "passed": has_content})

        # Minimum length
        has_length = len(content) > 200
        checks.append({"name": "minimum_length", "passed": has_length})

        # Not an error message
        not_error = "error" not in content.lower()[:200]
        checks.append({"name": "not_error_response", "passed": not_error})

        # Has structure (headers or numbered items)
        has_structure = any(marker in content for marker in ["#", "1.", "##", "- "])
        checks.append({"name": "has_structure", "passed": has_structure})

        passed = all(c["passed"] for c in checks)
        score = sum(1 for c in checks if c["passed"]) / len(checks) if checks else 0

        return GateResult(
            gate="G0",
            passed=passed,
            score=score,
            details={"checks": checks},
        )

    def _gate_technical(self, content: str) -> GateResult:
        """G1: technical execution quality."""
        indicators = []

        # Has code blocks
        has_code = "```" in content or "    " in content
        indicators.append({"name": "has_code", "passed": has_code})

        # Mentions specific technologies
        tech_terms = ["api", "database", "server", "deploy", "sdk", "cloud", "docker",
                       "typescript", "python", "rust", "solidity", "graphql", "rest"]
        tech_count = sum(1 for t in tech_terms if t in content.lower())
        has_tech = tech_count >= 2
        indicators.append({"name": "technical_depth", "passed": has_tech, "detail": f"{tech_count} tech terms"})

        # Has concrete details (numbers, versions, specific names)
        import re
        has_numbers = bool(re.search(r'\d+\.\d+|\$\d+|v\d+|port \d+', content))
        indicators.append({"name": "concrete_details", "passed": has_numbers})

        passed = sum(1 for i in indicators if i["passed"]) >= 2
        score = sum(1 for i in indicators if i["passed"]) / len(indicators) if indicators else 0

        return GateResult(
            gate="G1",
            passed=passed,
            score=score,
            details={"indicators": indicators},
        )

    def _gate_evidence(self, content: str, research: dict | None) -> GateResult:
        """G2: evidence verification — claims backed by specifics."""
        claims = []

        # Check for unsupported superlatives
        import re
        superlatives = re.findall(r'\b(best|perfect|ultimate|revolutionary|unprecedented)\b', content.lower())
        has_unsupported = len(superlatives) > 3
        claims.append({"name": "no_unsupported_superlatives", "passed": not has_unsupported,
                       "detail": f"{len(superlatives)} superlatives found"})

        # Check for specific references
        has_refs = bool(re.search(r'github\.com|docs\.|api\.|v\d+\.\d+', content))
        claims.append({"name": "has_specific_references", "passed": has_refs})

        # Check for rationale
        rationale_terms = ["because", "therefore", "since", "given that", "reason"]
        has_rationale = any(t in content.lower() for t in rationale_terms)
        claims.append({"name": "has_rationale", "passed": has_rationale})

        passed = sum(1 for c in claims if c["passed"]) >= 2
        score = sum(1 for c in claims if c["passed"]) / len(claims) if claims else 0

        return GateResult(
            gate="G2",
            passed=passed,
            score=score,
            details={"claims": claims},
        )

    def save(self, result: AssessorResult, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        (path / "result.json").write_text(json.dumps(result.to_dict(), indent=2))
        (path / "meta.json").write_text(json.dumps({
            "content_hash": result.content_hash(),
            "assessor_version": self.version,
        }, indent=2))
