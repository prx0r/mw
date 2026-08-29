"""Decision engine — make/buy/abort based on economics."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Decision:
    action: str = ""  # CONTINUE | ABORT | REJECT
    reason: str = ""
    expected_net: float = 0.0


class DecisionEngine:
    """Decide CONTINUE or ABORT based on expected value.

    Two numbers:
        whole_run_expected_profit = P(success) × payout - spent - expected_remaining
        marginal_continue_EV = expected_incremental_payout - expected_remaining_cost
    """
    def decide(self, spent: float, remaining_budget: float,
               p_success: float, reward: float, estimated_remaining: float,
               min_ev_threshold: float = 0.0) -> Decision:
        expected_payout = p_success * reward
        whole_run_expected = expected_payout - spent - estimated_remaining
        marginal_continue = (p_success * reward) - estimated_remaining

        # Must have positive marginal EV to continue
        if marginal_continue > min_ev_threshold and whole_run_expected > min_ev_threshold:
            return Decision("CONTINUE", f"marginal EV +${marginal_continue:.2f}", whole_run_expected)
        elif whole_run_expected <= 0 and marginal_continue <= 0:
            return Decision("ABORT", f"negative EV: marginal=${marginal_continue:.2f} whole_run=${whole_run_expected:.2f}", whole_run_expected)
        else:
            return Decision("ABORT", f"insufficient EV: marginal=${marginal_continue:.2f}", whole_run_expected)
