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
- Python 3 for the bundled helper scripts (recommended)

## Install

Copy or extract this repository into your ZCode user-level Skill directory so that the entrypoint resolves as:

```text
~/.zcode/skills/zcode-codex-collaboration/SKILL.md
```

Then refresh/enable the Skill in ZCode and invoke it with:

```text
$zcode-codex-collaboration bootstrap this repository
```

You can also download the packaged archive from `dist/skill.zip`.

## What the Skill does

### 1. Environment preflight

```bash
python scripts/preflight.py --workspace .
```

Checks the repository, worktrees, Codex availability, primary-worktree safety, and whether a new Codex production invocation is safe.

### 2. Safe Codex invocation

```bash
python scripts/run_codex.py \
  --workdir <primary-worktree> \
  --prompt-file <bounded-task.md> \
  --effort high \
  --log <task.log>
```

The runner verifies the **actual Codex startup header**, including the working directory and requested reasoning effort, instead of trusting configuration files or self-reports.

### 3. Repository-owned execution plan

Codex produces a bounded execution plan with:

- task IDs
- owners (`zcode` or `codex`)
- dependencies
- allowed files/modules
- required interfaces and behavior
- invariants and constraints
- tests and validation commands
- Definition of Done
- expected commit scope

ZCode executes only ready tasks whose design is sufficiently specified.

### 4. Ambiguity escalation

If implementation still requires a high-level engineering choice, ZCode records:

```text
NEEDS_CODEX_DECISION
```

Codex resolves the decision or strengthens the specification, then ZCode continues.

### 5. Review and bounded repair

```text
Codex specification
    ↓
ZCode implementation
    ↓
Mechanical validation
    ↓
Codex engineering review
    ↓
PASS / FIX_REQUIRED / TAKEOVER / BLOCKED
```

Automatic repair is bounded to two cycles before Codex decides whether to take over or mark the work blocked.

### 6. Safe interruption recovery

A timeout, provider disconnect, stopped UI, or machine restart is not automatically a task failure.

The Skill first checks:

- running process state
- primary `HEAD`
- `git status`
- diff
- recent commits
- valid partial work

Then it classifies the task as completed, partial, not started, still running, or ambiguous before deciding whether to resume/re-dispatch.

## Reasoning policy

Default Codex effort:

```text
high
```

Use `ultra` only for explicit escalation, such as:

- architecture/kernel-level decisions
- major irreversible design decisions
- difficult cross-module failure escalation
- high-risk refactors/migrations
- repeated repair failure
- final formal Goal engineering review

This keeps the collaboration practical on latency and token cost while preserving stronger reasoning where it materially changes engineering decisions.

## Repository structure

```text
.
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── preflight.py
│   └── run_codex.py
├── references/
│   ├── api_reference.md
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

Each project keeps its own source of truth in Git and adapts the collaboration protocol to its existing `AGENTS.md`, task/goal files, tests, and worktree layout.

## Status

Early reusable version extracted from a real ZCode + Codex CLI collaboration workflow. Treat it as an engineering protocol that should be tested against multiple repositories and iterated from real failures.
