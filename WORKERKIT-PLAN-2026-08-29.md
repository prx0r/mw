# WorkerKit Integration Plan — 2026-08-29

## Diagnosis

The repo is structurally further along than it appears, but has a dangerous gap between **implemented interfaces** and **implemented reality**. Architecture scores 8-9/10, real implementation scores 0-4/10 on the learning flywheel.

**One sentence:** Make `ethonline-2026` the integration line and ruthlessly replace every fake/simulated boundary with one real Letta → WorkerKit → evaluation → Hydra → learning cycle.

---

## 10 Changes (in execution order)

### 1. Rename `HydraStore` → `LabProjection`

**File:** `hydra/store.py`
**Why:** `HydraStore` is SQLite. Calling it Hydra implies a graph database that doesn't exist. This naming bug gives false confidence.

**Change:**
- Rename class `HydraStore` → `LabProjection`
- Keep `HydraStore` as a deprecated alias: `HydraStore = LabProjection`
- Update all imports across the codebase to use `LabProjection`
- Add interface methods: `project_event(...)`, `rebuild(...)`, `query(...)`
- Future: `SQLiteLabProjection` (current) and `HydraLabProjection` (real HydraDB)

**Files touched:** `hydra/store.py`, `fleet/manager.py`, `lab/context.py`, `lab/reflection.py`, `lab/discovery.py`, `lab/dashboard.py`, `cg/evolve.py`, `tests/test_hydra_fleet.py`, `tests/test_learning_lab.py`

---

### 2. Remove Letta stub `ok=True` — never fake success

**File:** `adapters/letta.py:130-138`
**Why:** When no Letta server exists, the adapter returns `ExecutionResult(ok=True)` with `[letta-stub]`. This is exactly what WorkerKit was designed to prevent — false confidence in simulated output.

**Change:**
- No server + no .af → `ExecutionResult(ok=False, error="NO_RUNTIME", metadata={"reason": "no Letta server or .af file"})`
- No server + .af exists → `ExecutionResult(ok=False, error="NOT_EXECUTED", metadata={"reason": "af found but no Letta server to execute against"})`
- Keep the stub execution ONLY under a `force_stub=True` parameter for testing
- Update `ExecutionResult` in `adapters/base.py` to add `error_code: str = ""` field

**Files touched:** `adapters/letta.py`, `adapters/base.py`, `tests/test_letta.py`, `tests/test_learning_lab.py`

---

### 3. Replace cg hash evaluator with real `Evaluator` interface

**File:** `cg/evolve.py:74-82`
**Why:** `Replay.run()` scores via `hash(worker + fixture + evaluator) → integer → pseudo score`. This tests deterministic hashing, not whether a Worker performs better. The claimed "v7 beats v1" proof is fake.

**Change:**
- Rename current `Replay` to `DeterministicMockEvaluator` (preserved for tests)
- Add `Evaluator` protocol:
  ```python
  class Evaluator(Protocol):
      async def evaluate(self, worker_version: dict, fixture: dict) -> EvaluationResult: ...
  ```
- Add `LiveEvaluator` that: fixture → Letta worker executes → artifact → actual evaluation → scores
- `EvolutionLab` gets `evaluator: Evaluator` parameter (default: `DeterministicMockEvaluator`)
- Move `DeterministicMockEvaluator` to `tests/mocks/`

**Files touched:** `cg/evolve.py`, `cg/__init__.py`, new file `tests/mocks/mock_evaluator.py`

---

### 4. Make lab projection append-only (fix `INSERT OR REPLACE`)

**File:** `hydra/store.py`
**Why:** Comment says "Runs — the core immutable record" but uses `INSERT OR REPLACE` which mutates. Contradicts WorkerKit's canonical principle: append-only events = truth, projection = disposable view.

