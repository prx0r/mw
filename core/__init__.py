"""WorkerKit core — 10 canonical record families."""
try:
    from workerkit.core.schema import (
        WorkOrder, WorkerManifest, WorkerEvent, ArtifactRef, CostEvent,
        VerificationResult, CommitDecision, SubmissionReceipt, OutcomeReceipt,
        SettlementReceipt, uid, sha256,
    )
    from workerkit.core.receipts import WorkReceipt
    from workerkit.core.events import EventLedger
except ImportError:
    from core.schema import (
        WorkOrder, WorkerManifest, WorkerEvent, ArtifactRef, CostEvent,
        VerificationResult, CommitDecision, SubmissionReceipt, OutcomeReceipt,
        SettlementReceipt, uid, sha256,
    )
    from core.receipts import WorkReceipt
    from core.events import EventLedger
