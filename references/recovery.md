# Recovery Decision Tree

## Table of contents

1. Timeout/stopped UI
2. Dirty primary tree
3. Network/provider failure
4. Machine restart
5. Ambiguous state

## 1. Timeout or stopped UI

A waiting timeout is not a task failure.

Before re-dispatch:

1. Check whether the Codex process still exists if process inspection is available.
2. Record primary HEAD.
3. Run `git status --porcelain`.
4. Inspect current diff.
5. Inspect recent commits.
6. Inspect the Codex log.

Classify:

### Completed
A new task commit exists and the worktree is stable.

Action: verify the commit; do not rerun.

### Partial
No complete task commit, but valid task-related modifications exist.

Action: preserve them. Resume the same task with Codex instructed to inspect and continue existing work.

### Not started
No task commit, no task-related diff, process exited.

Action: safe to re-dispatch the bounded task.

### Still running
Process exists or repository is actively changing consistently with the task.

Action: wait. Do not create a duplicate writer.

## 2. Dirty primary tree

Never launch a new independent Codex production task into unexplained dirty state.

If dirty changes match the interrupted task, resume that task.

If changes are unrelated or origin is unclear, mark `RECOVERY_STATE_AMBIGUOUS` and ask Codex for state analysis or the user when necessary.

Never reset/delete valid partial work merely to regain cleanliness.

## 3. Network/provider failure

Treat transport/stream failures separately from engineering failures.

Immediate transient retries: at most 2.

Before each retry, inspect Git state first.

After repeated transport failure, mark `BLOCKED_BY_TRANSIENT_INFRA` or allow the project's existing scheduled automation to retry later. Do not build a new watchdog solely for this.

## 4. Machine restart

After restart:

1. rerun environment preflight;
2. inspect both worktrees;
3. read repository current plan/state;
4. inspect primary HEAD/diff/recent commits;
5. recover the interrupted task using the classification above;
6. continue the existing plan rather than re-planning from chat memory.

## 5. Ambiguous state

If Git state, execution plan, and logs disagree materially:

- do not guess;
- do not copy files across worktrees;
- do not blindly reset/rebase;
- ask Codex for a bounded repository-state analysis if safe;
- escalate to the user when destructive or irreversible resolution would be required.