**Change:**
- Add `is_append_only: bool = True` flag to `LabProjection`
- When `is_append_only=True`: use only `INSERT` (never `INSERT OR REPLACE`)
- Duplicate inserts → raise `AppendOnlyViolation` with the existing record
- Add `rebuild()` method that drops and recreates tables from event ledger
- Keep `INSERT OR REPLACE` only in a `MutableProjection` subclass for dev/testing

**Files touched:** `hydra/store.py`

---

### 5. Add `RunDependency` — track exact versions per run

**New file:** `lab/dependencies.py`
**Why:** Today there's no provenance proving Run X USED Skill Y + Briefing Z + Process W + Memory V + Reviewer R. Without this, you can't attribute improvement to specific causes.

**Change:**
- New dataclass:
  ```python
  @dataclass
  class RunDependency:
      run_id: str
      worker_version_id: str
      skill_version_ids: list[str]
      briefing_id: str = ""
      process_version_id: str = ""
      memory_revision_id: str = ""
      reviewer_id: str = ""
      context_pack_ids: list[str] = field(default_factory=list)
  ```
- New table `lab_run_dependencies` in LabProjection schema
- `record_run_dependency(dep: RunDependency)` and `get_run_dependencies(run_id)` methods
- Every run in the learning cycle MUST record its dependencies before `close()`

**Files touched:** new `lab/dependencies.py`, `hydra/store.py`, `lab/__init__.py`

---

### 6. Replace LabContext substring matching with real retrieval

**File:** `lab/context.py:14`
**Why:** `task_family.lower() in json.dumps(r).lower()` is a search engine written in blood. It will return false positives and miss exact matches.

**Change:**
- Add `task_family` as a proper indexed column in `lab_runs` table
- `recall_similar_runs`: query by `task_family` column + `worker_version` + outcome filters
- `get_task_priors`: query by `task_family` column, not substring
- `get_failure_patterns`: use actual `failure_reason` from run events (add column to schema)
- `get_best_skill`: filter by `task_family` column, not substring
- Add `briefing_context` table for Hydra-backed retrieval (indexed, not scanned)
- Keep the exact same public API — only replace internals

**Files touched:** `lab/context.py`, `hydra/store.py`

---

### 7. Replace `CapabilityTracker` with `CapabilityEvidence` model

**File:** `capabilities.py`
**Why:** `successful_runs / total_runs` is wrong. A high-quality submission can lose. A terrible submission can win in a weak field. Need multi-dimensional evidence.

**Change:**
- New dataclass:
  ```python
  @dataclass
  class CapabilityEvidence:
      capability: str
      worker_version: str
      task_family: str
      evaluator_score: float
      outcome: str  # won/lost
      payout: float
      cost: float
      review_scores: list[float] = field(default_factory=list)
      evidence_strength: str = "INSUFFICIENT"
  ```
- `CapabilityTracker` derives capability estimates from `CapabilityEvidence` list
- Confidence now based on: evidence count + outcome variance + cost consistency + task-family coverage
- Deprecate `success_rate` property, replace with `quality_estimate` that weighs multiple signals
- Keep `Capability` dataclass but make it derived, not directly mutated

**Files touched:** `capabilities.py`

---

### 8. Refactor `ReflectionPipeline.promote()` to require `ExperimentResult`

**File:** `lab/reflection.py`
**Why:** Currently `promote()` just sets `status = "proven"` with no evidence. A lesson should only become proven after cg validates it on held-out fixtures.

**Change:**
- New dataclass:
  ```python
  @dataclass
  class ExperimentResult:
      experiment_id: str
      lesson_id: str
      parent_version: str
      candidate_version: str
      hidden_mean_before: float
      hidden_mean_after: float
      gate_regressions: list[str] = field(default_factory=list)
      cost_delta: float = 0.0
      promoted: bool = False
      reasoning: str = ""
  ```
- `CandidateLesson` gains: `hypothesis: str`, `patch: dict`, `source_runs: list[str]`, `evaluation_plan: str`
- New states: `OBSERVED → PROPOSED → UNDER_TEST → VALIDATED | REJECTED`
- `promote()` now requires `ExperimentResult` parameter — cannot promote without cg evidence
- `reject()` records rejection reason

