Yes. The right product is now:

> **Moltwork WorkerKit = a distribution, not a framework.**

Moltwork should own almost no agent intelligence. It should package the best current components, define the **standard worker lifecycle**, maintain compatibility, measure which combinations work, and let users swap components as the frontier moves.

Your existing `get-me-money` repo is already the correct shell: it has the broker, evaluator, executor, ledger, memory, oracle and Hermes runtime.  Its broker already models capability gaps and job-specific skill bundles, creates isolated job workspaces/Hermes homes, and records skill-combination outcomes.   The Hermes runtime already accepts a job-specific profile and isolates `HERMES_HOME`, model credentials and artifacts.

So I would tell the coding agent **not to rewrite that architecture**.

# 1. The stack I would ship today

```text
                  MOLTWORK WORKERKIT
                         │
               standard worker loop
                         │
       FIND → QUALIFY → PLAN → DO → VERIFY
                    → SUBMIT → LEARN
                         │
          ┌──────────────┼───────────────┐
          ▼              ▼               ▼
       RUNTIME          BRAIN           SKILLS
       Hermes           GBrain        Agent Skills
          │              │               │
          │              │           skills.sh
          │              │           Hermes Hub
          │              │           gstack
          │              │           Superpowers
          │              │           Letta skills
          │              │
          └──────────────┼───────────────┘
                         ▼
                    WORK HISTORY
                         │
                         ▼
               capability evidence
                         │
                         ▼
                  SPECIALIZATION
```

### Default production choices

**Execution runtime:** Nous Research Hermes Agent.

Hermes already has self-improving skills, persistent memory, profiles, MCP, model/provider switching, subagents and its own skill ecosystem. Crucially, it is not tied to a single model, so the WorkerKit automatically benefits when stronger models appear. ([GitHub][1])

**Professional brain:** GBrain.

GBrain explicitly supports Hermes over MCP and is designed around "thin harness, fat skills." Its current Hermes integration is literally a local stdio MCP process, so there is no bespoke adapter for us to maintain. ([GitHub][2])

**Skill standard:** Agent Skills / `SKILL.md`.

Do not make `moltwork-skill.json`. Agent Skills already gives us portable skills with instructions, scripts, references and assets. ([GitHub][3])

**Skill package manager:** `npx skills`.

It now explicitly supports Hermes Agent at `.hermes/skills` and `~/.hermes/skills`, as well as dozens of other harnesses. ([GitHub][4])

**Professional methodology:** Superpowers + selected gstack skills.

Superpowers supplies evidence-before-claims, planning, TDD, systematic debugging and review. ([GitHub][5])

gstack adds excellent specialist procedures such as `/investigate`, `/review`, `/qa`, `/retro`, `/browse`, planning/review roles and `/learn`; current gstack installation code even recognizes `~/.hermes/skills/gstack`. ([GitHub][6])

**Continual specialization:** Hermes learning + GBrain Skillify/dream cycle.

This is enough for production v1. Don't put another agent runtime in the loop merely because Memento exists.

Memento-Skills becomes an experimental/reference backend because its validated Read → Execute → Reflect → Rewrite loop is excellent, but it is currently its own runnable agent system rather than a Hermes plugin. ([GitHub][7])

---

# 2. What Moltwork actually owns

Only this:

```text
moltwork-workerkit/
├── get_me_money/             # existing career/economic shell
│
├── workerkit/
│   ├── manifests/
│   ├── builds/
│   └── policies/
│
├── upstreams/
│   └── upstreams.lock.yaml
│
├── install.sh
├── update.sh
├── doctor.sh
│
├── builds/
│   ├── researcher.yaml
│   ├── builder.yaml
│   ├── growth.yaml
│   └── operator.yaml
│
├── frontier/
│   └── README.md
│
└── .github/
    └── workflows/
        ├── upstream-watch.yml
        └── build-canaries.yml
```

Notice what is **not** there:

```text
custom vector database
custom memory engine
custom skill engine
custom multi-agent framework
custom browser
custom coding harness
custom reflection engine
custom skill marketplace format
```

Don't build them.

Moltwork owns **composition + economics + work evidence**.

---

# 3. Clone these upstream projects

I would formally track these.

### Tier A — production dependencies

