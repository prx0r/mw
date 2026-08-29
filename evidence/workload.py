"""WorkloadManifestV1 — attested workload identity.

Separates economic identity (agent) from execution identity (workload).
Agent #413 can upgrade WorkerKit 0.4 → 0.5 while retaining marketplace identity.

workload_id = hash(canonical(WorkloadManifestV1))

Includes Preflight-style capability fingerprint:
  capabilityHash changes when tool surface changes → reputation becomes versioned.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from evidence.canonical import sha256, keccak256, canonical_json


@dataclass
class WorkloadManifestV1:
    """Canonical workload identity — what code/TEE produced this result."""
    agent_id: str = ""
    source_repository: str = ""
    source_commit: str = ""
    image_digests: list[str] = field(default_factory=list)
    workerkit_version: str = ""
    config_hash: str = ""
    compose_hash: str = ""
    skills_hash: str = ""
    policy_hash: str = ""
    model_policy_hash: str = ""
    mcp_manifest_hash: str = ""
    capability_hash: str = ""  # Preflight-style: hash of live MCP tool surface
    created_at: float = field(default_factory=time.time)

    def canonical_form(self) -> dict:
        return {
            "agentId": self.agent_id,
            "sourceRepository": self.source_repository,
            "sourceCommit": self.source_commit,
            "imageDigests": sorted(self.image_digests),
            "workerkitVersion": self.workerkit_version,
            "configHash": self.config_hash,
            "composeHash": self.compose_hash,
            "skillsHash": self.skills_hash,
            "policyHash": self.policy_hash,
            "modelPolicyHash": self.model_policy_hash,
            "mcpManifestHash": self.mcp_manifest_hash,
            "capabilityHash": self.capability_hash,
        }

    def workload_id(self) -> str:
        """SHA-256 of canonical form — the workload identity."""
        return sha256(canonical_json(self.canonical_form()))

    def to_dict(self) -> dict:
        d = self.canonical_form()
        d["workloadId"] = self.workload_id()
        d["createdAt"] = self.created_at
        return d


def compute_capability_hash(tools: list[dict]) -> str:
    """Preflight-style: hash of live MCP tool surface.

    tools: [{"name": "...", "endpoint": "...", "pricing": {...}}]
    """
    canonical = json.dumps(tools, sort_keys=True, separators=(",", ":"))
    return sha256(canonical)
