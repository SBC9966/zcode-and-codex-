# Recovery and Streaming Decision Tree

## Table of contents

1. Transport mode
2. Wait timeout / stopped UI
3. Duplicate-dispatch prevention
4. Dirty primary tree
5. Provider/network failure
6. Machine restart
7. Ambiguous state

## 1. Transport mode

Determine whether the outer ZCode execution layer can expose live subprocess output.

### DIRECT_STREAM

Use when stdout/stderr is visible incrementally while the runner is still alive.

`run_codex.py` already reads Codex output line-by-line, flushes it to stdout, and mirrors it to a persistent log.

### INCREMENTAL_LOG_STREAM

Use when the outer tool behaves like:

```text
exec_xxx -> wait/poll -> timeout -> wait/poll
```

In this mode, treat the persistent log as the observation channel and read only new bytes since the previous cursor:

```bash
python <skill-dir>/scripts/read_codex_progress.py \
  --log <task.log> \
  --offset <previous-offset> \
  --workdir <primary-worktree>
```

Use the returned `next_offset` for the next read.

The cursor is only an observation cache. Source of truth remains:

```text
process + persistent log + Git state
```

Do not create a task database, watchdog daemon, Redis queue, or new supervisor for this.

Do not restart a running Codex invocation merely to move it onto a newer runner/transport mode. Adopt the new mode from the next safe invocation.

## 2. Wait timeout or stopped UI

A waiting/observation timeout is **not** a task failure.

Before re-dispatch:

1. Check whether the Codex process still exists if process inspection is available.
2. Read incremental new log output from the last offset.
3. Record primary HEAD.
4. Run `git status --porcelain`.
5. Inspect current diff.
6. Inspect recent commits.
7. Preserve valid partial artifacts/changes.

Classify the task:

### RUNNING

Evidence: process exists, log continues to grow, or repository activity is consistent with the task.

Action: continue observation. Never launch a duplicate writer.

### COMPLETED

Evidence: expected commit/output exists and process exited or task completion is otherwise verified.

Action: verify the result; do not rerun.

### PARTIAL

Evidence: no complete task commit, but valid task-related work/log evidence exists.

Action: preserve it. Resume the same bounded task with instructions to inspect existing work before modifying anything.

### NOT_STARTED

Evidence: no task commit, no related diff/artifact/log progress, and process is not running.

Action: safe to dispatch the bounded task.

### AMBIGUOUS

Evidence sources disagree materially or process ownership cannot be determined.

Action: do not guess. Perform bounded state analysis or escalate.

### FAILED

Evidence: process exited unsuccessfully and Git/log evidence shows no valid completed result. Distinguish engineering failure from transport failure.

Action: follow bounded retry/repair policy.

## 3. Duplicate-dispatch prevention

Before every Codex launch, verify:

- no known process is still handling the same task;
- the intended task log is not an unexplained active/recovery log;
- primary HEAD/status do not show an in-progress copy of the same task;
- the execution plan does not already mark the task as running/reviewing.

`run_codex.py` refuses to overwrite a non-empty existing log unless explicitly told to append/overwrite it. This is an evidence-preservation guard, not a complete scheduler.

A UI timeout alone never satisfies the conditions for re-dispatch.

## 4. Dirty primary tree

Never launch a new independent Codex production task into unexplained dirty state.

If dirty changes match the interrupted task, resume that task.

If changes are unrelated or origin is unclear, mark `RECOVERY_STATE_AMBIGUOUS` and request bounded state analysis.

Never reset/delete valid partial work merely to regain cleanliness.

## 5. Provider/network failure

Treat transport/stream failures separately from engineering failures.

Immediate transient retries: at most 2.

Before each retry, inspect process + log + Git state first. A provider reconnect handled inside the existing Codex process is not a reason to launch another invocation.

After repeated transport failure, mark `BLOCKED_BY_TRANSIENT_INFRA` or use the project's existing automation later. Do not build a new watchdog solely for this.

## 6. Machine restart

After restart:

1. rerun preflight;
2. inspect both worktrees;
3. read repository current plan/state;
4. inspect primary HEAD/diff/recent commits;
5. inspect the persistent task log if present;
6. classify the interrupted task using the states above;
7. continue the existing plan rather than re-planning from chat memory.

A previous byte offset may be lost after restart. That is acceptable; it is not source of truth. Resume observation from a safe point or inspect the existing log directly.

## 7. Ambiguous state

If Git state, execution plan, process evidence, and logs disagree materially:

- do not guess;
- do not copy files across worktrees;
- do not blindly reset/rebase;
- ask Codex for a bounded repository-state analysis when safe;
- escalate to the user when destructive or irreversible resolution would be required.
