"""Moltwork Lab integration kit.

Purposefully thin: upstream systems own runtime, evaluation and graph storage.
This package only binds versions/evidence and makes the slow parts replaceable.
"""
from .records import (
    CampaignRef, WorkerVersionRef, WorkerExecution, HarborTrialRecord,
    EvaluationRecord, RunBinding, CredentialRef,
)
from .runtime import WorkerRuntime, FakeWorkerRuntime, LettaRuntimeClient
from .harbor import HarborCLI, HarborJobParser, MockHarbor
from .hydra import HydraHTTPClient, MemoryGraphSink
from .oracle import HumanDependency, ExecutionStep, derive_autonomy_level

__all__ = [
    "CampaignRef", "WorkerVersionRef", "WorkerExecution", "HarborTrialRecord",
    "EvaluationRecord", "RunBinding", "CredentialRef", "WorkerRuntime",
    "FakeWorkerRuntime", "LettaRuntimeClient", "HarborCLI", "HarborJobParser",
    "MockHarbor", "HydraHTTPClient", "MemoryGraphSink", "HumanDependency",
    "ExecutionStep", "derive_autonomy_level",
]
