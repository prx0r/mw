"""Multi-dimensional evaluation harness — not scalar scores.

Evaluates submissions on multiple dimensions with explicit criteria.
Each dimension has a weight and a scoring method.

Dimensions:
  - requirement_coverage: did it satisfy every explicit constraint?
  - diversity: are ideas meaningfully distinct?
  - technical_validity: could each described system plausibly work?
  - specificity: is each idea implementable rather than vague?
  - novelty: is it genuinely new vs rehashing existing solutions?
  - rationale: is the value proposition explained?
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DimensionScore:
    """Score for one evaluation dimension."""
    name: str
    score: float  # 0.0 to 1.0
    weight: float
    details: str = ""
    evidence: list[str] = field(default_factory=list)

    @property
    def weighted(self) -> float:
        return self.score * self.weight

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "score": round(self.score, 4),
            "weight": self.weight,
            "weighted": round(self.weighted, 4),
            "details": self.details,
            "evidence": self.evidence,
        }


@dataclass
class EvaluationResult:
    """Multi-dimensional evaluation result."""
    fixture_id: str
    worker_id: str
    dimensions: list[DimensionScore] = field(default_factory=list)
    overall_score: float = 0.0
    gate_results: dict[str, bool] = field(default_factory=dict)
    raw_output: str = ""
    cost_usd: float = 0.0
    duration_s: float = 0.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "fixture_id": self.fixture_id,
            "worker_id": self.worker_id,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "overall_score": round(self.overall_score, 4),
            "gate_results": self.gate_results,
            "cost_usd": self.cost_usd,
            "duration_s": self.duration_s,
        }


# ─── Dimension scorers ────────────────────────────────────────────────

def score_requirement_coverage(output: str, fixture: dict) -> DimensionScore:
    """Check how many explicit constraints were satisfied."""
    constraints = fixture.get("constraints", [])
    if not constraints:
        return DimensionScore(name="requirement_coverage", score=1.0, weight=0.25,
                            details="no constraints to check")

    satisfied = 0
    evidence = []
    for c in constraints:
        # Simple heuristic: check if key terms from constraint appear in output
        key_terms = [w.lower() for w in c.split() if len(w) > 4 and w.lower() not in
                     {"each", "must", "include", "about", "that", "with", "from", "than", "have", "this"}]
        matches = sum(1 for t in key_terms if t in output.lower())
        if matches >= min(3, len(key_terms) * 0.4):
            satisfied += 1
            evidence.append(f"constraint satisfied: {c[:60]}...")
        else:
            evidence.append(f"constraint missed: {c[:60]}...")

    score = satisfied / len(constraints)
    return DimensionScore(
        name="requirement_coverage", score=score, weight=0.25,
        details=f"{satisfied}/{len(constraints)} constraints satisfied",
        evidence=evidence[:5],
    )


def score_diversity(output: str, fixture: dict) -> DimensionScore:
    """Check if ideas are meaningfully distinct."""
    # Count distinct numbered items
    items = re.findall(r'(?:^|\n)\s*(?:\d+[\.\)]\s*|[A-Z][a-z]+\s*:)', output)
    expected = fixture.get("task", "")
    # Extract number from task
    num_match = re.search(r'(\d+)\s+(?:ideas|ways|features|strategies)', expected)
    expected_count = int(num_match.group(1)) if num_match else 10

    actual_count = max(len(items), 1)

    # Check for obvious duplicates (same first 20 chars)
    lines = [l.strip() for l in output.split('\n') if l.strip() and len(l.strip()) > 20]
    first_phrases = [l[:30].lower() for l in lines]
    unique_phrases = len(set(first_phrases))
    uniqueness = unique_phrases / max(1, len(first_phrases))

    count_score = min(1.0, actual_count / expected_count)
    score = (count_score + uniqueness) / 2

    return DimensionScore(
        name="diversity", score=score, weight=0.20,
        details=f"found {actual_count}/{expected_count} items, {unique_phrases} unique phrases",
    )


def score_technical_validity(output: str, fixture: dict) -> DimensionScore:
    """Check if ideas are technically plausible."""
    # Heuristic: check for technical specificity markers
    tech_markers = [
        r'API', r'database', r' server', r' deploy', r' SDK', r' integration',
        r' cloud', r' AWS', r' Docker', r' Kubernetes', r' REST', r' GraphQL',
        r' database', r' cache', r' queue', r' microservice', r' pipeline',
        r' LLM', r' model', r' inference', r' training', r' fine-tune',
    ]
    matches = sum(1 for m in tech_markers if re.search(m, output, re.IGNORECASE))
    score = min(1.0, matches / 5)  # 5+ technical markers = full score

    return DimensionScore(
        name="technical_validity", score=score, weight=0.20,
        details=f"{matches} technical specificity markers found",
    )


def score_specificity(output: str, fixture: dict) -> DimensionScore:
    """Check if ideas are implementable rather than vague."""
    # Check for concrete details: numbers, names, specific tools
    specificity_markers = [
        r'\$\d+', r'\d+\s*(?:users|customers|requests|GB|TB|ms|seconds|minutes)',
        r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+',  # Proper nouns (product names)
        r'v\d+\.\d+', r'version \d+', r'API v\d',
        r'implementation', r'MVP', r'prototype', r'build',
    ]
    matches = sum(1 for m in specificity_markers if re.search(m, output))
    score = min(1.0, matches / 4)

    return DimensionScore(
        name="specificity", score=score, weight=0.15,
        details=f"{matches} specificity markers found",
    )


def score_novelty(output: str, fixture: dict) -> DimensionScore:
    """Check if ideas are genuinely new."""
    # Check for references to existing products (good — shows awareness)
    existing_products = [
        'google analytics', 'slack', 'zoom', 'notion', 'figma', 'linear',
        'vercel', 'netlify', 'supabase', 'firebase', 'aws', 'stripe',
        'github', 'gitlab', 'jira', 'confluence', 'salesforce',
        'hubspot', 'intercom', 'zendesk', 'freshdesk', 'otter',
    ]
    refs = sum(1 for p in existing_products if p in output.lower())
    # Check for differentiation language
    diff_markers = ['unlike', 'different from', 'compared to', 'instead of',
                   'goes beyond', 'not just', 'more than']
    diffs = sum(1 for d in diff_markers if d in output.lower())

    score = min(1.0, (refs + diffs * 2) / 5)

    return DimensionScore(
        name="novelty", score=score, weight=0.10,
        details=f"{refs} product references, {diffs} differentiation markers",
    )


def score_rationale(output: str, fixture: dict) -> DimensionScore:
    """Check if value propositions are explained."""
    rationale_markers = [
        r'because', r'therefore', r'this (?:enables|allows|means)',
        r'value', r'benefit', r'advantage', r'why', r'reason',
        r'users (?:want|need|benefit)', r'problem (?:is|that)',
        r'solution', r'impact', r'outcome',
    ]
    matches = sum(1 for m in rationale_markers if re.search(m, output, re.IGNORECASE))
    score = min(1.0, matches / 5)

    return DimensionScore(
        name="rationale", score=score, weight=0.10,
        details=f"{matches} rationale markers found",
    )


# ─── Main evaluator ───────────────────────────────────────────────────

DIMENSION_SCORERS = {
    "requirement_coverage": score_requirement_coverage,
    "diversity": score_diversity,
    "technical_validity": score_technical_validity,
    "specificity": score_specificity,
    "novelty": score_novelty,
    "rationale": score_rationale,
}


class Evaluator:
    """Multi-dimensional evaluator for competitive ideation tasks."""

    def __init__(self, rubric: dict | None = None):
        self.rubric = rubric or {}
        self.dimensions = self.rubric.get("dimensions", {})

    def evaluate(self, output: str, fixture: dict, worker_id: str = "") -> EvaluationResult:
        """Evaluate submission on all dimensions."""
        result = EvaluationResult(
            fixture_id=fixture.get("id", ""),
            worker_id=worker_id,
            raw_output=output,
        )

        # Score each dimension
        for dim_name, dim_config in self.dimensions.items():
            scorer = DIMENSION_SCORERS.get(dim_name)
            if scorer:
                dim_score = scorer(output, fixture)
                result.dimensions.append(dim_score)
            else:
                # Default scorer
                result.dimensions.append(DimensionScore(
                    name=dim_name, score=0.5,
                    weight=dim_config.get("weight", 0.1),
                    details="no scorer available",
                ))

        # Compute overall score
        if result.dimensions:
            result.overall_score = sum(d.weighted for d in result.dimensions)

        # Check gates
        gates = self.rubric.get("gates", [])
        for gate in gates:
            dim = next((d for d in result.dimensions if d.name == gate), None)
            if dim:
                result.gate_results[gate] = dim.score >= 0.5

        return result

    def compare(self, result_a: EvaluationResult, result_b: EvaluationResult) -> dict:
        """Compare two evaluation results dimension by dimension."""
        comparison = {
            "overall": {"a": result_a.overall_score, "b": result_b.overall_score,
                       "delta": result_b.overall_score - result_a.overall_score},
            "dimensions": {},
            "gates": {},
        }

        # Compare dimensions
        dims_a = {d.name: d for d in result_a.dimensions}
        dims_b = {d.name: d for d in result_b.dimensions}
        for dim_name in set(list(dims_a.keys()) + list(dims_b.keys())):
            a_score = dims_a[dim_name].score if dim_name in dims_a else 0
            b_score = dims_b[dim_name].score if dim_name in dims_b else 0
            comparison["dimensions"][dim_name] = {
                "a": round(a_score, 4),
                "b": round(b_score, 4),
                "delta": round(b_score - a_score, 4),
            }

        # Compare gates
        for gate in set(list(result_a.gate_results.keys()) + list(result_b.gate_results.keys())):
            a_pass = result_a.gate_results.get(gate, False)
            b_pass = result_b.gate_results.get(gate, False)
            comparison["gates"][gate] = {"a": a_pass, "b": b_pass}

        return comparison


def format_report(result: EvaluationResult) -> str:
    """Format evaluation result as human-readable report."""
    lines = [f"=== Evaluation: {result.fixture_id} ==="]
    lines.append(f"Worker: {result.worker_id}")
    lines.append(f"Overall: {result.overall_score:.4f}")
    lines.append("")
    lines.append("Dimensions:")
    for d in result.dimensions:
        lines.append(f"  {d.name}: {d.score:.4f} (weight={d.weight:.2f}, weighted={d.weighted:.4f})")
        if d.details:
            lines.append(f"    {d.details}")
    lines.append("")
    lines.append("Gates:")
    for gate, passed in result.gate_results.items():
        lines.append(f"  {gate}: {'✓ PASS' if passed else '✗ FAIL'}")
    return "\n".join(lines)


def format_comparison(comparison: dict, label_a: str = "v1", label_b: str = "v2") -> str:
    """Format comparison as human-readable report."""
    lines = [f"=== Comparison: {label_a} vs {label_b} ==="]
    lines.append(f"Overall: {label_a}={comparison['overall']['a']:.4f} → {label_b}={comparison['overall']['b']:.4f} (Δ={comparison['overall']['delta']:+.4f})")
    lines.append("")
    lines.append("Dimensions:")
    for dim_name, scores in comparison["dimensions"].items():
        delta = scores["delta"]
        marker = "↑" if delta > 0 else "↓" if delta < 0 else "="
        lines.append(f"  {dim_name}: {label_a}={scores['a']:.4f} → {label_b}={scores['b']:.4f} (Δ={delta:+.4f} {marker})")
    return "\n".join(lines)
