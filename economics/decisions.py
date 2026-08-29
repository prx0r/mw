"""Decision engine — make/abort based on marginal economics.

Two numbers:
    whole_run_expected_profit = P(success) × payout - spent - expected_remaining
    marginal_continue_EV = P(success) × payout - expected_remaining_cost

CONTINUE decision: marginal_continue_EV > threshold AND remaining_budget >= expected_remaining.
whole_run is for analytics/reporting only — sunk costs are sunk.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Decision:
    action: str = ""  # CONTINUE | ABORT | REJECT
    reason: str = ""
    expected_net: float = 0.0
    marginal_ev: float = 0.0


class DecisionEngine:
    def decide(self, spent: float, remaining_budget: float,
               p_success: float, reward: float, estimated_remaining: float,
               min_ev_threshold: float = 0.0) -> Decision:
        expected_payout = p_success * reward
        whole_run_expected = expected_payout - spent - estimated_remaining
        marginal_continue = expected_payout - estimated_remaining

        # CONTINUE if: worth doing AND can afford
        if marginal_continue > min_ev_threshold and remaining_budget >= estimated_remaining:
            return Decision("CONTINUE", f"marginal EV +${marginal_continue:.2f}", whole_run_expected, marginal_continue)
        elif marginal_continue <= 0:
            return Decision("ABORT", f"negative marginal EV ${marginal_continue:.2f}", whole_run_expected, marginal_continue)
        else:
            return Decision("ABORT", f"insufficient budget: ${remaining_budget:.2f} < ${estimated_remaining:.2f}", whole_run_expected, marginal_continue)