```bash
git clone https://github.com/NousResearch/hermes-agent.git
git clone https://github.com/garrytan/gbrain.git
git clone https://github.com/agentskills/agentskills.git
git clone https://github.com/vercel-labs/skills.git
git clone https://github.com/obra/superpowers.git
git clone https://github.com/garrytan/gstack.git
git clone https://github.com/letta-ai/skills.git
```

### Tier B — frontier harnesses users can switch to

```bash
git clone https://github.com/letta-ai/letta-code.git
git clone https://github.com/agent0ai/agent-zero.git
```

Letta Code is especially interesting as the alternative "memory-first" harness: its current features include git-versioned MemFS, skill learning, system-prompt learning, sleep-time reflection, `/doctor`, `/palace`, subagents and persistent context. ([GitHub][8])

### Tier C — learning laboratory/reference implementations

```bash
git clone https://github.com/Memento-Teams/Memento-Skills.git
git clone https://github.com/zorazrw/agent-workflow-memory.git
git clone https://github.com/LeapLabTHU/ExpeL.git
git clone https://github.com/OSU-NLP-Group/SkillWeaver.git
git clone https://github.com/noahshinn/reflexion.git
git clone https://github.com/MineDojo/Voyager.git
```

Do **not** wire all six into production.

They are the research shelf that tells us when our learning loop is becoming stale.

Their validated ideas are:

| System      | Pattern we preserve                                        |
| ----------- | ---------------------------------------------------------- |
| Memento     | Read → Execute → Reflect → Rewrite skill                   |
| AWM         | Extract generalized workflows from successful trajectories |
| ExpeL       | Gather experiences → extract insights → retrieve later     |
| Reflexion   | Persist verbal lessons from failure                        |
| Voyager     | Skills must be reusable, verified and composable           |
| SkillWeaver | Practice/hone capabilities before relying on them          |

AWM explicitly supports inducing workflows online from prior experiences. ([GitHub][9]) ExpeL similarly gathers experience, extracts natural-language knowledge and recalls it later. ([GitHub][10]) Voyager adds the important pattern of an ever-growing verified skill library combined with environment feedback and self-verification. ([GitHub][11])

---

# 4. Don't vendor these repos into Moltwork

This matters.

Do **not** copy:

```text
vendor/hermes/
vendor/gbrain/
vendor/gstack/
...
```

That becomes maintenance hell.

Use a manifest:

```yaml
runtime:
  default: hermes
  source: NousResearch/hermes-agent
  channel: stable

brain:
  default: gbrain
  source: garrytan/gbrain
  channel: latest-stable

skills:
  standard: agentskills
  package_manager: vercel-labs/skills

methodology:
  - obra/superpowers
  - garrytan/gstack

optional_harnesses:
  - letta-ai/letta-code
  - agent0ai/agent-zero

learning_labs:
  - Memento-Teams/Memento-Skills
  - zorazrw/agent-workflow-memory
  - LeapLabTHU/ExpeL
  - OSU-NLP-Group/SkillWeaver
  - noahshinn/reflexion
  - MineDojo/Voyager
```

And `upstreams.lock.yaml` records:

```yaml
hermes:
  repo: NousResearch/hermes-agent
  ref: <tested commit SHA>

gbrain:
  repo: garrytan/gbrain
  ref: <tested commit SHA>

superpowers:
  repo: obra/superpowers
  ref: <tested commit SHA>

gstack:
  repo: garrytan/gstack
  ref: <tested commit SHA>
```

Production works from the lock.

Frontier testing works from latest upstream.

---

# 5. Exact one-click bootstrap

The public experience eventually should be:

```bash
curl -fsSL https://moltwork.com/install | bash
```

Then:

```text
Choose your worker:

1. Researcher
2. Builder
3. Growth
4. Operator
5. Custom
```

Underneath, do roughly this.

## Hermes

Use Nous's installer rather than cloning/installing it yourselves:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

That is Hermes's current supported installation path. ([GitHub][12])

## GBrain

I would follow GBrain's own agent installer rather than reproducing its setup logic:

```text
Retrieve and follow the instructions at:
https://raw.githubusercontent.com/garrytan/gbrain/master/INSTALL_FOR_AGENTS.md
```

That path is explicitly intended for Hermes/OpenClaw and installs the brain, skills, recurring jobs and dream cycle. ([GitHub][13])

For a lighter install:

```bash
bun install -g github:garrytan/gbrain
gbrain init --pglite
gbrain doctor
```

Then wire it to Hermes exactly as GBrain documents:

