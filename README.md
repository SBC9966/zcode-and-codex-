# ZCode + Codex Collaboration

A reusable ZCode Skill for software projects where **Codex plans, ZCode executes, and Codex reviews**.

```text
Current Goal
    |
    v
Codex - plan / decide / specify
    |
    v
ZCode - implement / test / commit
    |
    v
Codex - engineering review
    |
    v
PASS / FIX_REQUIRED / TAKEOVER / BLOCKED
```

The Skill keeps the collaboration Git-native: no Redis, no new queue, no custom supervisor, and no second orchestration platform.

## What changed in v1.1

- Global/user-level installation is now the recommended default for this generic Skill.
- Project-local installation is reserved for intentionally pinned/forked versions.
- Added `DIRECT_STREAM` vs `INCREMENTAL_LOG_STREAM` transport selection.
- Added `scripts/read_codex_progress.py` for `exec_xxx -> wait/poll` outer executors.
- Added protection against silently overwriting an existing Codex recovery log.
- Added lightweight runner start/exit markers with PID.
- Added explicit duplicate-dispatch prevention: **wait timeout != task failure**.
- Added concise hook guidance; hooks remain reminders rather than another coordinator.

## Roles

### Codex

Owns high-decision-density work:

- planning and decomposition;
- architecture/API/schema decisions;
- detailed implementation specifications;
- ambiguity resolution;
- engineering review;
- final formal goal review;
- rare emergency takeover.

### ZCode

Owns most production execution:

- implementation;
- tests and fixtures;
- documentation;
- mechanical refactors;
- tool/Blender execution;
- validation;
- commits;
- continuous task progress.

**Difficulty increases Codex specification depth; it does not automatically transfer implementation ownership to Codex.**

## Requirements

- ZCode with Skills support
- Git
- Codex CLI available as `codex` on `PATH`
- Codex CLI already authenticated/configured
- Python 3

## Install: Global is recommended

For this generic cross-project Skill, install once at user level:

```text
~/.zcode/skills/zcode-codex-collaboration/
```

After extracting `dist/skill.zip`, this should exist:

```text
~/.zcode/skills/zcode-codex-collaboration/SKILL.md
```

Then open **Settings -> Skills**, click **Refresh**, enable it, and use:

```text
$zcode-codex-collaboration bootstrap this repository
```

### Do I need to copy the Skill into my current project?

Usually **no**.

Keep the generic Skill global. Keep project-specific state inside the repository:

```text
project/
├── AGENTS.md
├── project hook configuration
├── execution plan / checkpoints
├── architecture docs
└── project-specific commands and paths
```

Use project-local Skill installation only when you intentionally want a pinned/forked version for one repository:

```text
<workspace>/.zcode/skills/zcode-codex-collaboration/
```

Avoid keeping both global and project-local editable copies because they can drift.

## Recommended worktree model

```text
project-main/      <- Codex primary/integration worktree
project-zcode/     <- ZCode execution worktree
```

Example only:

```bash
git worktree add ../project-zcode -b zcode/execution
```

Adapt branch/path to the real project. Do not create a worktree from unexplained dirty state.

## Preflight

```bash
python <skill-dir>/scripts/preflight.py --workspace .
```

Or when primary inference is ambiguous:

```bash
python <skill-dir>/scripts/preflight.py \
  --workspace . \
  --primary /path/to/project-main
```

The preflight checks Git/worktrees, Codex availability, likely primary worktree, cleanliness, and whether a new independent Codex invocation is safe.

## Codex invocation

```bash
python <skill-dir>/scripts/run_codex.py \
  --workdir /path/to/project-main \
  --prompt-file /path/to/bounded-task.md \
  --effort high \
  --log /path/to/task.log
```

The runner:

- launches Codex in the requested worktree;
- reads stdout/stderr line-by-line;
- mirrors output to a persistent log;
- verifies actual `workdir:` and `reasoning effort:` startup headers;
- refuses unexplained dirty primary state;
- refuses to overwrite a non-empty existing task log unless explicitly requested.

