---
name: zcode-codex-collaboration
description: Coordinate ZCode and a local Codex CLI as a two-agent software-engineering pair in any Git project. Use when Codex should own planning, architecture decisions, specifications, ambiguity resolution, and engineering review while ZCode owns most implementation, testing, validation, and commits. Covers Git worktree isolation, verified Codex invocation, high/ultra reasoning policy, direct or incremental-log streaming, duplicate-dispatch prevention, timeout/restart recovery, and project bootstrap without hard-coded paths.
---

# ZCode + Codex Collaboration

Use Git and repository-owned state to coordinate two agents without introducing a separate orchestration platform.

Core model:

**Codex plans -> ZCode implements -> Codex reviews.**

Treat Codex as the high-decision-density agent and ZCode as the continuous execution agent.

## Workflow

1. Run environment preflight.
2. Resolve the Codex primary worktree and ZCode execution worktree.
3. Load project instructions and the collaboration contract.
4. Detect the available Codex-output transport mode.
5. Ask Codex for a bounded plan/specification when needed.
6. Execute ZCode-owned ready tasks exactly to specification.
7. Escalate unresolved engineering decisions to Codex.
8. Review meaningful implementation batches with Codex.
9. Integrate only reviewed work.
10. Recover from timeout/restart using process + log + Git evidence.
11. Finish only the current project goal unless project policy explicitly permits auto-advance.

## 1. Install Scope

Prefer installing this generic Skill once at ZCode user level:

```text
~/.zcode/skills/zcode-codex-collaboration/
```

Do **not** copy it into every project by default.

Use project-local installation only when the repository intentionally needs a pinned or forked Skill version:

```text
<workspace>/.zcode/skills/zcode-codex-collaboration/
```

Keep project-specific state in the project instead:

- `AGENTS.md` or equivalent instructions;
- hook configuration/text;
- current execution plan;
- checkpoints / ADRs / RFCs;
- repository-specific commands and paths.

Avoid maintaining both a global editable copy and a project-local editable copy because they drift.

Read `references/install-and-bootstrap.md` for installation and first-run guidance.

## 2. Preflight

Run:

```bash
python <skill-dir>/scripts/preflight.py --workspace .
```

If the Codex primary worktree is already known:

```bash
python <skill-dir>/scripts/preflight.py --workspace . --primary <primary-worktree>
```

Require:

- a Git repository;
- `codex` available on PATH;
- distinct writable worktrees when both agents may write concurrently;
- a clean primary worktree before a new independent Codex production invocation;
- no duplicate active invocation for the same bounded task.

If the primary worktree cannot be inferred safely, ask once instead of guessing.

## 3. Establish the Collaboration Contract

Use the repository's existing `AGENTS.md` if present. Preserve project-specific instructions and add only missing collaboration rules.

Load `references/collaboration-contract.md` for canonical roles and ownership.

Do not hard-code another project's:

- absolute paths;
- goal IDs;
- branch names;
- automation IDs;
- model/provider names;
- test commands.

Repository state is the source of truth.

## 4. Select Output Transport Mode

Detect how the outer ZCode execution layer exposes subprocess output.

### DIRECT_STREAM

Use `DIRECT_STREAM` only when ZCode can observe the runner's stdout/stderr incrementally while the process is still running.

The approved runner already streams Codex output line-by-line and mirrors it to a persistent log:

```bash
python <skill-dir>/scripts/run_codex.py \
  --workdir <primary-worktree> \
  --prompt-file <bounded-task.md> \
  --effort high \
  --log <task.log>
```

### INCREMENTAL_LOG_STREAM

If the outer tool is an opaque `exec_xxx -> wait/poll` handle, do not pretend it is direct streaming.

Use:

**Codex -> run_codex.py -> persistent log -> incremental offset reads.**

Read only new log bytes since the previous cursor:

```bash
python <skill-dir>/scripts/read_codex_progress.py \
  --log <task.log> \
  --offset <previous-byte-offset> \
  --workdir <primary-worktree>
```

The command returns the new output plus `next_offset`. Treat that offset as an observation cursor only.

Source of truth remains:

**process + persistent log + Git state.**

Do not create a queue, task database, watchdog daemon, or new orchestration state machine just to improve observability.

Do not restart an already-running Codex invocation merely to switch it to a new transport mode. Apply a new runner/transport mode from the next safe invocation.

## 5. Plan with Codex

Locate the repository's current goal/task source of truth before substantive work. Common locations include:

- `docs/runtime/CURRENT_EXECUTION_PLAN.md`;
- `docs/goals/`;
- `docs/checkpoints/`;
- project issue/task files.

If no valid Codex-authored plan exists for the current goal, invoke Codex for planning/specification.

Default Codex reasoning:

