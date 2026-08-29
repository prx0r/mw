"""AcceptanceContract — what must be true for work to be accepted."""
from __future__ import annotations
from dataclasses import dataclass, field
from workerkit.core.schema import uid


@dataclass
class Criterion:
    name: str = ""
    description: str = ""
    check_type: str = ""  # "file_exists", "content_min", "contains"
    required: bool = True


@dataclass
class AcceptanceContract:
    id: str = field(default_factory=uid)
    required_outputs: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    minimum_quality: float = 0.6
    maximum_cost: float = 5.0
    criteria: list[Criterion] = field(default_factory=list)
    external_conditions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "required_outputs": self.required_outputs,
            "constraints": self.constraints,
            "minimum_quality": self.minimum_quality,
            "maximum_cost": self.maximum_cost,
            "criteria": [{"name": c.name, "desc": c.description, "required": c.required} for c in self.criteria],
        }


def contract_from_jobspec(jobspec: dict) -> AcceptanceContract:
    return AcceptanceContract(
        required_outputs=["SUBMISSION.md"],
        constraints=jobspec.get("automatic_rejection", []),
        minimum_quality=0.6,
        criteria=[
            Criterion(name=r, description=r, required=True)
            for r in jobspec.get("hard_requirements", [])
        ],
    )
