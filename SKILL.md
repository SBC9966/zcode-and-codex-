---
name: zcode-codex-collaboration
description: Coordinate ZCode and a local Codex CLI as a two-agent software-engineering pair in any Git project. Use when ZCode should keep a project moving while Codex acts as the stronger planner/architect/reviewer and ZCode performs most implementation, testing, commits, and mechanical verification. Covers safe Git worktree isolation, Codex invocation, reasoning-effort policy, execution-plan handoff, review/repair loops, timeout and restart recovery, and project bootstrap without hard-coded paths.
---

# ZCode + Codex Collaboration

Use a repository-owned collaboration protocol instead of chat-to-chat handoffs.

Core model:

**Codex plans → ZCode implements → Codex reviews.**

Treat Codex as the high-decision-density agent and ZCode as the continuous execution agent. Prefer existing Git, ZCode, and Codex CLI capabilities over building a custom orchestrator.

## Workflow

1. Run the environment preflight.
2. Resolve the primary Codex worktree and the ZCode execution worktree.
3. Load or establish the repository collaboration contract.
4. Ask Codex for a bounded execution plan when no valid plan exists.
5. Execute ZCode-owned ready tasks exactly to specification.
6. Escalate unresolved design decisions to Codex; do not improvise architecture.
7. Submit meaningful implementation batches to Codex for engineering review.
8. Integrate only reviewed work into the primary branch.
9. Recover from timeout/restart from Git state, never from assumptions.
10. Complete only the current repository goal, then stop unless repository policy explicitly allows auto-advance.

## 1. Preflight

Run:

```bash
python <skill-dir>/scripts/preflight.py --workspace .
```

If the primary Codex worktree is already known:

```bash
python <skill-dir>/scripts/preflight.py --workspace . --primary <primary-worktree>
```

Require:

- a Git repository;
- `codex` available on PATH;
- distinct writable worktrees when both agents will modify code;
- a clean primary worktree before starting a new Codex production invocation;
- no duplicate active coordination run for the same task.

If the primary worktree cannot be inferred safely, ask for it once rather than guessing.

Read `references/install-and-bootstrap.md` when setting this workflow up for a new user/project.

## 2. Establish the Collaboration Contract

Use the repository's existing `AGENTS.md` if present. Preserve project-specific instructions and add only the missing collaboration rules.

Load `references/collaboration-contract.md` for the canonical role and ownership policy.

Do not hard-code:

- drive letters or absolute paths from another project;
- Goal IDs;
- branch names beyond configurable defaults;
- automation IDs;
- model names/providers;
- repository-specific test commands.

Prefer project-local configuration and repository source of truth.

## 3. Plan with Codex

Before substantive implementation, locate the repository's current goal/task source of truth. Common locations include:

- `docs/runtime/CURRENT_EXECUTION_PLAN.md`
- `docs/goals/`
- `docs/checkpoints/`
- project issue/task files

If no valid Codex-authored plan exists for the current goal, invoke Codex for **planning only**.

Default Codex reasoning policy:

- `high`: ordinary planning, decomposition, specifications, decisions, reviews;
- `ultra`: architecture-constitution/kernel decisions, difficult failure escalation, high-risk irreversible changes, or final goal review.

Do not use `ultra` merely because a task is large.

Use the bundled runner when possible:

```bash
python <skill-dir>/scripts/run_codex.py \
  --workdir <primary-worktree> \
  --prompt-file <bounded-task.md> \
  --effort high \
  --log <log-file>
```

The runner verifies the real Codex startup header rather than trusting config files.

Codex must convert difficult reasoning into precise executable specifications. Difficulty increases specification depth, not default implementation ownership.

Read `references/execution-plan.md` for task-plan and delegated-task requirements.

## 4. Execute with ZCode

Default production implementation owner: **ZCode**.

For each ready ZCode task:

1. Confirm all dependencies are done.
2. Read the full Codex-authored task specification.
3. Modify only allowed files/modules.
4. Run the specified real validation.
5. Commit the result on the ZCode worktree/branch.
6. Record concise evidence in the execution plan or project task state.
7. Do not mark engineering PASS yourself.

If implementation requires deciding schema shape, public API, architecture boundary, dependency, semantics, data relationships, or another major trade-off, mark `NEEDS_CODEX_DECISION` and ask Codex for a decision/specification update.

## 5. Review with Codex

Batch small related mechanical changes when appropriate. Do not spend a Codex review call on every trivial fixture or formatting edit.

For meaningful production work:

1. Point Codex at the ZCode commit through shared Git refs.
2. Ask Codex to review the actual diff and relevant tests/specification.
3. Accept one of:
   - `PASS`
   - `FIX_REQUIRED`
   - `TAKEOVER`
   - `BLOCKED`
4. On `FIX_REQUIRED`, apply only the bounded repair specification.
5. Allow at most 2 automatic repair cycles.
6. After repeated failure, let Codex choose takeover or blocked status.

Integrate reviewed work into the primary branch by reviewed cherry-pick/merge as appropriate. Then synchronize/rebase the ZCode branch onto latest primary. Never copy files manually between worktrees.

## 6. Codex Direct Implementation Is Exceptional

Codex should not become the default coder simply because work is architecture-sensitive or difficult.

Direct Codex implementation is allowed only when:

- ZCode has failed two bounded implementation/repair cycles against a clear specification;
- Codex explicitly records a safety/recovery reason for takeover; or
- the user explicitly asks Codex to implement directly.

Otherwise use:

**Codex design/specification → ZCode implementation → Codex review.**

## 7. Recover Safely

A ZCode wait timeout, stopped UI, provider disconnect, or machine restart is not proof of task failure.

Before re-dispatching anything:

1. inspect the Codex process if available;
2. inspect primary HEAD;
3. inspect `git status` and diff;
4. inspect recent commits;
5. preserve valid partial work;
6. classify the task as completed / partial / not started / ambiguous.

Read `references/recovery.md` for the recovery decision tree.

Never blindly relaunch the same task after a timeout.

## 8. Finish the Current Goal

When all implementation tasks appear complete:

1. ZCode performs mechanical verification (tests, lint, type checks, artifacts, Git cleanliness, scope checks).
2. Invoke Codex at `ultra` for final goal engineering review when the project uses a formal goal gate.
3. Complete repository checkpoint/update artifacts only after both levels pass.
4. Stop at the current goal unless repository policy explicitly permits auto-advance.

## Hard Constraints

- Do not build a new queue, daemon, supervisor, database, or orchestration framework merely to connect ZCode and Codex.
- Do not let ZCode silently make architecture decisions.
- Do not let Codex drift back into routine production implementation.
- Do not trust agent self-reports when Git/test evidence can verify them.
- Do not overwrite existing `AGENTS.md` project instructions.
- Do not run Codex in the ZCode worktree when isolated worktrees are configured.
- Do not use another project's absolute paths or automation IDs.

## Resources

- `references/collaboration-contract.md` — canonical roles, ownership, review, and takeover policy.
- `references/execution-plan.md` — plan schema and delegated-task specification template.
- `references/recovery.md` — timeout, provider failure, restart, dirty-tree, and ambiguous-state recovery.
- `references/install-and-bootstrap.md` — install/distribution and first-run setup for ZCode + Codex CLI.
- `scripts/preflight.py` — inspect Git/worktree/Codex environment and suggest the safe primary worktree.
- `scripts/run_codex.py` — stream Codex output, log it, and verify requested workdir/reasoning effort.
