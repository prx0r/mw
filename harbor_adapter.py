"""Harbor Adapter — bridge Harbor tasks with CGE experimental semantics.

Harbor = reproducible world execution
CGE = scientifically controlled comparison in that world

This adapter:
1. Converts SuccessModel → Harbor task + RewardKit verifier
2. Runs Harbor tasks through CGE experiment protocol
3. Collects multi-dimensional reward.json results
"""
from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class HarborTask:
    """A Harbor task configuration."""
    name: str
    instruction: str
    task_toml: dict = field(default_factory=dict)
    environment: dict = field(default_factory=dict)
    tests: list[str] = field(default_factory=list)
    
    def save(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        (path / "instruction.md").write_text(self.instruction)
        
        # task.toml
        toml_lines = ['version = "1.0"']
        for section, values in self.task_toml.items():
            toml_lines.append(f"\n[{section}]")
            for k, v in values.items():
                toml_lines.append(f'{k} = {json.dumps(v)}')
        (path / "task.toml").write_text("\n".join(toml_lines))
        
        # tests
        if self.tests:
            tests_dir = path / "tests"
            tests_dir.mkdir(exist_ok=True)
            for i, test_code in enumerate(self.tests):
                (tests_dir / f"test_{i}.py").write_text(test_code)


@dataclass  
class RewardKitVerifier:
    """RewardKit-style multi-dimensional verifier."""
    dimensions: dict[str, float] = field(default_factory=dict)  # name -> weight
    hard_gates: list[str] = field(default_factory=list)
    
    def generate_tests(self) -> list[str]:
        """Generate Python test files for each dimension."""
        tests = []
        
        # Hard gates test
        if self.hard_gates:
            gate_code = 'import re\nfrom pathlib import Path\n\ndef test_hard_gates(output_dir: Path):\n    content = (output_dir / "submission.md").read_text()\n'
            for gate in self.hard_gates:
                gate_code += f'    assert len(content.strip()) > 0, "empty output"\n'
            tests.append(gate_code)
        
        # Per-dimension tests
        for dim_name in self.dimensions:
            dim_code = f'import re\nfrom pathlib import Path\n\ndef test_{dim_name}(output_dir: Path):\n    content = (output_dir / "submission.md").read_text()\n'
            
            if "requirement" in dim_name.lower():
                dim_code += '    key_terms = ["architecture", "technical", "implementation"]\n    found = sum(1 for t in key_terms if t in content.lower())\n    assert found >= 2, f"Only {{found}}/3 key terms"\n'
            elif "novelty" in dim_name.lower():
                dim_code += '    assert "unlike" in content.lower() or "novel" in content.lower() or "unique" in content.lower(), "Lacks differentiation"\n'
            elif "technical" in dim_name.lower():
                dim_code += '    has_code = "```" in content or "0x" in content or "v1" in content\n    assert has_code, "Lacks technical specifics"\n'
            elif "evidence" in dim_name.lower():
                dim_code += '    has_ref = "github" in content.lower() or "api" in content.lower() or "sdk" in content.lower()\n    assert has_ref, "Lacks evidence references"\n'
            else:
                dim_code += f'    assert len(content) > 200, "Output too short for {{dim_name}}"\n'
            
            tests.append(dim_code)
        
        return tests
    
    def generate_reward_json(self, scores: dict[str, float]) -> dict:
        """Generate Harbor-style reward.json."""
        weighted_sum = 0
        total_weight = 0
        for dim, weight in self.dimensions.items():
            score = scores.get(dim, 0.5)
            weighted_sum += score * weight
            total_weight += weight
        
        reward = weighted_sum / total_weight if total_weight > 0 else 0
        reward.update({"reward": reward})  # Harbor expects a 'reward' key
        return reward


def success_model_to_harbor(success_model: dict, opportunity: dict) -> tuple[HarborTask, RewardKitVerifier]:
    """Convert a SuccessModel to a Harbor task + RewardKit verifier."""
    
    # Build instruction from opportunity
    instruction = f"# {opportunity.get('title', 'Task')}\n\n"
    instruction += f"{opportunity.get('description', '')}\n\n"
    instruction += "## Requirements\n"
    for req in opportunity.get("requirements", []):
        instruction += f"- {req}\n"
    instruction += "\n## Output\nGenerate a structured document and save it to submission.md\n"
    
    # Build task.toml
    task_toml = {
        "verifier": {"timeout_sec": 120.0, "environment_mode": "separate"},
        "agent": {"timeout_sec": 120.0},
        "environment": {"build_timeout_sec": 600.0, "cpus": 1, "memory_mb": 2048, "storage_mb": 10240},
    }
    
    # Build verifier
    dimensions = success_model.get("dimensions", {})
    hard_gates = list(success_model.get("hard_gates", {}).keys())
    
    task = HarborTask(
        name=opportunity.get("id", "task"),
        instruction=instruction,
        task_toml=task_toml,
    )
    
    verifier = RewardKitVerifier(
        dimensions=dimensions,
        hard_gates=hard_gates,
    )
    
    return task, verifier


def run_harbor_task(task: HarborTask, agent: str = "opencode", model: str = "mimo-v2.5") -> dict:
    """Run a Harbor task and return results."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        task_path = Path(tmpdir) / task.name
        task.save(task_path)
        
        try:
            result = subprocess.run(
                ["harbor", "run", "-p", str(task_path), "-a", agent, "-m", model],
                capture_output=True, text=True, timeout=300,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[-1000:],
                "stderr": result.stderr[-500:],
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
