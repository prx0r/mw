"""CGE Evaluator Gates — deterministic and rubric-based checks."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class GateResult:
    gate: str
    passed: bool
    score: float
    details: dict


def gate_format(content: str, config: dict = None) -> GateResult:
    """G0: Format check — is it structured and non-empty?"""
    checks = {
        "non_empty": bool(content and len(content.strip()) > 50),
        "has_structure": bool(re.search(r'#{1,3}\s|^\d+\.|^- ', content, re.MULTILINE)),
        "reasonable_length": 100 < len(content) < 50000,
    }
    passed = all(checks.values())
    score = sum(checks.values()) / len(checks)
    return GateResult(gate="G0_format", passed=passed, score=score, details=checks)


def gate_requirements(content: str, requirements: list[str], config: dict = None) -> GateResult:
    """G1: Requirements coverage — are all requirements addressed?"""
    if not requirements:
        return GateResult(gate="G1_requirements", passed=True, score=1.0, details={"no_requirements": True})
    
    covered = 0
    details = {}
    for req in requirements:
        # Check if requirement keywords appear in content
        keywords = [w.lower() for w in req.split() if len(w) > 3]
        found = any(kw in content.lower() for kw in keywords)
        details[req[:40]] = found
        if found:
            covered += 1
    
    score = covered / len(requirements) if requirements else 0
    passed = score >= 0.5  # at least half the requirements addressed
    
    return GateResult(
        gate="G1_requirements",
        passed=passed,
        score=score,
        details={"coverage": f"{covered}/{len(requirements)}", "per_requirement": details},
    )


def gate_feasibility(content: str, config: dict = None) -> GateResult:
    """G2: Technical feasibility — could this actually work?"""
    indicators = {
        "has_technical_terms": bool(re.search(r'\b(api|sdk|contract|protocol|deploy|database|server|endpoint)\b', content.lower())),
        "has_concrete_details": bool(re.search(r'\d+\.\d+|v\d+|port \d+|\$\d+|0x[0-9a-fA-F]+', content)),
        "no_impossible_claims": not bool(re.search(r'\b(infinite|zero.cost|100%.secure|unhackable)\b', content.lower())),
        "references_real_tech": bool(re.search(r'github|npm|pypi|docker|aws|gcp|ethereum|solana|base', content.lower())),
    }
    
    passed_count = sum(indicators.values())
    score = passed_count / len(indicators)
    passed = score >= 0.5
    
    return GateResult(
        gate="G2_feasibility",
        passed=passed,
        score=score,
        details=indicators,
    )


def gate_specificity(content: str, config: dict = None) -> GateResult:
    """G3: Specificity — concrete details, not vague promises."""
    indicators = {
        "has_numbers": bool(re.search(r'\d+', content)),
        "has_proper_nouns": bool(re.search(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*', content)),
        "has_code_blocks": "```" in content or "    " in content,
        "mentions_versions": bool(re.search(r'v\d+|version \d+|\d+\.\d+\.\d+', content)),
        "specific_not_generic": not bool(re.search(r'\b(general|various|multiple|several)\b', content.lower())),
    }
    
    passed_count = sum(indicators.values())
    score = passed_count / len(indicators)
    passed = score >= 0.4
    
    return GateResult(
        gate="G3_specificity",
        passed=passed,
        score=score,
        details=indicators,
    )


def gate_novelty(content: str, past_submissions: list[str] = None, config: dict = None) -> GateResult:
    """G5: Novelty — differentiates from existing solutions."""
    # Check for differentiation language
    differentiation = bool(re.search(
        r'\b(unlike|differs|instead|unique|novel|first|innovative|different approach)\b',
        content.lower()
    ))
    
    # Check it's not just restating existing solutions
    generic_clone = bool(re.search(
        r'\b(like|similar to|same as|copy of|fork of)\b',
        content.lower()
    )) and not differentiation
    
    # If we have past submissions, check for overlap
    overlap_score = 0.0
    if past_submissions:
        content_words = set(content.lower().split())
        max_overlap = 0
        for past in past_submissions:
            past_words = set(past.lower().split())
            if content_words and past_words:
                overlap = len(content_words & past_words) / min(len(content_words), len(past_words))
                max_overlap = max(max_overlap, overlap)
        overlap_score = 1.0 - min(1.0, max_overlap)
    
    indicators = {
        "has_differentiation": differentiation,
        "not_generic_clone": not generic_clone,
        "different_from_past": overlap_score > 0.3 if past_submissions else True,
    }
    
    score = sum(indicators.values()) / len(indicators)
    passed = score >= 0.5
    
    return GateResult(
        gate="G5_novelty",
        passed=passed,
        score=score,
        details={**indicators, "past_overlap": overlap_score},
    )


# Gate registry
GATES = {
    "G0_format": gate_format,
    "G1_requirements": gate_requirements,
    "G2_feasibility": gate_feasibility,
    "G3_specificity": gate_specificity,
    "G5_novelty": gate_novelty,
}


def run_gates(content: str, gate_names: list[str], requirements: list[str] = None,
              past_submissions: list[str] = None) -> list[GateResult]:
    """Run a set of gates on content."""
    results = []
    for name in gate_names:
        fn = GATES.get(name)
        if not fn:
            continue
        
        kwargs = {"content": content}
        if name == "G1_requirements" and requirements:
            kwargs["requirements"] = requirements
        elif name == "G5_novelty" and past_submissions:
            kwargs["past_submissions"] = past_submissions
        
        try:
            result = fn(**kwargs)
            results.append(result)
        except Exception as e:
            results.append(GateResult(gate=name, passed=False, score=0.0, details={"error": str(e)}))
    
    return results