If startup configuration differs from the request, it returns:

```text
CODEX_REASONING_CONFIGURATION_MISMATCH
```

## Streaming modes

### DIRECT_STREAM

Use when ZCode can display the runner's stdout while the process is still active.

```text
Codex -> run_codex.py -> ZCode live output
                    `-> persistent log
```

### INCREMENTAL_LOG_STREAM

Use when ZCode's outer execution tool behaves like:

```text
exec_xxx -> wait/poll -> timeout -> fetch output again
```

The outer layer cannot be made truly direct-streaming from inside this Skill. Instead:

```text
Codex
  |
  v
run_codex.py
  |
  +--> persistent task.log
             |
             v
read_codex_progress.py --offset N
             |
             v
only newly-added output + next_offset
```

Example:

```bash
python <skill-dir>/scripts/read_codex_progress.py \
  --log /path/to/task.log \
  --offset 18422 \
  --workdir /path/to/project-main
```

The returned byte offset is only an observation cursor. The real recovery evidence remains:

```text
process + persistent log + Git state
```

## Timeout and duplicate-dispatch protection

A ZCode wait timeout means only that the current observation window ended.

It does **not** mean:

```text
Codex failed
```

Before re-dispatching, inspect:

- whether the Codex process still exists;
- whether the log has grown;
- incremental new log output;
- primary HEAD;
- `git status` and diff;
- recent commits;
- valid partial artifacts.

Classify the task as:

```text
RUNNING
COMPLETED
PARTIAL
NOT_STARTED
AMBIGUOUS
FAILED
```

Only a safely classified `NOT_STARTED`/`FAILED` state should be considered for a new invocation.

## Reasoning policy

Default Codex reasoning effort:

```text
high
```

Use `high` for most planning, specifications, architecture interpretation, API/schema design, ambiguity resolution, engineering review, repair specification, and integration planning.

Escalate to `ultra` only for cases such as:

- architecture/kernel-level decisions;
- major irreversible decisions;
- difficult unresolved cross-module failures;
- repeated repair failure;
- high-risk migrations/refactors;
- formal final Goal engineering review.

## Ambiguity rule

If ZCode would need to invent a public/architectural decision, use:

```text
NEEDS_CODEX_DECISION
```

Then Codex supplies the missing decision or strengthens the specification; ZCode resumes implementation.

## Review loop

```text
Codex specification
    |
    v
ZCode implementation + mechanical validation
    |
    v
ZCode commit
    |
    v
Codex engineering review
    |
    +--> PASS
    +--> FIX_REQUIRED -> ZCode bounded repair
    +--> TAKEOVER
    `--> BLOCKED
```

Maximum automatic ZCode repair cycles: **2**.

## Hooks stay thin

Do not copy the entire Skill into `SessionStart`, `UserPromptSubmit`, or `Stop` hooks.

Hooks should only remind ZCode to:

- restore project state from Git/plan/checkpoints;
- avoid duplicate dispatch;
- use the approved runner/log;
- treat wait timeout as an observation event rather than failure.

See `references/hook-guidance.md`.

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
│   ├── run_codex.py
│   └── read_codex_progress.py
├── references/
│   ├── collaboration-contract.md
│   ├── execution-plan.md
│   ├── hook-guidance.md
│   ├── install-and-bootstrap.md
│   └── recovery.md
└── dist/
    └── skill.zip
```

## What not to do

- Do not run Codex and ZCode as concurrent writers in the same worktree.
- Do not let ZCode silently make architecture decisions.
- Do not use `ultra` for every Codex call.
- Do not re-run a timed-out Codex call without process/log/Git checks.
- Do not overwrite recovery logs by default.
- Do not manually copy implementation files between worktrees.
- Do not build Redis/queues/supervisors/databases merely to coordinate these two agents.
- Do not copy this generic Skill into every project unless project-local pinning is intentional.

## License

MIT License. See [`LICENSE`](./LICENSE).
