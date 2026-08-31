# Shared Ontology — Oracle × WorkerKit × CGE

## The problem

Three systems need to speak the same language:

```
ORACLE          "here is work that matters"
WORKERKIT       "here is what happened when we tried"
CGE             "here is how to measure if we're getting better"
```

Without a shared ontology, each system invents its own vocabulary and they can't compose.

## Submission types

Every piece of work a worker produces falls into a submission type. The type determines what the evaluator needs to check.

### Type 1: `technical_implementation`

**What:** Working code that solves a specific problem.

**Examples:**
- Smart contract + deploy script + tests
- API endpoint + integration
- Browser extension
- CLI tool
- SDK wrapper

**Evaluator requires:**
```
G0: file structure (README, LICENSE, code files exist)
G1: builds/compiles (cargo build, npm install, etc.)
G2: tests pass (cargo test, npm test, etc.)
G3: runs/demonstrates (can actually execute)
G4: code quality (no obvious bugs, reasonable structure)
G5: documentation (README explains what/how/why)
```

**Oracle signals:**
```
task_family: software.implementation
required_capabilities: [code.{language}, deploy.{target}]
autonomy_level: H1-H2
reward_model: bounty | competition_prize
```

### Type 2: `technical_ideation`

**What:** Ideas, proposals, architecture designs for technical projects.

**Examples:**
- Hackathon idea generation
- System architecture proposal
- Technical approach document
- Research direction proposal

**Evaluator requires:**
```
G0: format (structured, readable)
G1: requirements coverage (addresses all stated constraints)
G2: technical feasibility (could actually be built)
G3: specificity (concrete details, not vague)
G4: novelty (differentiates from existing solutions)
G5: evidence (references real tools/APIs/patterns)
```

**Oracle signals:**
```
task_family: research.ideation.technical
required_capabilities: [text.reason, code.understand, search.web]
autonomy_level: H0-H1
reward_model: competition_prize | bounty
```

### Type 3: `research_analysis`

**What:** Analysis, reports, investigations.

**Examples:**
- Market analysis
- Security audit
- Competitive landscape
- Technical deep-dive
- Due diligence

**Evaluator requires:**
```
G0: structure (executive summary, findings, recommendations)
G1: source quality (references real data, not hallucinated)
G2: completeness (covers the scope)
G3: accuracy (claims are verifiable)
G4: actionability (reader can do something with it)
```

**Oracle signals:**
```
task_family: research.analysis
required_capabilities: [search.web, source.verify, text.reason]
autonomy_level: H0-H2
reward_model: gig | bounty
```

### Type 4: `content_creation`

**What:** Written, visual, or multimedia content.

**Examples:**
- Blog post / article
- Tutorial / guide
- Video script
- Design mockup
- Marketing copy

**Evaluator requires:**
```
G0: format (correct type, reasonable length)
G1: clarity (readable, well-organized)
G2: accuracy (facts are correct)
G3: engagement (interesting, not boring)
G4: completeness (covers the topic)
```

**Oracle signals:**
```
task_family: content.writing
required_capabilities: [text.write, domain.knowledge]
autonomy_level: H0-H1
reward_model: gig | per_word
```

### Type 5: `support_resolution`

**What:** Customer/user support interactions.

**Examples:**
- Bug report triage
- User support ticket
- FAQ response
- Escalation handling

**Evaluator requires:**
```
G0: response time (within SLA)
G1: policy compliance (follows company rules)
G2: resolution quality (actually solves the problem)
G3: tone (professional, empathetic)
G4: escalation judgment (knows when to escalate)
```

**Oracle signals:**
```
task_family: support.customer_service
required_capabilities: [text.respond, policy.retrieve, escalation.judge]
autonomy_level: H2-H3
reward_model: per_resolution | subscription
```

### Type 6: `data_processing`

**What:** Transforming, analyzing, or aggregating data.

**Examples:**
- Data cleaning pipeline
- Report generation from data
- API data aggregation
- ETL workflow

**Evaluator requires:**
```
G0: correctness (output matches expected for known inputs)
G1: completeness (all records processed)
G2: error handling (graceful failures)
G3: performance (within time/memory bounds)
G4: reproducibility (same input → same output)
```

**Oracle signals:**
```
task_family: data.processing
required_capabilities: [data.transform, code.{language}]
autonomy_level: H1-H2
reward_model: per_job | usage_based
```

## Task family hierarchy

```
research
├── ideation
│   ├── technical
│   ├── business
│   └── creative
├── analysis
│   ├── market
│   ├── security
│   ├── technical
│   └── competitive
└── verification
    ├── fact_check
    ├── source_verify
    └── audit

software
├── implementation
│   ├── smart_contract
│   ├── api
│   ├── frontend
│   ├── backend
│   ├── cli
│   └── sdk
├── maintenance
│   ├── bug_fix
│   ├── refactor
│   └── dependency_update
└── infrastructure
    ├── deploy
    ├── monitor
    └── optimize

content
├── writing
│   ├── article
│   ├── tutorial
│   ├── documentation
│   └── marketing
├── visual
│   ├── design
│   ├── diagram
│   └── video
└── data
    ├── visualization
    ├── report
    └── dashboard

support
├── customer_service
├── technical_support
└── sales

data
├── processing
├── analysis
├── visualization
└── pipeline

business
├── strategy
├── finance
├── operations
└── legal
```

## Capability taxonomy

