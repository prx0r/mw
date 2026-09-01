"""Evolution laboratory — real evaluation, not hash scoring.

The old Replay scored via hash(worker + fixture + evaluator) → integer.
That tests determinism, not whether a Worker performs better.

New structure:
  Evaluator protocol  — real evaluation interface
  DeterministicMockEvaluator — hash-based, for tests only
  LiveEvaluator — Letta worker executes → artifact → scoring
  EvolutionLab — uses Evaluator to compare worker versions
"""
from __future__ import annotations
import hashlib, json, math, random, time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Protocol, Any


def _h(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def _wilson(k,n,z=1.96):
    if n==0: return (0.0,0.0)
    p=k/n; d=1+z*z/n
    c=(p+z*z/(2*n))/d; w=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (max(0,c-w),min(1,c+w))
def _bootstrap(scores,n=2000,seed=0):
    rnd=random.Random(seed); m=len(scores)
    if m==0: return (0.0,0.0)
    means=sorted(sum(scores[rnd.randrange(m)] for _ in range(m))/m for _ in range(n))
    return (means[int(0.025*n)],means[int(0.975*n)])


@dataclass(frozen=True)
class EvaluationResult:
    """Result of evaluating one worker-version on one fixture."""
    score: float = 0.0
    gates_passed: dict[str, bool] = field(default_factory=dict)
    cost_usd: float = 0.0
    duration_s: float = 0.0
    artifact_hash: str = ""
    error: str = ""
    metadata: dict = field(default_factory=dict)


class Evaluator(Protocol):
    """Real evaluation interface. Implementations must actually execute work."""

    async def evaluate(self, worker_version: dict, fixture: dict) -> EvaluationResult:
        """Execute worker on fixture and return evaluation result."""
        ...


class DeterministicMockEvaluator:
    """Hash-based scoring — FOR TESTS ONLY. Not evidence of learning."""

    def __init__(self, evaluator_src: str = ""):
        self.evaluator_src = evaluator_src

    async def evaluate(self, worker_version: dict, fixture: dict) -> EvaluationResult:
        h = _h({"worker": worker_version, "fixture": fixture, "evaluator": _h(self.evaluator_src)})
        score = (int(h[:8], 16) % 1000) / 1000
        gates = {"deterministic": score > 0.5}
        return EvaluationResult(
            score=score,
            gates_passed=gates,
            metadata={"mode": "deterministic-mock", "hash": h[:16]},
        )


class LiveEvaluator:
    """Real evaluation: fixture → Letta worker executes → artifact → scoring.

    Requires a runtime adapter that can actually execute work.
    """

    def __init__(self, adapter: Any, evaluator_fn: Any = None):
        self.adapter = adapter
        self.evaluator_fn = evaluator_fn  # async fn(artifact, fixture) -> EvaluationResult

    async def evaluate(self, worker_version: dict, fixture: dict) -> EvaluationResult:
        from workerkit.adapters.base import RunContext

        # Execute via adapter
        context = RunContext(
            workspace=fixture.get("workspace", "/tmp/eval"),
            budget_remaining=fixture.get("budget", 4.0),
            timeout_seconds=fixture.get("timeout", 300),
        )
        work_order = {
            "title": fixture.get("title", fixture.get("task", "")),
            "description": fixture.get("description", json.dumps(fixture)[:500]),
        }

        try:
            result = await self.adapter.execute(work_order, context)
        except Exception as e:
            return EvaluationResult(error=f"execution failed: {e}")

        if not result.ok:
            return EvaluationResult(
                error=result.error or result.error_code,
                metadata={"error_code": result.error_code, "mode": "live"},
            )

        # Score the artifact
        if self.evaluator_fn:
            try:
                return await self.evaluator_fn(result.output_content, fixture)
            except Exception as e:
                return EvaluationResult(error=f"evaluator failed: {e}")

        # Default: basic quality heuristics
        content = result.output_content
        score = 0.0
        gates = {}

        # Heuristic: non-empty, reasonable length, no errors
        if content and len(content) > 50:
            score += 0.3
        if len(content) > 200:
            score += 0.2
        if "error" not in content.lower():
            score += 0.2
        if result.cost_usd < fixture.get("budget", 4.0):
            score += 0.15
        if result.duration_s < fixture.get("timeout", 300):
            score += 0.15

        gates["has_content"] = bool(content and len(content) > 50)
        gates["within_budget"] = result.cost_usd < fixture.get("budget", 4.0)
        gates["no_errors"] = "error" not in content.lower()

        return EvaluationResult(
            score=min(1.0, score),
            gates_passed=gates,
            cost_usd=result.cost_usd,
            duration_s=result.duration_s,
            artifact_hash=result.output_hash,
            metadata={"mode": "live", "content_length": len(content)},
        )


@dataclass(frozen=True)
class WorldPack:
    name: str; root: Path
    training: list[dict]=field(default_factory=list)
    validation: list[dict]=field(default_factory=list)
    hidden: list[dict]=field(default_factory=list)
    evaluator_src: str=""; rubric: dict=field(default_factory=dict)
    @classmethod
    def from_dir(cls,root: str|Path, name="pack"):
        p=Path(root); tr=_load(p/"training.json"); va=_load(p/"validation.json"); hi=_load(p/"hidden.json")
        ev=(p/"evaluator.py").read_text() if (p/"evaluator.py").exists() else ""
        ru=_load_yaml(p/"rubric.yaml")
        return cls(name=name,root=p,training=tr,validation=va,hidden=hi,evaluator_src=ev,rubric=ru)
    @property
    def manifest_hash(self)->str: return _h({"t":self.training,"v":self.validation,"h":len(self.hidden),"e":_h(self.evaluator_src),"r":self.rubric})[:16]
    def all_fixtures(self, tier="validation"): return {"training":self.training,"validation":self.validation,"hidden":self.hidden}[tier]

def _load(p:Path):
    if not p.exists(): return []
    try: return json.loads(p.read_text())
    except: return []
def _load_yaml(p:Path):
    if not p.exists(): return {}
    try:
        import yaml
        return yaml.safe_load(p.read_text()) or {}
    except: return {}

ALLOWED=("memory","skill","mod","planning_policy","model_route")
@dataclass(frozen=True)
class Mutation:
    kind: str; payload: dict=field(default_factory=dict)
    def __post_init__(self): assert self.kind in ALLOWED, f"unknown mutation {self.kind}"
    @property
    def hash(self)->str: return _h({"kind":self.kind,"payload":self.payload})[:16]
    def apply(self, base: dict)->dict: d=dict(base); d[self.kind]=self.payload; d["_mut_hash"]=self.hash; return d

@dataclass
class CapabilityClaim:
    claim_id: str; world: str; scenario_hash: str; candidate: dict; metrics: dict
    n: int; wins: int; receipts: list[str]=field(default_factory=list)
    created_at: float=field(default_factory=time.time)
    @property
    def wilson(self): return _wilson(self.wins,self.n)
    @property
    def bootstrap(self): return _bootstrap(self.metrics.get("scores",[]))
    @property
    def content_hash(self)->str: return _h({"claim_id":self.claim_id,"world":self.world,"scenario_hash":self.scenario_hash,"candidate":self.candidate,"metrics":self.metrics,"n":self.n})
    def to_dict(self): lo,hi=self.wilson; b_lo,b_hi=self.bootstrap; return {"claim_id":self.claim_id,"world":self.world,"scenario_hash":self.scenario_hash,"candidate":self.candidate,"metrics":self.metrics,"n":self.n,"wins":self.wins,"wilson_lo":lo,"wilson_hi":hi,"bootstrap_lo":b_lo,"bootstrap_hi":b_hi,"content_hash":self.content_hash,"receipts":self.receipts}


# Keep old Replay as DeterministicMockEvaluator for backward compat
Replay = DeterministicMockEvaluator


@dataclass
class EvolutionLab:
    pack: WorldPack; hydra=None; seed: int=0
    evaluator: Evaluator|None=None

    def __post_init__(self):
        if self.evaluator is None:
            self.evaluator = DeterministicMockEvaluator(self.pack.evaluator_src)

    async def step(self, objective: str, budget: int=8, variants: list[dict]|None=None)->dict:
        rnd=random.Random(self.seed); gates=self.pack.rubric.get("gates",[objective])
        if variants is None: variants=[{"id":f"v{i}","objective":objective,"seed":self.seed+i} for i in range(budget)]
        scored=[]
        for v in sorted(variants, key=lambda x: _h(x)):
            # Evaluate each variant on validation fixtures
            scores = []
            for fx in (self.pack.validation or [{"id":"dummy"}]):
                try:
                    result = await self.evaluator.evaluate(v, fx)
                    scores.append(result.score)
                except Exception:
                    scores.append(0.0)

            metrics={"mean":sum(scores)/len(scores),"scores":scores,"gates":{g: all(s>0.5 for s in scores) for g in gates}}
            gate_pass=sum(metrics["gates"].values()); h=_h({"variant":v,"metrics":metrics})
            metrics["_hash"]=h[:16]
            scored.append((gate_pass, metrics["mean"], h, v, metrics))
            if self.hydra: self.hydra.record_run(run_id=f"evo_{h[:8]}",agent_id=v.get("id","evo"),opportunity_id=objective,model=v.get("model",""),skills=[objective],evaluation_score=metrics["mean"],outcome="won" if gate_pass==len(gates) else "lost")
        scored.sort(key=lambda x: (-x[0],-x[1],x[2]))
        winner=scored[0]; claim=CapabilityClaim(claim_id=f"claim_{winner[2][:24]}",world=self.pack.name,scenario_hash=self.pack.manifest_hash,candidate=winner[3],metrics=winner[4],n=len(winner[4]["scores"]),wins=sum(1 for s in winner[4]["scores"] if s>0.5),receipts=[winner[2][:16]])
        return {"winner":winner[3],"metrics":winner[4],"claim":claim.to_dict(),"ranked":[s[3] for s in scored],"gates":gates}

    async def replay(self, worker_version: dict, tier="hidden")->list[dict]:
        """Replay a worker version on held-out fixtures using real evaluation."""
        fixtures = self.pack.all_fixtures(tier)
        out = []
        for fx in fixtures:
            try:
                result = await self.evaluator.evaluate(worker_version, fx)
                out.append({"fixture": fx.get("id", _h(fx)[:8]), "score": result.score,
                           "gates": result.gates_passed, "cost": result.cost_usd})
            except Exception as e:
                out.append({"fixture": fx.get("id", "err"), "score": 0.0, "error": str(e)})
        return out