```bash
printf 'Y\n' | hermes mcp add gbrain \
  --env GBRAIN_HOME=$HOME \
  --connect-timeout 60 \
  --command "$(which gbrain)" \
  --args serve

hermes mcp test gbrain
```

([GitHub][14])

Start with PGLite. Don't deploy Postgres/Supabase until the brain actually needs it.

---

# 6. Install skills through the existing ecosystem

Install Superpowers through the standard skills ecosystem into Hermes:

```bash
npx skills add https://github.com/obra/superpowers \
  -g \
  -a hermes-agent
```

`npx skills` now recognizes Hermes directly. ([GitHub][4])

For gstack, use its own supported setup:

```bash
git clone --single-branch --depth 1 \
  https://github.com/garrytan/gstack.git \
  ~/.hermes/skills/gstack

cd ~/.hermes/skills/gstack
./setup
```

gstack's current install tooling explicitly searches that Hermes path. ([GitHub][15])

Then use `npx skills find` when capabilities are missing:

```bash
npx skills find playwright
npx skills find research
npx skills find github
npx skills find pdf
```

And install individual vetted skills:

```bash
npx skills add OWNER/REPO \
  --skill SKILL_NAME \
  -g \
  -a hermes-agent
```

Do **not** blindly `--all` huge collections into Hermes. A recent skills CLI issue documented a category-name collision that could replace an existing Hermes skill directory. Use selected skills and snapshot/lock what you install. ([GitHub][16])

---

# 7. WorkerKit's loop becomes extremely simple

The **mandatory lifecycle** for every build:

```text
1. DISCOVER
      ↓
2. DEDUPLICATE
      ↓
3. QUALIFY
      ↓
4. COMPILE TASK CONTRACT
      ↓
5. CAPABILITY GAP CHECK
      ↓
6. LOAD/ACQUIRE SKILLS
      ↓
7. PLAN
      ↓
8. EXECUTE
      ↓
9. VERIFY
      ↓
10. SUBMIT
      ↓
11. RECORD OUTCOME
      ↓
12. REFLECT
      ↓
13. DISTILL EXPERIENCE
      ↓
14. UPDATE MEMORY/SKILLS
      ↓
15. RE-EVALUATE CAPABILITY
```

That becomes the thing **every Moltwork worker guarantees**.

Everything else is swappable.

Your existing `CapabilityBroker` already gets you surprisingly far toward steps 5–6.

---

# 8. The learning policy

This is where the research projects should shape the product.

Do not allow:

```text
one success
→ permanent skill
```

Use a staged promotion process:

```text
WORKRUN
   ↓
reflection
   ↓
lesson
   ↓
candidate
   ↓
reuse
   ↓
verification
   ↓
promotion
```

I'd use:

```text
1 occurrence
→ episodic memory only

2 occurrences
→ candidate workflow

3 successful occurrences
→ candidate reusable skill

5+ successful occurrences
+ verification
→ established worker skill

cross-worker validation
→ publishable profession-pack skill
```

This is remarkably close to Letta's current community-skill philosophy: one occurrence should remain personal; repeated occurrences justify generalization; multiple instances strengthen the case for sharing. ([GitHub][17])

That's a much safer learning rule than "the LLM thought this was useful."

---

# 9. GBrain becomes the career brain

Use separate namespaces/types for:

```text
worker/
jobs/
clients/
skills/
lessons/
artifacts/
sources/
people/
companies/
domains/
```

And the important semantic distinction is:

```text
RAW WORKRUN
immutable evidence

        ↓

GBRAIN
derived professional understanding
```

Do not dump every terminal command into memory.

Raw traces belong to WorkRun storage.

GBrain should know:

```text
I tried X.
X failed because Y.
Z worked.
This pattern repeated across four jobs.
The accounting-research skill now performs better using Z.
```

GBrain already has synthesis, graph traversal, recurring enrichment and overnight consolidation; that's exactly why it's better here than us building a vector DB. ([GitHub][13])

---

# 10. Starter build #1 — Researcher

Call it something like:

> **Scout — Research & Intelligence Worker**

## Base

```text
WorkerKit Core
Hermes
GBrain
Superpowers generic discipline
```

## Skill sources

Hermes built-in research skills + selected:

```text
web research
source verification
competitive research
GitHub investigation
Reddit/community research
PDF
spreadsheet
report generation
citation verification
```

Pull useful skills dynamically from:

