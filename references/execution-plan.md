# Execution Plan and Task Specification

## Table of contents

1. Plan responsibilities
2. Minimal plan format
3. Delegated ZCode task specification
4. Review task
5. Status transitions

## 1. Plan responsibilities

Codex owns engineering plan structure. ZCode may update only execution status, results, and evidence unless Codex explicitly asks for plan restructuring.

A valid plan must:

- identify the current repository goal;
- preserve already-completed work;
- list only remaining work;
- make dependencies explicit;
- default production implementation to ZCode;
- record why any production task is assigned to Codex;
- identify safe parallelism;
- include integration and final verification.

## 2. Minimal plan format

Markdown is sufficient; a database is unnecessary.

```markdown
# Current Execution Plan

Goal: GOAL-X
Planned by: Codex
Plan status: active

| ID | Task | Owner | Depends on | Status | Notes |
|---|---|---|---|---|---|
| T001 | Define API specification | codex | - | done | decision/spec only |
| T002 | Implement API | zcode | T001 | ready | see specification below |
| T003 | Engineering review | codex | T002 | blocked | review only |
```

Use project-native task files if the repository already has a better format.

## 3. Delegated ZCode task specification

Every nontrivial ZCode production task should include:

```markdown
## T002 — <Title>

### Objective
<one bounded outcome>

### Why
<why this exists in the current goal>

### Dependencies
- T001

### Allowed files/modules
- path/a
- path/b

### Required interfaces
- `TypeName`
- `function_name(...)`

### Required behavior
- ...

### Invariants
- ...

### Constraints
- ...

### Explicit non-goals
- ...

### Required tests
- valid case ...
- invalid case ...
- regression ...

### Validation commands
- `pytest ...`
- `ruff ...`
- `mypy ...`

### Definition of Done
- ...

### Expected commit scope
<files/change class expected>

### Execution results / evidence
<ZCode updates only this section/status unless asked otherwise>
```

For complex tasks add pseudocode, exact signatures, examples, expected JSON/error codes, fixture expectations, or integration sequencing.

If ZCode still needs to invent a public or architectural decision, the specification is incomplete. Set `NEEDS_CODEX_DECISION`.

## 4. Review task

A Codex review should reference:

- the exact ZCode commit hash from Git;
- task specification;
- relevant project architecture/contracts;
- mechanical validation evidence.

Codex must inspect actual diff/state and return one verdict:

`PASS | FIX_REQUIRED | TAKEOVER | BLOCKED`

`FIX_REQUIRED` must include a bounded repair specification.

## 5. Status transitions

Recommended task states:

`blocked -> ready -> working -> implemented -> review -> done`

Exceptional states:

- `NEEDS_CODEX_DECISION`
- `FIX_REQUIRED`
- `TAKEOVER`
- `BLOCKED`
- `BLOCKED_BY_TRANSIENT_INFRA`

Do not infer `done` from an agent narrative. Require repository/test evidence and engineering review when the task needs it.