```
text
├── reason          # logical reasoning, argumentation
├── write           # clear, structured writing
├── respond         # conversational, helpful responses
├── summarize       # distill large content
└── translate       # cross-language

code
├── understand      # read and comprehend code
├── write           # produce correct code
├── debug           # find and fix issues
├── review          # evaluate code quality
└── refactor        # improve code structure

search
├── web             # find information online
├── academic        # find research papers
└── code            # find code examples

data
├── transform       # clean, reshape, aggregate
├── analyze         # statistical analysis
├── visualize       # charts, graphs, dashboards
└── pipeline        # ETL, workflows

domain
├── smart_contract  # Solidity, EVM, DeFi
├── web             # HTTP, APIs, browsers
├── mobile          # iOS, Android
├── cloud           # AWS, GCP, Azure
├── security        # crypto, auth, audits
└── finance         # accounting, markets, trading

process
├── plan            # break down work
├── estimate        # time/cost forecasting
├── prioritize      # rank by importance
├── verify          # check own work
└── escalate        # know when to ask for help

source
├── verify          # fact-check claims
├── cite            # reference properly
└── evaluate        # assess source quality

policy
├── retrieve        # find relevant rules
├── apply           # follow rules correctly
└── judge           # edge cases, judgment calls
```

## Evaluator gate hierarchy

Every evaluator runs gates in order. A failure at any gate stops evaluation.

```
G0: FORMAT        → does it exist and is it the right type?
G1: STRUCTURE     → is it organized and complete?
G2: CORRECTNESS   → are the facts/implementation correct?
G3: QUALITY       → is it good, not just acceptable?
G4: EVIDENCE      → are claims backed by proof?
G5: NOVELTY       → does it add something new?
G6: JUDGMENT      → does it show domain expertise?
```

For each submission type, the required gates are a subset:

| Type | Required gates | Optional gates |
|------|---------------|----------------|
| technical_implementation | G0, G1, G2, G3 | G4, G5 |
| technical_ideation | G0, G1, G2, G3, G5 | G6 |
| research_analysis | G0, G1, G2, G4 | G3, G5 |
| content_creation | G0, G1, G3 | G2, G4 |
| support_resolution | G0, G2, G3 | G1, G6 |
| data_processing | G0, G1, G2 | G3, G4 |

## How this maps to CGE WorldPacks

A WorldPack for `technical_ideation`:

```
worlds/technical-ideation/
├── world.yaml
│   task_family: research.ideation.technical
│   capabilities: [text.reason, code.understand, search.web]
│   gates: [G0, G1, G2, G3, G5]
│   rubric:
│     requirements_coverage: 0.25
│     technical_feasibility: 0.20
│     specificity: 0.20
│     novelty: 0.15
│     evidence: 0.10
│     rationale: 0.10
├── public/
│   ├── requirements.md       # what the worker sees
│   └── examples/             # past winning submissions
├── scenarios/
│   ├── dev.jsonl             # training scenarios
│   └── validation.jsonl      # held-out scenarios
├── hidden/
│   └── sealed.jsonl          # final test (never shown to worker)
├── evaluator/
│   ├── gates/
│   │   ├── format.py         # G0: structured, non-empty
│   │   ├── coverage.py       # G1: requirements addressed
│   │   ├── feasibility.py    # G2: could actually work
│   │   ├── specificity.py    # G3: concrete details
│   │   └── novelty.py        # G5: different from existing
│   ├── rubric.yaml           # scoring weights
│   └── judge.md              # LLM-as-judge prompt
└── README.md
```

## How this maps to WorkerKit capabilities

After each run, WorkerKit records:

```
Run R91
  task_family: research.ideation.technical
  capabilities_used: [text.reason, code.understand]
  gates_passed: {G0: true, G1: true, G2: false, G3: true, G5: false}
  overall_score: 0.68
  cost: $0.38
```

This feeds into the capability tracker:

```
CapabilityEvidence:
  task_class: research.ideation.technical
  sample_size: 47
  acceptance_rate: 0.72
  median_cost: $0.31
  gate_pass_rates:
    G0: 0.98
    G1: 0.91
    G2: 0.74    ← weakness identified
    G3: 0.85
    G5: 0.62    ← weakness identified
```

The Lab then knows: "worker is weak at technical feasibility and novelty."

## How this maps to Oracle decisions

Oracle sees:

```
Demand signal:
  task_family: research.ideation.technical
  opportunities: 23 open
  median_reward: $45
  competition: 12 submissions avg
  
Worker capability:
  acceptance_rate: 0.72
  cost_per_attempt: $0.38
  
DecisionEngine:
  expected_value = 0.72 * $45 - $0.38 = $32.02
  recommendation: DO
```

## The shared data model

```python
# Shared across all three systems
@dataclass
class TaskFamily:
    id: str                    # "research.ideation.technical"
    path: list[str]            # ["research", "ideation", "technical"]
    required_capabilities: list[str]  # ["text.reason", "code.understand"]
    submission_type: str       # "technical_ideation"
    autonomy_level: str        # "H0"
    
@dataclass
class CapabilityEvidence:
    task_class: str
    sample_size: int
    acceptance_rate: float
    median_cost: float
    gate_pass_rates: dict[str, float]
    
@dataclass
class SubmissionType:
    name: str
    required_gates: list[str]
    optional_gates: list[str]
    evaluator_config: dict     # maps to WorldPack evaluator/
    
@dataclass
class GateDefinition:
    id: str                    # "G0"
    name: str                  # "format"
    check_fn: str              # "evaluator.gates.format"
    description: str
```

## Next steps

1. Implement `SubmissionType` registry in WorkerKit
2. Implement `GateDefinition` registry
3. Create WorldPack templates for each submission type
4. Wire Oracle's task_family taxonomy to WorkerKit's capability tracker
5. Wire CGE's evaluator gates to the gate registry