```text
NousResearch/hermes-agent
garrytan/gbrain
letta-ai/skills
skills.sh ecosystem
```

The Letta skill repo already contains reusable PDF, Playwright, spreadsheet, transcription and other operational skills and is itself intentionally a peer-reviewed living skill base. ([GitHub][18])

## Specialized loop

```text
brief
→ research plan
→ source families
→ gather
→ extract claims
→ triangulate
→ analyze
→ adversarial review
→ structured report
→ citation QA
→ submit
→ learn
```

### Work it should pursue

```text
market research
competitive intelligence
lead/company research
Reddit pain-point reports
literature reviews
due diligence
dataset research
fact checking
product research
```

This is probably your first build because it can perform a huge variety of remote jobs without deployment credentials.

---

# 11. Starter build #2 — Builder

> **Forge — Software Engineering Worker**

Base WorkerKit, then install:

```text
Superpowers
gstack
Hermes software development skills
GitHub skills
browser/Playwright QA
deployment skills as required
```

Superpowers gives you the discipline.

gstack gives you the software-company roles.

Hermes gives you runtime/tool access.

## Loop

```text
issue/spec
→ inspect repo
→ reproduce
→ design
→ plan
→ implementation
→ tests
→ review
→ browser QA
→ final diff
→ submission
→ retro
→ skill improvement
```

gstack already ships specialist procedures around engineering planning, review, QA, investigation and retrospectives. ([GitHub][6])

### Work

```text
GitHub issues
bug fixes
small features
API integrations
tests
documentation
refactors
deployment fixes
```

---

# 12. Starter build #3 — Growth

> **Hunter — Prospecting & Growth Worker**

Same WorkerKit.

Different skills:

```text
web/company research
prospecting
competitor research
market mapping
lead enrichment
email research
CRM/data hygiene
spreadsheet generation
copywriting
offer analysis
```

## Loop

```text
ICP/task
→ target definition
→ discovery
→ qualify
→ enrich
→ verify
→ prioritize
→ produce outreach intelligence
→ quality check
→ deliver
→ outcome
→ learn what converts
```

The interesting long-term specialization signal becomes:

```text
generic prospecting
      ↓
SaaS prospecting
      ↓
developer-tool prospecting
      ↓
x402 infrastructure buyer discovery
```

Not because the user selected those labels.

Because its WorkRuns prove those competencies.

---

# 13. Starter build #4 — Operator

> **Relay — Data/API & Automation Worker**

This is the most "agent-native" character.

Skills:

```text
API inspection
MCP
browser automation
data extraction
CSV/JSON transformation
spreadsheet operations
webhooks
Cloudflare
GitHub
deployment
monitoring
documentation
```

## Loop

```text
desired result
→ inspect available interfaces
→ choose API/CLI/browser/MCP
→ authenticate safely
→ execute
→ validate
→ produce structured output
→ monitor if required
→ document repeatable path
→ convert repeated procedure into skill
```

### Work

```text
API integrations
data collection
migration
automation
monitoring
MCP jobs
x402 integration
structured extraction
recurring reports
```

This worker should become incredibly valuable because repeated jobs naturally turn into reusable deterministic workflows.

---

# 14. The four characters then share one genome

```text
                         WORKERKIT

 DISCOVER
 QUALIFY
 PLAN
 ACQUIRE CAPABILITY
 EXECUTE
 VERIFY
 SUBMIT
 LEARN
 RECORD ECONOMICS
 BUILD REPUTATION

        │
 ┌──────┼─────────┬─────────┐
 ▼      ▼         ▼         ▼

Scout   Forge     Hunter    Relay
Research Builder  Growth    Operator
```

And you can eventually expose:

```bash
moltwork install researcher
moltwork install builder
moltwork install growth
moltwork install operator
```

or:

```bash
moltwork worker create
```

Then choose a starting class.

---

# 15. But packs must be overlays, not forks

This is important.

Don't create:

```text
research-hermes
builder-hermes
growth-hermes
operator-hermes
```

Four divergent runtimes would be awful.

Instead:

```text
Hermes
   +
WorkerKit
   +
build manifest
```

Example conceptual `researcher.yaml`:

```yaml
name: researcher

runtime:
  provider: hermes

brain:
  provider: gbrain

methodology:
  - superpowers

skill_sources:
  - nousresearch/hermes-agent
  - garrytan/gbrain
  - letta-ai/skills
  - skills.sh

capabilities:
  - research
  - web
  - sources
  - documents
  - spreadsheets
  - reporting
  - verification

learning:
  reflection: always
  distill_success: true
  distill_failure: true
  skill_promotion_threshold: 3
```

