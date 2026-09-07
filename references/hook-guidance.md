# Hook Guidance

Hooks should remain small reminders and recovery entry points. They must not duplicate the full Skill or become a second coordinator.

## SessionStart

Recommended intent:

```text
If zcode-codex-collaboration is available, use its recovery protocol.
Restore project state from Git, AGENTS.md, the current execution plan, checkpoints, and existing Codex logs before continuing.
If a prior Codex task may still be running or partially complete, inspect process + log + Git before dispatching another invocation.
```

## UserPromptSubmit

Recommended intent:

```text
Apply the repository collaboration policy before launching new work.
Check whether the request belongs to an already-active task.
Do not duplicate-dispatch after a wait/observation timeout.
Prefer the repository-approved Codex runner and persistent log when Codex is needed.
```

## Stop

Recommended intent:

```text
Do not interpret UI timeout, interrupted observation, or missing fresh output as Codex failure.
Before marking work incomplete or re-dispatching, inspect process state, incremental log growth, HEAD, git status, recent commits, and partial artifacts.
```

## Rules

- Keep each hook concise.
- Do not paste the entire Skill or automation prompt into hooks.
- Do not make hooks create queues, daemons, databases, or competing coordinators.
- Do not use hooks to silently modify architecture/project policy.
- If the project already has working hooks, edit only the minimum text needed to align timeout/recovery behavior.