**Files touched:** `lab/reflection.py`

---

### 9. Create `services/runtime-letta/` TypeScript service boundary

**New directory:** `services/runtime-letta/`
**Why:** Python REST adapter hitting `/v1/agents` and picking the first agent is catastrophic with 5+ workers. Need explicit Worker ↔ Letta Agent mapping owned by a service.

**Change:**
- TypeScript service using Hono (matching oracle worker pattern)
- Owns: `Worker ID ↔ Letta Agent ID` mapping (never "list and pick first")
- Exposes: `createWorker`, `openRun`, `execute`, `snapshot`, `applyLearning`, `exportTrajectory`, `health`
- Python side talks to this service via HTTP, not directly to Letta API
- Worker identity: `worker_123` maps to exactly `letta_agent_abc`
- Uses Letta Agent SDK (not raw REST)

**Files touched:** new `services/runtime-letta/` directory

---

### 10. Replace `test_learning_lab.py` with real experiment harness

**File:** `tests/test_learning_lab.py`
**Why:** Current test hardcodes `v1_score, v7_score = 0.65, 0.82` and asserts `v7 > v1`. Also has multiple `test(..., True)` assertions. The 321 tests prove interfaces compose, not that learning works.

**Change:**
- Remove all hardcoded scores
- Remove all `test(..., True)` trivial assertions
- New structure:
  ```
  UNIT TESTS (existing test_invariants.py — keep)
  SYSTEM EVIDENCE (new test_learning_lab.py)
  ```
- Test outputs:
  ```
  WorkerKit invariants            PASS
  Lab projection roundtrip        PASS
  Letta live execution            PASS/SKIP (if no server)
  RunDependency recording         PASS
  Learning experiment:
    v1 hidden mean                <computed>
    v2 hidden mean                <computed>
    difference                    <computed>
    cost delta                    <computed>
    n                             <computed>
    regressions                   <none or list>
    PROMOTED                      YES/NO
  ```
- Uses `LiveEvaluator` when Letta server available, `DeterministicMockEvaluator` otherwise
- Reports actual numbers, not boolean claims

**Files touched:** `tests/test_learning_lab.py`

---

## Execution Order

| # | Change | Risk | Depends on |
|---|--------|------|-----------|
| 1 | Rename HydraStore → LabProjection | Low | — |
| 2 | Remove Letta stub ok=True | Low | — |
| 3 | Replace cg hash evaluator | Medium | — |
| 4 | Make lab projection append-only | Low | 1 |
| 5 | Add RunDependency | Low | 1 |
| 6 | Replace LabContext retrieval | Low | 1, 5 |
| 7 | Replace CapabilityTracker | Low | — |
| 8 | Refactor ReflectionPipeline | Medium | 3, 5 |
| 9 | Create runtime-letta service | High | 2 |
| 10 | Replace test harness | Medium | 1-8 |

Changes 1, 2, 3, 7 are independent — can be done in parallel.
Changes 4, 5 depend on 1.
Change 6 depends on 1, 5.
Change 8 depends on 3, 5.
Change 9 depends on 2.
Change 10 depends on all prior changes.

---

## Success Criteria

After all 10 changes:

1. No fake success paths — `ok=True` only when real execution happened
2. HydraStore renamed — no false graph-database implications
3. CG uses real evaluator — hash evaluator only in tests
4. Lab projection is append-only — events are truth, projections disposable
5. Every run has provenance — `RunDependency` tracks all inputs
6. LabContext uses indexed queries — no substring matching
7. Capability derived from multi-dimensional evidence — not simple ratio
8. Promotion requires experiment evidence — no unvalidated lessons
9. Letta service owns Worker↔Agent mapping — no "pick first"
10. Tests report actual numbers — not boolean claims

**The one thing that must work:** Real Letta worker → real tasks → real artifacts → real evaluation → real experience → real memory/skill patch → real held-out replay → measurable improvement.