- `high`: planning, decomposition, specifications, ordinary architecture/API decisions, ambiguity resolution, reviews, repairs, integration planning;
- `ultra`: architecture-constitution/kernel changes, major irreversible decisions, difficult unresolved failures, repeated repair failure, high-risk migration/refactor, formal final-goal review.

Do not use `ultra` merely because a task is large or important.

Codex must convert difficult reasoning into precise executable specifications. Difficulty increases specification depth, not default implementation ownership.

Read `references/execution-plan.md` for plan/task requirements.

## 6. Execute with ZCode

Default production implementation owner: **ZCode**.

For each ready ZCode task:

1. Confirm dependencies are complete.
2. Read the full Codex-authored specification.
3. Modify only allowed files/modules.
4. Run required real validation.
5. Commit on the ZCode worktree/branch.
6. Record concise evidence in repository task state.
7. Do not self-declare engineering PASS.

If implementation requires deciding schema shape, public API, architecture boundary, dependency, semantics, data relationships, compatibility, security/reliability policy, or another major trade-off, set:

```text
NEEDS_CODEX_DECISION
```

Ask Codex for the missing decision/specification rather than guessing.

## 7. Review with Codex

Batch small related mechanical changes when appropriate; do not invoke expensive review for every trivial fixture/edit.

For meaningful production work:

1. Point Codex at the exact ZCode commit through Git refs.
2. Ask Codex to review the actual diff, task specification, and validation evidence.
3. Accept exactly one verdict:
   - `PASS`
   - `FIX_REQUIRED`
   - `TAKEOVER`
   - `BLOCKED`
4. On `FIX_REQUIRED`, apply only the bounded repair specification.
5. Allow at most 2 automatic repair cycles.
6. After repeated failure, Codex chooses takeover or blocked status.

On PASS, integrate by reviewed cherry-pick/merge as appropriate, then synchronize ZCode onto latest primary. Never manually copy files between worktrees.

## 8. Codex Direct Implementation Is Exceptional

Do not transfer implementation ownership to Codex just because work is difficult or architecture-sensitive.

Allow direct Codex production implementation only when:

- ZCode failed two bounded implementation/repair cycles against a clear specification;
- Codex explicitly records a safety/recovery reason for takeover; or
- the user explicitly asks Codex to implement directly.

Otherwise use:

**Codex design/specification -> ZCode implementation -> Codex review.**

## 9. Recover Safely

A ZCode wait timeout, stopped UI, provider disconnect, or machine restart is not proof of task failure.

Before any re-dispatch:

1. inspect the Codex process if possible;
2. inspect log growth and incremental new output;
3. inspect primary HEAD;
4. inspect `git status`, diff, and recent commits;
5. preserve valid partial work;
6. classify the task as `RUNNING`, `COMPLETED`, `PARTIAL`, `NOT_STARTED`, `AMBIGUOUS`, or `FAILED`.

Never duplicate-dispatch because an observation/wait window timed out.

Read `references/recovery.md` for the full decision tree.

## 10. Keep Hooks Thin

Hooks are reminders and recovery entry points, not an orchestration engine.

Keep `SessionStart`, `UserPromptSubmit`, and `Stop` text short. Let this Skill hold the detailed rules.

Read `references/hook-guidance.md` before creating or revising ZCode hook text.

## 11. Finish the Current Goal

When implementation appears complete:

1. ZCode performs mechanical verification: tests, lint, type checks, artifacts, scope, Git cleanliness.
2. If the project uses a formal goal gate, invoke Codex at `ultra` for final engineering review.
3. Update checkpoints/project state only after required review passes.
4. Stop at the current goal unless repository policy explicitly allows auto-advance.

## Hard Constraints

- Do not build a new queue, daemon, supervisor, database, or orchestration framework merely to connect ZCode and Codex.
- Do not let ZCode silently make architecture decisions.
- Do not let Codex drift into routine production implementation.
- Do not trust agent self-reports when Git/test evidence can verify them.
- Do not overwrite existing project instructions.
- Do not run Codex in the ZCode worktree when isolated worktrees are configured.
- Do not use another project's paths or automation IDs.
- Do not treat `wait timeout` as `task failed`.
- Do not overwrite an existing recovery log by default.

## Resources

- `references/collaboration-contract.md` - roles, ownership, review, takeover.
- `references/execution-plan.md` - execution-plan and delegated-task specification.
- `references/recovery.md` - timeout, incremental-log observation, provider failure, restart recovery.
- `references/install-and-bootstrap.md` - global/project install policy and first-run setup.
- `references/hook-guidance.md` - concise hook responsibilities and templates.
- `scripts/preflight.py` - inspect Git/worktree/Codex environment.
- `scripts/run_codex.py` - stream Codex output, persist a log, and verify startup configuration.
- `scripts/read_codex_progress.py` - read only new bytes from a persistent Codex log for wait/poll outer executors.