That's configuration, not another framework.

---

# 16. Letta should be a switch

Later:

```bash
moltwork runtime set letta
```

or:

```yaml
runtime:
  provider: letta-code
```

Letta's current architecture is compelling enough to support because it offers memory-first agents with git-tracked memory, sleep-time reflection and skill learning. ([GitHub][19])

But I would **not** default to:

```text
Hermes
inside Letta
inside GBrain
inside Moltwork
```

That's madness.

Instead:

```text
Moltwork WorkerKit
        │
        ├── Hermes + GBrain   ← default
        │
        └── Letta Code        ← alternate
```

Same WorkerKit lifecycle.

Different underlying harness.

---

# 17. Same idea for OpenClaw / Agent Zero / OpenHands

The eventual compatibility matrix:

| Component   | Status                 |
| ----------- | ---------------------- |
| Hermes      | **Recommended**        |
| Letta Code  | Supported experimental |
| OpenClaw    | Supported experimental |
| Agent Zero  | Lab                    |
| OpenHands   | Lab                    |
| Codex       | Lab                    |
| Claude Code | Lab                    |

The beauty of `SKILL.md` is that many skills move with the worker rather than being permanently tied to Hermes. The standard was explicitly designed for cross-product reuse. ([GitHub][20])

---

# 18. How Moltwork stays at the frontier

This should be a first-class system.

Do **not** say:

> WorkerKit uses Hermes 1.2 and GBrain 0.4 forever.

Maintain two channels.

```text
STABLE
known-good combination
real money runs here

FRONTIER
latest upstreams
automatic evals
never touches important jobs
```

Every week:

```text
check Hermes
check GBrain
check gstack
check Superpowers
check skills CLI
check Letta
check Memento
check AWM/ExpeL/etc.
        ↓
new commits/releases?
        ↓
build frontier image
        ↓
run worker eval suite
        ↓
compare against stable
        ↓
better?
   yes ──────► candidate
   no  ──────► retain stable
```

This is how you get "Nous Hermes but continuously current" rather than freezing some stack today.

---

# 19. Evaluate whole workers, not libraries

For each starter build maintain ~20 representative tasks.

Example:

```text
Scout:
5 web research
5 synthesis
5 competitive intelligence
5 structured extraction

Forge:
5 bug fixes
5 features
5 tests
5 repo investigations

Hunter:
5 lead discovery
5 enrichment
5 market maps
5 competitor jobs

Relay:
5 API
5 browser
5 transformations
5 integrations
```

Score:

```text
task success
verification pass
artifact quality
cost
latency
tool failures
human intervention
```

The frontier version gets promoted only when it improves the Worker.

That stops Moltwork from chasing GitHub hype.

---

# 20. Upstream freshness should be automated

Put this in GitHub Actions:

```text
nightly:
    check production dependency releases

weekly:
    test newest upstream commits

on update:
    create candidate lockfile
    construct all 4 workers
    execute eval suites
    generate comparison report

if candidate > stable:
    open promotion PR
```

Never silently auto-upgrade a money-earning worker.

Use:

```text
stable.lock
candidate.lock
frontier.lock
```

That's the correct relationship to the frontier.

---

# 21. Skills should have the same channels

```text
BUILT-IN
Hermes / GBrain

TRUSTED
curated known-good ecosystem skills

EXPERIMENTAL
recent skills.sh/GitHub discoveries

LEARNED
created from this worker's WorkRuns

PROMOTED
learned + repeatedly validated

PUBLISHED
cross-worker validated and distributable
```

And `npx skills` already gives us:

```bash
npx skills find
npx skills add
npx skills check
npx skills update
```

so there is no need to build a skill package manager. ([GitHub][21])

---

# 22. The Capability Broker should stop knowing specific marketplaces

Right now the broker has hard-coded skill knowledge like `mp-research`, `superpowers`, etc.

Conceptually mutate it from:

```text
CODE FEATURE
→ install these six named skills
```

into:

```text
CODE FEATURE

required capabilities:
- inspect-codebase
- plan-change
- implement
- test
- review
- verify

        ↓

resolve capabilities against:

Hermes built-ins
GBrain skillpack
installed Agent Skills
skills.sh
GitHub
worker learned skills
```

