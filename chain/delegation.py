"""ERC-7710 delegation adapter — bounded capabilities for agents.

MetaMask Delegation Framework (Base Sepolia):
  DelegationManager: 0xdb9B1e94B5b69Df7e401DDbedE43491141047dB3
  AllowedMethodsEnforcer: 0x2c21fD0Cb9DC8445CB3fb0DC5E7Bb0Aca01842B5
  AllowedTargetsEnforcer: 0x7F20f61b1f09b08D970938F6fa563634d65c4EeB
  ERC20TransferAmountEnforcer: 0xf100b0819427117EcF76Ed94B358B1A5b5C6D2Fc
  LimitedCallsEnforcer: 0x04658B29F6b82ed55274221a06Fc97D318E25416
"""
from __future__ import annotations

from dataclasses import dataclass, field
from evidence.policy import ExecutionPolicy


@dataclass
class DelegationConfig:
    """MetaMask Delegation Framework deployment."""
    chain_id: int = 84532  # Base Sepolia
    delegation_manager: str = "0xdb9B1e94B5b69Df7e401DDbedE43491141047dB3"
    allowed_methods_enforcer: str = "0x2c21fD0Cb9DC8445CB3fb0DC5E7Bb0Aca01842B5"
    allowed_targets_enforcer: str = "0x7F20f61b1f09b08D970938F6fa563634d65c4EeB"
    erc20_amount_enforcer: str = "0xf100b0819427117EcF76Ed94B358B1A5b5C6D2Fc"
    limited_calls_enforcer: str = "0x04658B29F6b82ed55274221a06Fc97D318E25416"


@dataclass
class DelegationAdapter:
    """ERC-7710 delegation for Moltwork leases."""
    config: DelegationConfig = field(default_factory=DelegationConfig)

    def build_delegation(self, policy: ExecutionPolicy, delegate: str) -> dict:
        """Build delegation from execution policy.

        Maps TEE policy → on-chain caveats.
        """
        caveats = []

        # Allowed targets
        if policy.allowed_targets:
            caveats.append({
                "enforcer": self.config.allowed_targets_enforcer,
                "terms": ",".join(policy.allowed_targets),
            })

        # Allowed methods
        if policy.allowed_methods:
            caveats.append({
                "enforcer": self.config.allowed_methods_enforcer,
                "terms": ",".join(policy.allowed_methods),
            })

        # Spend cap
        if policy.max_spend_usd:
            caveats.append({
                "enforcer": self.config.erc20_amount_enforcer,
                "terms": policy.max_spend_usd,
            })

        # Call limit
        if policy.max_calls < 10000:
            caveats.append({
                "enforcer": self.config.limited_calls_enforcer,
                "terms": str(policy.max_calls),
            })

        return {
            "delegate": delegate,
            "caveats": caveats,
            "policyDigest": policy.digest(),
            "expiresAt": policy.expires_at,
        }
