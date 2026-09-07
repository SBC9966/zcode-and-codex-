# Install and Bootstrap

## Table of contents

1. Requirements
2. Choose install scope
3. Install in ZCode
4. Share with another user
5. First project bootstrap
6. Optional worktree setup
7. ZCode automation

## 1. Requirements

- ZCode with Skills enabled.
- Git.
- Codex CLI available as `codex` on PATH and already authenticated/configured.
- Python 3 for bundled helper scripts.

No MCP server, database, message queue, or custom daemon is required.

## 2. Choose install scope

This Skill is generic and intended to work across repositories.

### Recommended: Global/user-level

Install once at:

```text
~/.zcode/skills/zcode-codex-collaboration/
```

Use this for normal personal use across multiple projects.

### Optional: Project-local

Install at:

```text
<workspace>/.zcode/skills/zcode-codex-collaboration/
```

Use project-local scope only when:

- the repository intentionally pins a specific Skill version;
- a team wants the Skill version to travel with that repository;
- the project uses a fork with project-specific collaboration behavior;
- global installation is not allowed in the environment.

Do not put the generic Skill into every project merely because the project uses it.

Avoid keeping two independently edited copies (global + project-local). Pick one authoritative installation source.

Project-specific information belongs in the project, not the generic Skill:

- `AGENTS.md`;
- hooks;
- execution plan/checkpoints;
- repository paths;
- project test/build commands;
- goal/task IDs.

## 3. Install in ZCode

For a packaged release, extract `skill.zip` so this exists:

```text
~/.zcode/skills/zcode-codex-collaboration/SKILL.md
```

Then open **Settings -> Skills**, click **Refresh**, enable the Skill, and invoke:

```text
$zcode-codex-collaboration bootstrap this repository
```

If you maintain the Skill in another supported coding agent, ZCode can import it as Copy or Symlink. Choose Global for cross-project use or Project when intentionally scoped to the current workspace.

## 4. Share with another user

For one-off sharing, send `skill.zip` or the Skill folder. The recipient should normally install it at user level.

For a GitHub source, clone/download the repository and copy the Skill contents into the ZCode global Skill directory. Do not require the user's application repository to vendor the Skill.

For team distribution, package the Skill in a ZCode plugin repository using the flat layout:

```text
skills/zcode-codex-collaboration/SKILL.md
skills/zcode-codex-collaboration/references/...
skills/zcode-codex-collaboration/scripts/...
```

Do not nest skills under extra grouping directories.

## 5. First project bootstrap

Invoke:

```text
$zcode-codex-collaboration bootstrap collaboration for this repo
```

The Skill should:

1. run preflight;
2. identify current Git root and worktrees;
3. resolve or ask once for the primary Codex worktree;
4. inspect existing `AGENTS.md`/project instructions;
5. preserve project rules and add only missing collaboration rules;
6. detect the repository's goal/task/checkpoint mechanism;
7. determine output transport mode (`DIRECT_STREAM` or `INCREMENTAL_LOG_STREAM`);
8. ask Codex for a current plan/specification if needed;
9. start under Codex-plans/ZCode-executes/Codex-reviews.

## 6. Optional worktree setup

If only one worktree exists and both agents need to modify code concurrently, prefer creating a second worktree before parallel execution.

Example only:

```bash
git worktree add ../<repo>-zcode -b zcode/execution
```

Adapt the branch/path to the project. Do not create a worktree when the repository is dirty or path/branch safety is ambiguous.

## 7. ZCode automation

The Skill is the reusable protocol. A scheduled ZCode automation is optional.

If unattended continuation is wanted, keep the automation prompt thin, for example:

```text
Use $zcode-codex-collaboration. Resume the repository's current goal from Git/project state. Stop at PASS or BLOCKED.
```

Do not duplicate the full Skill rules in the automation prompt. Put project-specific paths in the automation instance or project configuration, not in the shared Skill.
