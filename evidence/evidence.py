"""Evidence tiers — formalized trust levels."""
from __future__ import annotations

from enum import Enum


class EvidenceTier(Enum):
    """Evidence trust hierarchy.

    E0 SELF_REPORTED: agent says it did the work
    E1 OBSERVED: Moltwork independently observed output
    E2 PAYMENT_VERIFIED: settlement/payments independently verified
    E3 TEE_VERIFIED: attested expected workload executed receipt
    E4 REEXECUTED: independent execution reproduced result
    E5 ZK_VERIFIED: cryptographic computation proof
    """
    SELF_REPORTED = "E0_SELF_REPORTED"
    OBSERVED = "E1_OBSERVED"
    PAYMENT_VERIFIED = "E2_PAYMENT_VERIFIED"
    TEE_VERIFIED = "E3_TEE_VERIFIED"
    REEXECUTED = "E4_REEXECUTED"
    ZK_VERIFIED = "E5_ZK_VERIFIED"

    @property
    def level(self) -> int:
        return int(self.value.split("_")[0][1:])

    def __ge__(self, other):
        return self.level >= other.level

    def __gt__(self, other):
        return self.level > other.level
