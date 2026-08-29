"""ERC-8183 adapter — job escrow, real web3 when available."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum

try:
    from web3 import Web3  # type: ignore
    HAS_WEB3 = True
except ImportError:
    HAS_WEB3 = False
    Web3 = None  # type: ignore


class JobState(Enum):
    OPEN = "Open"
    FUNDED = "Funded"
    SUBMITTED = "Submitted"
    COMPLETED = "Completed"
    REJECTED = "Rejected"
    EXPIRED = "Expired"


@dataclass
class ERC8183Config:
    chain_id: int = 84532
    job_contract: str = field(default_factory=lambda: os.environ.get("ERC8183_CONTRACT", ""))
    rpc_url: str = field(default_factory=lambda: os.environ.get("BASE_SEPOLIA_RPC", "https://sepolia.base.org"))
    usdc_address: str = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"  # Base Sepolia USDC


JOB_ABI = [
    {"inputs": [{"name": "provider", "type": "address"}, {"name": "amount", "type": "uint256"}, {"name": "uri", "type": "string"}], "name": "createJob", "outputs": [{"name": "jobId", "type": "uint256"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "jobId", "type": "uint256"}], "name": "fundJob", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "jobId", "type": "uint256"}, {"name": "receiptHash", "type": "bytes32"}, {"name": "deliverable", "type": "string"}], "name": "submitJob", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "jobId", "type": "uint256"}], "name": "completeJob", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "jobId", "type": "uint256"}], "name": "getJob", "outputs": [{"type": "tuple", "components": [{"name": "client", "type": "address"}, {"name": "provider", "type": "address"}, {"name": "evaluator", "type": "address"}, {"name": "amount", "type": "uint256"}, {"name": "state", "type": "uint8"}]}], "stateMutability": "view", "type": "function"},
]


@dataclass
class Job:
    job_id: str = ""
    client: str = ""
    provider: str = ""
    evaluator: str = ""
    amount: str = "0"
    state: JobState = JobState.OPEN
    receipt_hash: str = ""
    deliverable: str = ""

    def to_dict(self) -> dict:
        return {"jobId": self.job_id, "client": self.client, "provider": self.provider, "evaluator": self.evaluator, "amount": self.amount, "state": self.state.value, "receiptHash": self.receipt_hash, "deliverable": self.deliverable}


@dataclass
class JobAdapter:
    config: ERC8183Config = field(default_factory=ERC8183Config)

    def _w3(self):
        if not HAS_WEB3:
            raise RuntimeError("web3 not installed: pip install web3")
        if not self.config.job_contract:
            raise RuntimeError("ERC8183_CONTRACT not set")
        return Web3(Web3.HTTPProvider(self.config.rpc_url))

    def _contract(self):
        return self._w3().eth.contract(address=self.config.job_contract, abi=JOB_ABI)

    # ─── Off-chain helpers (work without RPC) ────────────────────────

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

    # ─── On-chain (require funded key + deployed contract) ───────────

    def create_job_onchain(self, private_key: str, provider: str, amount_wei: int, uri: str) -> dict:
        w3 = self._w3()
        acct = w3.eth.account.from_key(private_key)
        c = self._contract()
        tx = c.functions.createJob(provider, amount_wei, uri).build_transaction({
            "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 400000, "chainId": self.config.chain_id,
        })
        signed = acct.sign_transaction(tx)
        h = w3.eth.send_raw_transaction(signed.raw_transaction)
        return {"txHash": h.hex()}

    def get_job_onchain(self, job_id: int) -> dict | None:
        try:
            c = self._contract()
            r = c.functions.getJob(job_id).call()
            return {"client": r[0], "provider": r[1], "evaluator": r[2], "amount": str(r[3]), "state": r[4]}
        except Exception:
            return None
