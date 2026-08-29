"""Decision engine — make/buy/abort based on economics."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Decision:
    action: str = ""  # CONTINUE | SWITCH | BUY_HELP | ABORT
    reason: str = ""
    expected_net: float = 0.0


class DecisionEngine:
    def decide(self, spent: float, remaining_budget: float,
               p_success: float, reward: float, estimated_remaining: float) -> Decision:
        expected_payout = p_success * reward
        expected_net = expected_payout - spent - estimated_remaining

        if expected_net > 0:
            return Decision("CONTINUE", f"EV +${expected_net:.2f}", expected_net)
        elif remaining_budget > estimated_remaining:
            return Decision("CONTINUE", "budget allows, learning value", expected_net)
        else:
            return Decision("ABORT", f"EV ${expected_net:.2f}, budget exhausted", expected_net)
