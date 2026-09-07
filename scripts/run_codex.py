#!/usr/bin/env python3
"""Run Codex in a specific worktree and verify its startup header.

Streams merged stdout/stderr to the caller and an optional log. The script
refuses an unexplained dirty primary tree by default and checks the actual
reported workdir and reasoning effort.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def norm(path: str | Path) -> str:
    return os.path.normcase(os.path.realpath(os.path.expanduser(str(path))))


def git_clean(workdir: Path) -> tuple[bool, str]:
    p = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(workdir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if p.returncode != 0:
        raise RuntimeError(p.stdout.strip() or "git status failed")
    return not bool(p.stdout.strip()), p.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", required=True)
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--effort", choices=["high", "ultra"], default="high")
    parser.add_argument("--log", default=None)
    parser.add_argument("--sandbox", default="workspace-write")
    parser.add_argument("--allow-dirty", action="store_true")
    args = parser.parse_args()

    codex = shutil.which("codex")
    if not codex:
        print("ERROR: codex not found on PATH", file=sys.stderr)
        return 20

    workdir = Path(args.workdir).expanduser().resolve()
    prompt_file = Path(args.prompt_file).expanduser().resolve()
    if not prompt_file.is_file():
        print(f"ERROR: prompt file not found: {prompt_file}", file=sys.stderr)
        return 21

    try:
        clean, status = git_clean(workdir)
    except Exception as exc:
        print(f"ERROR: cannot inspect primary worktree: {exc}", file=sys.stderr)
        return 22

    if not clean and not args.allow_dirty:
        print("ERROR: primary worktree is dirty; inspect/resume existing work before launching another task", file=sys.stderr)
        print(status, file=sys.stderr)
        return 23

    prompt = prompt_file.read_text(encoding="utf-8")
    command = [
        codex,
        "exec",
        "-s",
        args.sandbox,
        "-C",
        str(workdir),
        "-c",
        f'model_reasoning_effort="{args.effort}"',
        "-",
    ]

    log_handle = None
    if args.log:
        log_path = Path(args.log).expanduser().resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_handle = log_path.open("w", encoding="utf-8", newline="")

    expected_workdir = norm(workdir)
    saw_workdir = False
    saw_effort = False
    mismatch = None

    try:
        proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            cwd=str(workdir),
        )
        assert proc.stdin is not None and proc.stdout is not None
        proc.stdin.write(prompt)
        if not prompt.endswith("\n"):
            proc.stdin.write("\n")
        proc.stdin.close()

        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            if log_handle:
                log_handle.write(line)
                log_handle.flush()

            stripped = line.strip()
            if stripped.lower().startswith("workdir:"):
                reported = stripped.split(":", 1)[1].strip()
                saw_workdir = True
                if norm(reported) != expected_workdir:
                    mismatch = f"workdir mismatch: expected {workdir}, got {reported}"
                    proc.terminate()
                    break
            elif stripped.lower().startswith("reasoning effort:"):
                reported_effort = stripped.split(":", 1)[1].strip().lower()
                saw_effort = True
                if reported_effort != args.effort.lower():
                    mismatch = f"reasoning effort mismatch: expected {args.effort}, got {reported_effort}"
                    proc.terminate()
                    break

        return_code = proc.wait()
    finally:
        if log_handle:
            log_handle.close()

    if mismatch:
        print(f"CODEX_REASONING_CONFIGURATION_MISMATCH: {mismatch}", file=sys.stderr)
        return 42
    if not saw_workdir or not saw_effort:
        missing = []
        if not saw_workdir:
            missing.append("workdir")
        if not saw_effort:
            missing.append("reasoning effort")
        print(f"ERROR: Codex startup header missing required field(s): {', '.join(missing)}", file=sys.stderr)
        return 43

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
