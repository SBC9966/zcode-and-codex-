#!/usr/bin/env python3
"""Read only new bytes from a persistent Codex log for wait/poll executors.

This is an observation helper, not a scheduler or source of truth. The returned
next_offset can be passed to the next poll. Process state, persistent log, and
Git state remain authoritative for recovery decisions.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def run_git(workdir: Path, *args: str) -> tuple[int, str]:
    p = subprocess.run(
        ["git", *args],
        cwd=str(workdir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return p.returncode, p.stdout.strip()


def git_snapshot(workdir: Path) -> dict[str, object]:
    result: dict[str, object] = {"workdir": str(workdir)}
    code, head = run_git(workdir, "rev-parse", "HEAD")
    if code != 0:
        result["git_error"] = head or "git rev-parse failed"
        return result
    result["git_head"] = head

    code, status = run_git(workdir, "status", "--porcelain")
    if code != 0:
        result["git_status_error"] = status or "git status failed"
        return result
    lines = status.splitlines()
    result["git_clean"] = not bool(lines)
    result["git_status_lines"] = lines
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--workdir", default=None)
    args = parser.parse_args()

    if args.offset < 0:
        print(json.dumps({"error": "offset_must_be_non_negative"}, indent=2))
        return 2

    log_path = Path(args.log).expanduser().resolve()
    result: dict[str, object] = {
        "mode": "INCREMENTAL_LOG_STREAM",
        "log_path": str(log_path),
        "requested_offset": args.offset,
        "log_exists": log_path.is_file(),
    }

    if not log_path.is_file():
        result.update(
            {
                "previous_offset": args.offset,
                "next_offset": args.offset,
                "bytes_read": 0,
                "log_size": 0,
                "log_grew": False,
                "new_output": "",
            }
        )
        if args.workdir:
            result.update(git_snapshot(Path(args.workdir).expanduser().resolve()))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    stat = log_path.stat()
    size = stat.st_size
    previous = args.offset
    reset = False
    if previous > size:
        previous = 0
        reset = True

    with log_path.open("rb") as handle:
        handle.seek(previous)
        data = handle.read()
        next_offset = handle.tell()

    result.update(
        {
            "previous_offset": previous,
            "next_offset": next_offset,
            "bytes_read": len(data),
            "log_size": size,
            "log_mtime": stat.st_mtime,
            "log_grew": len(data) > 0,
            "offset_reset_after_truncation": reset,
            "new_output": data.decode("utf-8", errors="replace"),
        }
    )

    if args.workdir:
        result.update(git_snapshot(Path(args.workdir).expanduser().resolve()))

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
