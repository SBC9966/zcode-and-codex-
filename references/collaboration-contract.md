# Collaboration Contract

## Table of contents

1. Roles
2. Ownership
3. Decision boundary
4. Git/worktree boundary
5. Review and integration
6. Repair/takeover
7. Reasoning policy
8. Repository source of truth

## 1. Roles

### Codex

Codex is the high-decision-density agent:

- lead planner;
- lead architect;
- engineering decision maker;
- specification author;
- ambiguity resolver;
- engineering reviewer;
- integration reviewer;
- final goal reviewer;
- emergency implementation fallback.

Codex should spend expensive reasoning on decisions, not routine edits.

### ZCode

ZCode is the continuous execution agent:

- automation host;
- primary implementation worker;
- test/fixture/docs worker;
- mechanical refactoring worker;
- Blender/tool execution worker when the project needs it;
- validation runner;
- committer of delegated work;
- mechanical verifier.

ZCode mechanical PASS is not engineering PASS.

## 2. Ownership

Default production implementation owner: `zcode`.

Architecture sensitivity, core-contract sensitivity, cross-module scope, or task difficulty do not by themselves change ownership.

For difficult work:

1. Codex resolves the design.
2. Codex writes a deeper implementation specification.
3. ZCode executes it.
4. Codex reviews the actual result.

Codex production takeover is exceptional and must be recorded.

## 3. Decision boundary

ZCode may make local mechanical choices that do not alter public semantics, such as:

- variable names inside an existing convention;
- formatting compatible with project tooling;
- test-data values that do not encode new product semantics;
- equivalent command ordering where no contract depends on it.

ZCode must escalate when the task requires deciding:

- public API or schema shape;
- architecture boundary;
- new dependency/framework;
- persistence/serialization semantics;
- error taxonomy;
- compatibility policy;
- cross-module ownership;
- security/reliability trade-off;
- major data relationships;
- destructive migration.

Use `NEEDS_CODEX_DECISION` rather than guessing.

## 4. Git/worktree boundary

Preferred layout:

- primary worktree: Codex-facing primary/integration branch;
- execution worktree: ZCode-facing implementation/review branch.

Rules:

- never have both agents write the same worktree concurrently;
- require a clean primary worktree before a new Codex production invocation;
- exchange work through Git refs and commits, not file copying;
- inspect real commits/diffs rather than agent-reported hashes;
- keep stable task boundaries clean.

If a project intentionally uses one worktree, do not pretend isolation exists. Run only one writer at a time.

## 5. Review and integration

Normal flow:

1. Codex authors specification.
2. ZCode implements and commits.
3. ZCode runs mechanical validation.
4. Codex reviews the ZCode commit through shared Git refs.
5. On PASS, integrate the reviewed commit into primary.
6. Synchronize ZCode branch onto latest primary.

Review verdicts:

- `PASS`: engineering acceptance.
- `FIX_REQUIRED`: bounded repair specification required.
- `TAKEOVER`: Codex may implement remainder under takeover rule.
- `BLOCKED`: human/environment decision required.

Small low-risk related changes may be reviewed as a batch.

## 6. Repair/takeover

Maximum automatic ZCode repair cycles: 2.

After two failed cycles, Codex chooses:

- `TAKEOVER`, with recorded reason; or
- `BLOCKED`, with exact blocker/evidence.

Do not create endless agent-review loops.

## 7. Reasoning policy

Default Codex reasoning: `high`.

Use `high` for:

- goal planning;
- decomposition;
- specifications;
- ordinary API/schema/interface design;
- ambiguity resolution;
- engineering review;
- repair specification;
- integration planning.

Use `ultra` for:

- architecture constitution/kernel changes;
- major irreversible decisions;
- difficult unresolved cross-module failure;
- repeated repair failure;
- high-risk migration/refactor;
- formal final goal review;
- explicit Codex escalation with reason.

Do not escalate merely because a task is long.

## 8. Repository source of truth

Prefer repository-owned state over chat memory:

- `AGENTS.md` or equivalent project instructions;
- current goal/task source;
- execution plan;
- checkpoints;
- ADR/RFC records;
- Git history and current status;
- real test/artifact evidence.

Never copy a prior project's paths, branch names, goal numbers, automation IDs, model names, or provider settings into a new project without detection/confirmation.
