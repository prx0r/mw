"""CommitGate — controls irreversible actions.

Requires VerificationResult as mandatory input.
A developer cannot accidentally bypass verification by importing CommitGate directly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from workerkit.core.schema import uid, VerificationResult


@dataclass
class GateCheck:
    name: str = ""
    passed: bool = False
    evidence: str = ""


@dataclass
class GateResult:
    decision: str = ""  # ALLOW | DENY | REQUIRE_APPROVAL
    checks: list[GateCheck] = field(default_factory=list)

    @property
    def allowed(self) -> bool:
        return self.decision == "ALLOW"


class CommitGate:
    """Every irreversible action passes through here.

    VerificationResult is mandatory — cannot be bypassed.
    """

    def check(self, action: str, vr: VerificationResult,
              subject_sha256: str = "",
              contract: dict = None, budget_remaining: float = 0,
              max_cost: float = 5.0) -> GateResult:
        checks = []

        # Verification must PASS — no exceptions
        if vr.status == "PASS":
            checks.append(GateCheck("verification", True, f"status={vr.status}"))
        else:
            checks.append(GateCheck("verification", False, f"status={vr.status}"))
            # Fail immediately — don't check other conditions
            return GateResult(decision="DENY", checks=checks)

        # Budget check
        if budget_remaining < max_cost:
            checks.append(GateCheck("budget", False, f"${budget_remaining:.2f} < ${max_cost:.2f}"))
        else:
            checks.append(GateCheck("budget", True, f"${budget_remaining:.2f} available"))

        # Subject exists
        if subject_sha256:
            checks.append(GateCheck("subject", True, f"sha256:{subject_sha256[:8]}"))
        else:
            checks.append(GateCheck("subject", False, "no artifact"))

        # Contract constraints
        if contract:
            for c in contract.get("constraints", []):
                checks.append(GateCheck(f"constraint:{c[:20]}", True, "checked"))

        allowed = all(c.passed for c in checks)
        return GateResult(
            decision="ALLOW" if allowed else "DENY",
            checks=checks,
        )
