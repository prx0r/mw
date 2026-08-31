"""Valuation engine — price a WorkerAsset based on observable economics.

Computes trailing P&L, utilization, capability breadth, performance trend,
customer concentration, runtime dependency, and process defensibility.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from core.worker_asset import WorkerAsset, ValuationSignals


def compute_valuation(worker: WorkerAsset, recent_runs: list[dict] = None,
                      lease_data: list[dict] = None) -> ValuationSignals:
    """Compute valuation signals from observable data.

    Args:
        worker: the WorkerAsset to value
        recent_runs: list of run dicts from LabProjection (last 12 months)
        lease_data: list of lease records

    Returns:
        ValuationSignals with all fields populated
    """
    v = ValuationSignals()

    prod = worker.production

    # Trailing 12-month economics
    v.trailing_12m_revenue = prod.total_revenue_usd
    v.trailing_12m_contribution = prod.gross_contribution
    v.estimated_monthly_cost = prod.operating_cost / max(1, prod.total_runs) * 30

    # Capability breadth (normalized 0-1)
    v.capability_breadth = min(1.0, len(worker.capabilities) / 10)

    # Utilization (lease hours / available hours)
    if worker.lease_history:
        total_lease_days = sum(
            (l.end_time - l.start_time) / 86400
            for l in worker.lease_history
            if l.end_time > l.start_time
        )
        age_days = worker.age_days()
        v.utilization_rate = min(1.0, total_lease_days / max(1, age_days))

    # Performance trend (from capability trends)
    trends = [c.trend for c in worker.capabilities if c.trend]
    if trends:
        improving = sum(1 for t in trends if t == "IMPROVING")
        degrading = sum(1 for t in trends if t == "DEGRADING")
        if improving > degrading:
            v.performance_trend = "IMPROVING"
        elif degrading > improving:
            v.performance_trend = "DEGRADING"
        else:
            v.performance_trend = "STABLE"

    # Customer concentration (from lease history)
    if worker.lease_history:
        lessees = {}
        for l in worker.lease_history:
            lessees[l.lessee] = lessees.get(l.lessee, 0) + l.revenue_usd
        total = sum(lessees.values()) or 1
        hhi = sum((rev / total) ** 2 for rev in lessees.values())
        v.customer_concentration = round(hhi, 4)

    # Runtime dependency (0 = fully portable, 1 = locked)
    if worker.runtime.adapter:
        # Single runtime = some dependency, multiple = portable
        v.runtime_dependency = 0.3  # baseline for any runtime

    # Process defensibility (from education + version count)
    versions = len(worker.lineage)
    schools = len(worker.education)
    v.process_defensibility = min(1.0, (versions * 0.1 + schools * 0.2))

    # Renewal rate
    if worker.lease_history:
        completed = [l for l in worker.lease_history if l.end_time > 0]
        if completed:
            # Check if same lessee appears again after a lease ends
            renewed = 0
            for i, l1 in enumerate(completed):
                for l2 in completed[i+1:]:
                    if l1.lessee == l2.lessee and l2.start_time > l1.end_time:
                        renewed += 1
                        break
            v.renewal_rate = round(renewed / len(completed), 4)

    return v


def estimate_worker_price(worker: WorkerAsset, valuation: ValuationSignals) -> float:
    """Estimate monthly lease price based on valuation signals.

    Heuristic: trailing monthly contribution × capability multiplier × availability.
    """
    monthly_contribution = valuation.trailing_12m_contribution / 12
    if monthly_contribution <= 0:
        monthly_contribution = valuation.estimated_monthly_cost * 0.5

    # Capability multiplier
    cap_mult = 1.0 + valuation.capability_breadth * 0.5

    # Performance multiplier
    perf_mult = {"IMPROVING": 1.2, "STABLE": 1.0, "DEGRADING": 0.8}.get(
        valuation.performance_trend, 1.0)

    # Availability
    price = monthly_contribution * cap_mult * perf_mult * worker.availability
    return max(0, round(price, 2))


def format_worker_profile(worker: WorkerAsset, valuation: ValuationSignals) -> str:
    """Format a human-readable worker profile."""
    lines = [
        f"Worker: {worker.worker_id}",
        f"Age: {worker.age_days():.0f} days",
        f"Owner: {worker.owner}",
        "",
        "Production:",
        f"  Runs: {worker.production.total_runs:,}",
        f"  Revenue: ${worker.production.total_revenue_usd:,.2f}",
        f"  Cost: ${worker.production.total_cost_usd:,.2f}",
        f"  Contribution: ${worker.production.gross_contribution:,.2f}",
        f"  Acceptance: {worker.production.acceptance_rate:.1%}",
        f"  Escalation: {worker.production.escalation_rate:.1%}",
        "",
        "Capabilities:",
    ]
    for cap in sorted(worker.capabilities, key=lambda c: c.quality, reverse=True):
        stars = "★" * int(cap.quality * 5) + "☆" * (5 - int(cap.quality * 5))
        lines.append(f"  {cap.name}: {stars} ({cap.confidence})")

    if worker.education:
        lines.append("")
        lines.append("Education:")
        for edu in worker.education:
            lines.append(f"  {edu.school_name} v{edu.curriculum_version}")

    lines.extend([
        "",
        "Valuation:",
        f"  12m revenue: ${valuation.trailing_12m_revenue:,.2f}",
        f"  12m contribution: ${valuation.trailing_12m_contribution:,.2f}",
        f"  Utilization: {valuation.utilization_rate:.1%}",
        f"  Trend: {valuation.performance_trend}",
        f"  Capability breadth: {valuation.capability_breadth:.2f}",
        f"  Process defensibility: {valuation.process_defensibility:.2f}",
    ])

    price = estimate_worker_price(worker, valuation)
    if price > 0:
        lines.append(f"  Estimated monthly: ${price:,.2f}")

    return "\n".join(lines)