The broker should care about **capability**, not vendor.

That's the one refactor worth doing.

Not because we're recreating functionality; because we're deleting vendor coupling.

---

# 23. And don't invent our own learning algorithm

Use a synthesis of the proven processes:

```text
                 MOLTWORK LEARNING

                      RUN
                       │
                       ▼
                external outcome
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
           success             failure
             │                   │
             ▼                   ▼
        AWM / ExpeL          Reflexion
      extract workflow      extract lesson
             │                   │
             └─────────┬─────────┘
                       ▼
                 Memento pattern
               update candidate
                       │
                       ▼
                GBrain Skillify
                  test/review
                       │
                       ▼
                 repeated use
                       │
                       ▼
                  promotion
                       │
                       ▼
                 SKILL.md
```

Almost every box is already validated somewhere.

Moltwork adds the critical signal they don't usually have:

> **Was somebody willing to pay for the result?**

---

# 24. Package the frontier as a playground too

The README should show:

```text
Moltwork WorkerKit

Recommended:
✓ Hermes
✓ GBrain
✓ Superpowers
✓ gstack
✓ Agent Skills

Try another harness:
□ Letta Code
□ OpenClaw
□ Agent Zero
□ OpenHands

Try another memory:
□ Letta
□ GBrain

Explore learning research:
□ Memento-Skills
□ AWM
□ ExpeL
□ Reflexion
□ SkillWeaver
□ Voyager

Skill sources:
□ Hermes Hub
□ skills.sh
□ GBrain
□ Letta Skills
□ GitHub
```

This is exactly the right positioning.

Not:

> We know the final agent architecture.

But:

> **Here is the best tested WorkerKit today. Everything important is modular. Here's the frontier lab if you want to mutate it.**

---

# 25. The dev task I'd give your coding agent

I would make the implementation brief essentially:

```text
MISSION

Turn prx0r/get-me-money into the reference Moltwork WorkerKit distribution.

DO NOT implement new:
- memory systems
- skill formats
- skill package managers
- browser systems
- agent frameworks
- continual-learning algorithms
- vector stores
- multi-agent runtimes.

Use upstream projects.

DEFAULT STACK

Runtime:
NousResearch/hermes-agent

Brain:
garrytan/gbrain via its official Hermes MCP integration

Skills standard:
agentskills/agentskills

Skill manager:
vercel-labs/skills

Professional methodology:
obra/superpowers
garrytan/gstack

Skill/knowledge sources:
NousResearch/hermes-agent
garrytan/gbrain
letta-ai/skills
skills.sh

OPTIONAL RUNTIMES

letta-ai/letta-code
agent0ai/agent-zero

LEARNING RESEARCH TRACKED, NOT REQUIRED AT RUNTIME

Memento-Teams/Memento-Skills
zorazrw/agent-workflow-memory
LeapLabTHU/ExpeL
OSU-NLP-Group/SkillWeaver
noahshinn/reflexion
MineDojo/Voyager

ARCHITECTURAL RULE

get-me-money owns:
opportunity lifecycle
work ledger
WorkRun
economic evaluation
capability requirements
submission state
outcomes
capability evidence
reputation

Upstreams own:
execution
memory
skill loading
reflection mechanisms
browser/tooling
coding methodology
skill distribution.

BUILDS

Create four declarative build manifests:
researcher
builder
growth
operator

All builds must run the exact same WorkerKit lifecycle.

Do not fork Hermes/GBrain/gstack/Superpowers.

Maintain upstream URLs + tested commit SHAs in upstreams.lock.yaml.

Create stable/candidate/frontier channels.

Add automated upstream checks and canary evals.

One install command should:
1. install Hermes using upstream installer
2. install GBrain using upstream instructions
3. connect GBrain to Hermes
4. install selected Agent Skills
5. install chosen Worker build
6. initialize WorkerKit economic/work state
7. run doctor
8. run one smoke-test WorkRun.

The system is complete when:

moltwork install researcher

produces a functioning Hermes worker with:
persistent GBrain
WorkerKit work ledger
selected research capabilities
skill discovery
job-isolated WorkRuns
verification
post-run learning
and a reproducible lockfile.
```

That is the product I would build.

**Not another agent framework.**

It is closer to:

> **Ubuntu for working agents.**

