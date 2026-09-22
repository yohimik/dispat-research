#!/usr/bin/env python3
"""Run one reproduction step and record it.

Usage:
  python3 experiments/tools/repro-step.py --family DIR --name STEP [--cwd DIR]
      [--allow-exit CODES] -- COMMAND [ARG ...]

The command's combined stdout and stderr go to DIR/STEP.log (refused if the
log already exists) and one JSON line describing the step (UTC start and end,
argv, working directory, exit status, log path) is appended to DIR/steps.jsonl.
The wrapper's own exit status is the command's. Nothing outside DIR is written
by the wrapper itself.
"""
import argparse
import datetime
import json
import os
import pathlib
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--family", required=True, type=pathlib.Path,
                        help="directory that receives STEP.log and steps.jsonl")
    parser.add_argument("--name", required=True, help="step name, one path component")
    parser.add_argument("--cwd", type=pathlib.Path, default=None)
    parser.add_argument("--allow-exit", default="0",
                        help="comma-separated exit codes that count as expected")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise SystemExit("no command given")
    if "/" in args.name or args.name in ("", ".", ".."):
        raise SystemExit("step name must be one path component")
    family = args.family.resolve()
    family.mkdir(parents=True, exist_ok=True)
    log = family / (args.name + ".log")
    if log.exists():
        raise SystemExit(f"refusing to overwrite {log}")
    allowed = {int(x) for x in args.allow_exit.split(",") if x.strip()}
    started = datetime.datetime.now(datetime.timezone.utc)
    cwd = str(args.cwd.resolve()) if args.cwd else os.getcwd()
    with log.open("x") as stream:
        stream.write("# " + json.dumps({"argv": command, "cwd": cwd,
                                        "started_utc": started.isoformat()}) + "\n")
        stream.flush()
        try:
            result = subprocess.run(command, cwd=cwd, stdout=stream,
                                    stderr=subprocess.STDOUT)
            code = result.returncode
            error = None
        except OSError as exc:
            code = None
            error = f"{type(exc).__name__}: {exc}"
            stream.write(error + "\n")
    ended = datetime.datetime.now(datetime.timezone.utc)
    record = {"step": args.name, "started_utc": started.isoformat(),
              "ended_utc": ended.isoformat(),
              "elapsed_seconds": round((ended - started).total_seconds(), 3),
              "argv": command, "cwd": cwd, "exit": code,
              "expected": code in allowed,
              "log": str(log.relative_to(family))}
    if error:
        record["error"] = error
    with (family / "steps.jsonl").open("a") as ledger:
        ledger.write(json.dumps(record, sort_keys=True) + "\n")
    print(json.dumps({k: record[k] for k in ("step", "exit", "expected",
                                              "elapsed_seconds", "log")}))
    sys.exit(0 if code in allowed else (code if isinstance(code, int) and code else 1))


if __name__ == "__main__":
    main()
