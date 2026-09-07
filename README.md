# ZCode + Codex Collaboration

A reusable collaboration Skill for software projects where **Codex plans, ZCode executes, and Codex reviews**.

The goal is to combine a stronger reasoning agent with a lower-cost continuous execution agent without building a custom multi-agent platform.

```text
Current Goal
    ↓
Codex — plan / design / specify
    ↓
ZCode — implement / test / commit
    ↓
Codex — engineering review
    ↓
PASS / FIX_REQUIRED / TAKEOVER / BLOCKED
```

## Why this exists

Many multi-agent workflows waste capability in one of two ways:

- the strongest model spends most of its time on repetitive implementation; or
- the execution model is forced to make architecture decisions it should not own.

This Skill makes the boundary explicit:

- **Codex** owns high-decision-density work: planning, architecture, specifications, ambiguity resolution, engineering review, and final goal review.
- **ZCode** owns most production execution: code, tests, fixtures, documentation, mechanical refactors, validation, and commits.
- Difficult tasks should result in a **more precise Codex specification**, not automatically in Codex taking over implementation.

## Core principles

1. **Codex plans. ZCode executes. Codex reviews.**
2. `DEFAULT_IMPLEMENTATION_OWNER = zcode`.
3. ZCode never silently decides schema shape, public API, architecture boundaries, semantics, or major trade-offs.
4. Git state is the source of truth after interruptions; never blindly re-run a timed-out task.
5. Keep Codex and ZCode in separate Git worktrees when both modify code.
6. Use normal Codex reasoning at `high`; escalate to `ultra` only when the decision value justifies the latency/cost.
7. Codex direct implementation is an exception, mainly after bounded repair failure or explicit safety takeover.
8. Do not build a new queue, daemon, supervisor, database, or orchestration framework merely to connect the two tools.

## Requirements

- ZCode with Skills support enabled
- Git
- Codex CLI available as `codex` on `PATH`
- Codex CLI already authenticated/configured
- Python 3 for the bundled helper scripts

## Quick start

### 1. Download or clone this repository

```bash
git clone https://github.com/SBC9966/zcode-and-codex-.git
```

Or download `dist/skill.zip` directly from this repository.

### 2. Install the Skill into ZCode

Copy or extract the Skill so this file exists:

```text
~/.zcode/skills/zcode-codex-collaboration/SKILL.md
```

A typical layout is:

```text
~/.zcode/skills/zcode-codex-collaboration/
├── SKILL.md
├── agents/
├── scripts/
└── references/
```

Then refresh/enable the Skill in ZCode.

### 3. Prepare your project

The workflow works best with two Git worktrees:

```text
project-main/      ← Codex primary worktree
project-zcode/     ← ZCode execution worktree
```

Example:

```bash
git clone <your-repo-url> project-main
cd project-main
git worktree add ../project-zcode -b zcode/work main
```

Use your real default branch (`main`, `master`, `trunk`, etc.) instead of assuming `main`.

### 4. Run the environment preflight

From either worktree:

```bash
python <skill-dir>/scripts/preflight.py --workspace .
```

If automatic primary-worktree inference is ambiguous, pass it explicitly:

```bash
python <skill-dir>/scripts/preflight.py \
  --workspace . \
  --primary /path/to/project-main
```

The preflight checks:

- Git repository state
- discovered worktrees
- Codex CLI availability
- likely primary worktree
- primary worktree cleanliness
- whether starting a new Codex production invocation is safe

### 5. Bootstrap collaboration in ZCode

Invoke the Skill in ZCode with a request such as:

```text
$zcode-codex-collaboration bootstrap this repository
```

Or:

```text
Use zcode-codex-collaboration for this project. Codex should plan and review; ZCode should implement.
```

The Skill should adapt to the repository's existing `AGENTS.md`, task files, architecture docs, tests, branches, and worktree layout instead of replacing them.

## Typical daily workflow

Once bootstrapped, the intended loop is:

```text
1. ZCode reads repository source of truth
2. Codex creates/updates the execution plan
3. ZCode selects a ready delegated task
4. ZCode implements and validates it
5. ZCode commits the result
6. Codex reviews the real diff/commit
7. ZCode repairs if required
8. Reviewed work is integrated into primary
9. Continue until the current goal passes
```

### Example delegated task

A good Codex-authored task should look more like this:

```text
Task: T003 — Implement AssetSpec validation
Owner: zcode

Objective:
Implement the already-decided AssetSpec validation contract.

Allowed files:
- core/schemas/asset.py
- tests/unit/test_asset.py

Required behavior:
- reject duplicate part IDs
- reject missing relation targets
- preserve canonical serialization

Non-goals:
- do not redesign PartGraph
- do not change public IDs

Validation:
- pytest tests/unit/test_asset.py -q
- ruff check core/schemas/asset.py tests/unit/test_asset.py

Definition of Done:
- all specified cases pass
- no unrelated files changed
```

The important rule is that **ZCode should not have to invent the architecture while implementing the task**.

## Safe Codex invocation

The bundled runner launches Codex in a specific primary worktree and verifies the actual startup header.

