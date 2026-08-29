"""ERC-8183 adapter — agentic commerce job lifecycle.

State machine:
  Open → Funded → Submitted → Completed / Rejected / Expired

Roles: Client, Provider, Evaluator
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class JobState(Enum):
    OPEN = "Open"
    FUNDED = "Funded"
    SUBMITTED = "Submitted"
    COMPLETED = "Completed"
    REJECTED = "Rejected"
    EXPIRED = "Expired"


@dataclass
class ERC8183Config:
    """ERC-8183 deployment config."""
    chain_id: int = 84532  # Base Sepolia
    job_contract: str = ""  # deployed at hackathon


@dataclass
class Job:
    """ERC-8183 job — maps to WorkerKit WorkOrder."""
    job_id: str = ""
    client: str = ""      # buyer address
    provider: str = ""    # worker address
    evaluator: str = ""   # evaluator address
    amount: str = "0"     # USDC amount
    state: JobState = JobState.OPEN
    receipt_hash: str = ""
    deliverable: str = ""

    def to_dict(self) -> dict:
        return {
            "jobId": self.job_id,
            "client": self.client,
            "provider": self.provider,
            "evaluator": self.evaluator,
            "amount": self.amount,
            "state": self.state.value,
            "receiptHash": self.receipt_hash,
            "deliverable": self.deliverable,
        }


@dataclass
class JobAdapter:
    """ERC-8183 job lifecycle adapter."""
    config: ERC8183Config = field(default_factory=ERC8183Config)

    def create_job(self, client: str, provider: str, amount: str) -> Job:
        return Job(client=client, provider=provider, amount=amount)

    def fund_job(self, job: Job) -> Job:
        job.state = JobState.FUNDED
        return job

    def submit_job(self, job: Job, receipt_hash: str, deliverable: str) -> Job:
        job.state = JobState.SUBMITTED
        job.receipt_hash = receipt_hash
        job.deliverable = deliverable
        return job

    def complete_job(self, job: Job) -> Job:
        job.state = JobState.COMPLETED
        return job

    def reject_job(self, job: Job) -> Job:
        job.state = JobState.REJECTED
        return job
