# Install and Bootstrap

## Table of contents

1. Requirements
2. Install in ZCode
3. Share with another user
4. First project bootstrap
5. Optional worktree setup
6. ZCode automation

## 1. Requirements

- ZCode with Skills enabled.
- Git.
- Codex CLI available as `codex` on PATH and already authenticated/configured.
- Python 3 for bundled helper scripts (optional but recommended).

No MCP server, database, message queue, or custom daemon is required.

## 2. Install in ZCode

ZCode user-level skills live under:

```text
~/.zcode/skills/<skill-name>/SKILL.md
```

Extract/copy this skill directory to:

```text
~/.zcode/skills/zcode-codex-collaboration/
```

Then open **Settings -> Skills**, refresh, enable the skill, and invoke it with:

```text
$zcode-codex-collaboration bootstrap this repository
```

ZCode can also import skills detected from supported external coding agents. Choose Copy for an independent ZCode copy or Symlink when you intentionally want one shared source.

## 3. Share with another user

For one-off sharing, send the skill archive/folder and have the recipient extract it into their user-level ZCode skill directory.

For team distribution, package the skill in a ZCode plugin repository using the flat layout:

```text
skills/zcode-codex-collaboration/SKILL.md
skills/zcode-codex-collaboration/references/...
skills/zcode-codex-collaboration/scripts/...
```

Do not nest skills under extra grouping directories.

## 4. First project bootstrap

Invoke:

```text
$zcode-codex-collaboration bootstrap collaboration for this repo
```

The skill should:

1. run preflight;
2. identify current Git root and worktrees;
3. resolve or ask once for the primary Codex worktree;
4. inspect existing `AGENTS.md`/project instructions;
5. add the collaboration contract without overwriting project rules;
6. detect the repository's goal/task/checkpoint mechanism;
7. ask Codex for a current execution plan if needed;
8. start the plan under the Codex-plans/ZCode-executes/Codex-reviews model.

## 5. Optional worktree setup

If only one worktree exists and both agents need to modify code concurrently, prefer creating a second worktree before parallel execution.

Example only (adapt branch/path to the project):

```bash
git worktree add ../<repo>-zcode -b zcode/execution
```

Do not create a worktree when the repository is dirty or the intended branch/path would conflict. If safe inference is impossible, ask the user.

## 6. ZCode automation

The Skill itself is the reusable protocol. A ZCode scheduled automation is optional.

If the user wants unattended periodic continuation, configure an existing/new ZCode automation to invoke the skill against the repository, e.g.:

```text
$zcode-codex-collaboration resume the current repository goal; stop at PASS or BLOCKED
```

Do not embed absolute paths in the shared Skill. Put project paths in project-local configuration or the automation instance.
