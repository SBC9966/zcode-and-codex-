#!/usr/bin/env python3
"""Inspect a Git workspace for safe ZCode/Codex collaboration.

Stdlib-only. Prints JSON by default so an agent can consume it reliably.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


def run(args: list[str], cwd: Path | None = None) -> tuple[int, str]:
    p = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return p.returncode, p.stdout.strip()


def git(cwd: Path, *args: str) -> str:
    code, out = run(["git", *args], cwd)
    if code != 0:
        raise RuntimeError(out or f"git {' '.join(args)} failed")
    return out


def norm(path: str | Path) -> str:
    return os.path.normcase(os.path.realpath(os.path.expanduser(str(path))))


def parse_worktrees(raw: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in raw.splitlines() + [""]:
        if not line.strip():
            if current:
                rows.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    return rows


def branch_of(worktree: dict[str, str]) -> str | None:
    ref = worktree.get("branch")
    if not ref:
        return None
    prefix = "refs/heads/"
    return ref[len(prefix) :] if ref.startswith(prefix) else ref


def choose_primary(current_root: Path, worktrees: list[dict[str, str]], explicit: str | None) -> tuple[str | None, str]:
    if explicit:
        return norm(explicit), "explicit"

    current_norm = norm(current_root)
    candidates: list[tuple[str, str | None]] = []
    for wt in worktrees:
        path = wt.get("worktree")
        if not path:
            continue
        candidates.append((norm(path), branch_of(wt)))

    current_branch = next((b for p, b in candidates if p == current_norm), None)
    preferred = [(p, b) for p, b in candidates if b in {"main", "master", "trunk"}]
    if len(preferred) == 1:
        return preferred[0][0], "single-primary-branch"

    others = [(p, b) for p, b in candidates if p != current_norm]
    if current_branch and current_branch.lower().startswith("zcode/") and len(others) == 1:
        return others[0][0], "single-other-worktree"

    if current_branch in {"main", "master", "trunk"}:
        return current_norm, "current-primary-branch"

    return None, "ambiguous"


def inspect_worktree(path: str) -> dict[str, object]:
    root = Path(path)
    try:
        head = git(root, "rev-parse", "HEAD")
        branch = git(root, "branch", "--show-current")
        status = git(root, "status", "--porcelain")
        return {
            "path": str(root),
            "branch": branch or None,
            "head": head,
            "clean": not bool(status.strip()),
            "status_lines": status.splitlines(),
        }
    except Exception as exc:  # pragma: no cover - defensive diagnostics
        return {"path": str(root), "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--primary", default=None)
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    result: dict[str, object] = {
        "workspace": str(workspace),
        "git_available": bool(shutil.which("git")),
        "codex_path": shutil.which("codex"),
        "warnings": [],
    }

    if not result["git_available"]:
        result["error"] = "git_not_found"
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2

    try:
        root = Path(git(workspace, "rev-parse", "--show-toplevel")).resolve()
    except Exception as exc:
        result["error"] = "not_a_git_repository"
        result["detail"] = str(exc)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 3

    result["git_root"] = str(root)
    raw_worktrees = git(root, "worktree", "list", "--porcelain")
    worktrees = parse_worktrees(raw_worktrees)
    result["worktrees"] = [
        {"path": wt.get("worktree"), "branch": branch_of(wt), "head": wt.get("HEAD")}
        for wt in worktrees
    ]

    primary, reason = choose_primary(root, worktrees, args.primary)
    result["primary_worktree"] = primary
    result["primary_resolution"] = reason

    if result["codex_path"]:
        code, version = run([str(result["codex_path"]), "--version"])
        result["codex_version"] = version if code == 0 else None
        if code != 0:
            result["warnings"].append("codex_found_but_version_check_failed")
    else:
        result["warnings"].append("codex_not_found_on_path")

    result["current"] = inspect_worktree(str(root))
    if primary:
        result["primary"] = inspect_worktree(primary)
        pclean = bool(result["primary"].get("clean")) if isinstance(result["primary"], dict) else False
        result["safe_to_start_new_codex_production_task"] = bool(result["codex_path"]) and pclean
    else:
        result["safe_to_start_new_codex_production_task"] = False
        result["warnings"].append("primary_worktree_ambiguous")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