```bash
python <skill-dir>/scripts/run_codex.py \
  --workdir /path/to/project-main \
  --prompt-file /path/to/bounded-task.md \
  --effort high \
  --log /path/to/task.log
```

The runner checks the reported:

```text
workdir: ...
reasoning effort: ...
```

If the runtime does not match the requested configuration, the invocation is rejected instead of silently continuing.

## Reasoning policy

Default Codex effort:

```text
high
```

Use `high` for most work:

- Goal planning
- task decomposition
- specifications
- API/schema/interface design
- ordinary architecture interpretation
- ambiguity resolution
- engineering review
- repair specification
- integration planning

Use `ultra` only for explicit escalation, such as:

- architecture/kernel-level decisions
- major irreversible design decisions
- difficult cross-module failure escalation
- high-risk refactors/migrations
- repeated repair failure
- final formal Goal engineering review

This keeps the workflow practical on latency and token cost while preserving stronger reasoning where it materially changes engineering decisions.

## Ambiguity handling

If ZCode reaches a point where it would need to decide any of the following:

- public API shape
- schema shape
- architecture boundary
- dependency choice
- data relationship semantics
- error taxonomy
- compatibility strategy
- major trade-off

it should record:

```text
NEEDS_CODEX_DECISION
```

Then Codex should return a decision or strengthen the task specification.

The workflow should be:

```text
unclear implementation point
    ↓
NEEDS_CODEX_DECISION
    ↓
Codex decision / updated specification
    ↓
ZCode continues implementation
```

## Review and repair

Meaningful production work should be reviewed by Codex after ZCode has performed mechanical validation.

```text
Codex specification
    ↓
ZCode implementation
    ↓
pytest / ruff / mypy / project validation
    ↓
ZCode commit
    ↓
Codex engineering review
```

Codex verdicts:

- `PASS`
- `FIX_REQUIRED`
- `TAKEOVER`
- `BLOCKED`

Automatic repair is bounded to two cycles.

After two failed repair cycles, Codex should decide whether direct takeover is justified or whether the task should be marked blocked.

Small related fixtures/tests/docs may be grouped into a single review batch to avoid wasting Codex latency and reasoning tokens.

## Interruption and timeout recovery

Do not treat a timeout as proof that Codex failed.

If ZCode sees:

- task-output timeout
- UI stopped
- provider disconnect
- machine restart

first inspect:

```bash
git -C <primary-worktree> log --oneline -5
git -C <primary-worktree> status --short
git -C <primary-worktree> diff
```

Also inspect whether the Codex process is still running when possible.

Then classify the interrupted task as one of:

```text
COMPLETED
PARTIAL
NOT_STARTED
STILL_RUNNING
AMBIGUOUS
```

Only after classification should the task be resumed or re-dispatched.

Never blindly re-run a timed-out Codex task, because the first invocation may already have created valid work or committed it.

See `references/recovery.md` for the full recovery decision tree.

## Git integration model

Recommended flow:

```text
Codex specification
    ↓
ZCode branch implementation
    ↓
ZCode commit
    ↓
Codex review of that commit
    ↓
PASS
    ↓
reviewed cherry-pick / merge into primary
    ↓
ZCode rebase/sync to latest primary
```

Do not manually copy files between the two worktrees.

## Repository-owned source of truth

The Skill does not require every project to use the same folder layout.

It looks for the repository's own source of truth, which may include:

- `AGENTS.md`
- architecture documents
- goal/task packages
- checkpoints
- `docs/runtime/CURRENT_EXECUTION_PLAN.md`
- issues or project task files

When the project already has its own conventions, preserve them.

Do not overwrite an existing `AGENTS.md` wholesale just to install this workflow.

## What not to do

Avoid these anti-patterns:

- running Codex and ZCode in the same writable worktree
- letting ZCode make silent architecture decisions
- giving ZCode vague tasks such as "implement the whole feature"
- using `ultra` for every Codex call
- re-running timed-out Codex calls without checking Git state
- trusting an agent's claimed commit hash without verifying Git
- manually copying files between worktrees
- building Redis/queues/supervisors/databases merely to coordinate these two agents
- letting Codex become the routine implementation worker again

## Repository structure

```text
.
├── README.md
├── LICENSE
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── preflight.py
│   └── run_codex.py
├── references/
│   ├── collaboration-contract.md
│   ├── execution-plan.md
│   ├── install-and-bootstrap.md
│   └── recovery.md
└── dist/
    └── skill.zip
```

## Project adaptation

The Skill deliberately does **not** hard-code:

- drive letters or absolute paths
- Goal IDs
- branch names
- repository-specific test commands
- automation IDs
- model providers

Each project keeps its own source of truth in Git and adapts the collaboration protocol to its existing instructions and tooling.

## Status

Early reusable version extracted from a real ZCode + Codex CLI collaboration workflow. It is intentionally small and Git-native rather than a new multi-agent orchestration platform.

The best way to improve it is to test it against unrelated repositories and convert recurring failure patterns into tighter specifications, validation rules, and recovery logic.

## License

MIT License. See [`LICENSE`](./LICENSE).