Hermes is one kernel/runtime. GBrain is one brain. `SKILL.md` is the package format. skills.sh is a package ecosystem. Superpowers/gstack are battle-tested professional software. Worker builds are distributions. Moltwork is the career/economic layer that turns all of it into a worker.

And because the underlying pieces are swappable, the WorkerKit can remain current even if the best harness six months from now is no longer Hermes.

[1]: https://github.com/NousResearch/Hermes-Agent?utm_source=chatgpt.com "GitHub - NousResearch/hermes-agent: The agent that grows with you · GitHub"
[2]: https://github.com/garrytan/gbrain/blob/master/docs/ethos/THIN_HARNESS_FAT_SKILLS.md?utm_source=chatgpt.com "gbrain/docs/ethos/THIN_HARNESS_FAT_SKILLS.md at master · garrytan/gbrain · GitHub"
[3]: https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx?utm_source=chatgpt.com "agentskills/docs/specification.mdx at main · agentskills/agentskills · GitHub"
[4]: https://github.com/vercel-labs/skills?utm_source=chatgpt.com "GitHub - vercel-labs/skills: The open agent skills tool - npx skills · GitHub"
[5]: https://github.com/obra/superpowers?pubDate=20260803&utm_source=chatgpt.com "GitHub - obra/superpowers: An agentic skills framework & software development methodology that works. · GitHub"
[6]: https://github.com/garrytan/gstack/blob/main/README.md?ref=explainx&utm_source=chatgpt.com "gstack/README.md at main · garrytan/gstack · GitHub"
[7]: https://github.com/Memento-Teams/Memento-Skills?utm_source=chatgpt.com "GitHub - Memento-Teams/Memento-Skills: Memento-Skills: Let Agents Design Agents · GitHub"
[8]: https://github.com/letta-ai/letta-code/blob/main/README.md?utm_source=chatgpt.com "letta-code/README.md at main · letta-ai/letta-code · GitHub"
[9]: https://github.com/zorazrw/agent-workflow-memory?utm_source=chatgpt.com "GitHub - zorazrw/agent-workflow-memory: AWM: Agent Workflow Memory · GitHub"
[10]: https://github.com/LeapLabTHU/ExpeL?utm_source=chatgpt.com "GitHub - LeapLabTHU/ExpeL · GitHub"
[11]: https://github.com/MineDojo/Voyager?utm_source=chatgpt.com "GitHub - MineDojo/Voyager: An Open-Ended Embodied Agent with Large Language Models · GitHub"
[12]: https://github.com/NousResearch/hermes-agent?contact=enterprise&utm_source=chatgpt.com "GitHub - NousResearch/hermes-agent: The agent that grows with you · GitHub"
[13]: https://github.com/garrytan/gbrain "GitHub - garrytan/gbrain: Garry's Opinionated OpenClaw/Hermes Agent Brain · GitHub"
[14]: https://github.com/garrytan/gbrain/blob/master/docs/mcp/HERMES.md?utm_source=chatgpt.com "gbrain/docs/mcp/HERMES.md at master · garrytan/gbrain · GitHub"
[15]: https://github.com/garrytan/gstack/blob/main/bin/gstack-team-init?utm_source=chatgpt.com "gstack/bin/gstack-team-init at main · garrytan/gstack · GitHub"
[16]: https://github.com/vercel-labs/skills/issues/1723?utm_source=chatgpt.com "[Bug]: Hermes Agent install recursively overwrites a category directory on skill-name collision · Issue #1723 · vercel-labs/skills · GitHub"
[17]: https://github.com/letta-ai/skills/blob/main/CULTURE.md?utm_source=chatgpt.com "skills/CULTURE.md at main · letta-ai/skills · GitHub"
[18]: https://github.com/letta-ai/skills/blob/main/README.md?utm_source=chatgpt.com "skills/README.md at main · letta-ai/skills · GitHub"
[19]: https://github.com/letta-ai/letta/blob/main/README.md?utm_source=chatgpt.com "letta/README.md at main · letta-ai/letta · GitHub"
[20]: https://github.com/Open-Dot-Agents/SKILL.md?utm_source=chatgpt.com "GitHub - Open-Dot-Agents/SKILL.md: Specification and documentation for Agent Skills · GitHub"
[21]: https://github.com/vercel-labs/skills/blob/main/skills/find-skills/SKILL.md?utm_source=chatgpt.com "skills/skills/find-skills/SKILL.md at main · vercel-labs/skills · GitHub"
