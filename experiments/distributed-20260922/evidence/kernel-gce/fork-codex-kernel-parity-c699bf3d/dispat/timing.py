#!/usr/bin/env python3
"""Measure coordinator/worker overhead from dispat JSON logs.

The log timestamps are wall-clock observations (often only precise to one second).
The ``took`` field on ``git`` events is milliseconds and is converted here.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _seconds(start: dict[str, Any] | None, end: dict[str, Any] | None) -> float | None:
    if not start or not end:
        return None
    return (_timestamp(end["time"]) - _timestamp(start["time"])).total_seconds()


def read_json_lines(paths: Iterable[Path]) -> tuple[list[dict[str, Any]], int]:
    events: list[dict[str, Any]] = []
    ignored = 0
    for path in paths:
        with path.open(errors="replace") as stream:
            for line in stream:
                try:
                    event = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    ignored += 1
                    continue
                if isinstance(event, dict) and isinstance(event.get("time"), str):
                    events.append(event)
                else:
                    ignored += 1
    events.sort(key=lambda event: _timestamp(event["time"]))
    return events, ignored


def _first(events: Iterable[dict[str, Any]], *, message: str, role: str | None = None,
           task: str | None = None) -> dict[str, Any] | None:
    return next((event for event in events
                 if event.get("message") == message
                 and (role is None or event.get("role") == role)
                 and (task is None or event.get("task") == task)), None)


def _last(events: Iterable[dict[str, Any]], *, message: str, role: str | None = None,
          task: str | None = None) -> dict[str, Any] | None:
    return next((event for event in reversed(list(events))
                 if event.get("message") == message
                 and (role is None or event.get("role") == role)
                 and (task is None or event.get("task") == task)), None)


def read_results(paths: Iterable[Path]) -> dict[str, dict[str, Any]]:
    """Read one phase's evidence, rejecting cells that are not unique.

    result.json has no run identifier or timestamp.  Consequently there is no
    sound way to select among repeated cells from a combined experiment tree.
    Callers must pass an isolated phase directory (or explicit result files).
    """
    found: dict[str, dict[str, Any]] = {}
    sources: dict[str, Path] = {}
    files: list[Path] = []
    for path in paths:
        files.extend(path.rglob("result.json") if path.is_dir() else [path])
    for path in files:
        try:
            result = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        cell = result.get("cell")
        if isinstance(cell, str):
            if cell in found:
                raise ValueError(
                    f"ambiguous result for cell {cell!r}: {sources[cell]} and {path}; "
                    "pass an isolated per-phase result directory"
                )
            found[cell] = result
            sources[cell] = path
    return found


def analyze(coordinator: list[dict[str, Any]], worker: list[dict[str, Any]],
            results: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    results = results or {}
    release_start = _first(coordinator, message="release started", role="orchestrator")
    kernel_done = _first(coordinator, message="task finished", role="orchestrator",
                         task="kernel:build")
    input_pushed = _first(coordinator, message="input state pushed", role="orchestrator")

    assigned = [e for e in coordinator
                if e.get("role") == "orchestrator" and e.get("message") == "task assigned"]
    task_counts: dict[str, int] = defaultdict(int)
    for event in assigned:
        task_counts[event["task"]] += 1

    def belongs_to_assignment(event: dict[str, Any], assignment: dict[str, Any]) -> bool:
        """Match the identity fields emitted on both sides of an assignment."""
        for key in ("run", "task", "branch", "attempt"):
            if assignment.get(key) is not None and event.get(key) != assignment.get(key):
                return False
        worker_name = assignment.get("worker")
        return worker_name is None or event.get("node") == worker_name

    def coordinator_receipt(assignment: dict[str, Any]) -> dict[str, Any] | None:
        # Receipts omit branch/attempt, but retain run/task/worker. Take the
        # first matching receipt after this particular assignment.
        assigned_at = _timestamp(assignment["time"])
        return next((event for event in coordinator
                     if event.get("role") == "orchestrator"
                     and event.get("message") == "task finished"
                     and event.get("run") == assignment.get("run")
                     and event.get("task") == assignment.get("task")
                     and event.get("worker") == assignment.get("worker")
                     and _timestamp(event["time"]) >= assigned_at), None)

    jobs: list[dict[str, Any]] = []
    previous_received_by_worker: dict[str, dict[str, Any]] = {}
    for assignment in assigned:
        task = assignment["task"]
        events = [event for event in worker if belongs_to_assignment(event, assignment)]
        claim = _first(events, message="task claimed", role="worker", task=task)
        worktree = _first(events, message="worktree added", role="worker", task=task)
        stage = _first(events, message="stage started", role="worker", task=task)
        completed = _last(events, message="task finished", role="worker", task=task)
        received = coordinator_receipt(assignment)
        package = task.removesuffix(":build")
        # Current harnesses write cells such as ``build-hexagon``; accepting the
        # bare architecture also makes older downloaded evidence usable.
        result = (results.get(package, results.get(package.removeprefix("build-"), {}))
                  if task_counts[task] == 1 else {})
        timings = result.get("timings", {}) if isinstance(result.get("timings", {}), dict) else {}
        kernel_timings = {key: float(timings[key]) for key in
                          ("cache_lock_seconds", "kernel_fetch_seconds",
                           "kernel_checkout_seconds")
                          if isinstance(timings.get(key), (int, float))}
        checkout = sum(kernel_timings.values())
        total = result.get("seconds")
        build_script = result.get("script_seconds")
        wrapper_other = None
        if isinstance(total, (int, float)) and isinstance(build_script, (int, float)):
            wrapper_other = max(0.0, float(total) - float(build_script) - checkout)
        worker_name = assignment.get("worker") or (claim or {}).get("node")
        jobs.append({
            "task": task,
            "node": claim.get("node") if claim else None,
            "assigned_at": assignment["time"],
            "assignment_to_claim_seconds": _seconds(assignment, claim),
            "farm_checkout_seconds": _seconds(claim, worktree),
            **{key: kernel_timings.get(key) for key in
               ("cache_lock_seconds", "kernel_fetch_seconds", "kernel_checkout_seconds")},
            "wrapper_other_seconds": wrapper_other,
            "build_script_seconds": (float(build_script)
                                     if isinstance(build_script, (int, float)) else None),
            "worker_completion_to_coordinator_result_seconds": _seconds(completed, received),
            "queue_gap_after_previous_result_seconds": _seconds(
                previous_received_by_worker.get(worker_name), assignment),
            "worker_elapsed_seconds": _seconds(claim, completed),
            "status": (completed or received or {}).get("status"),
            "result_evidence": ("ambiguous-repeated-task" if task_counts[task] > 1
                                else "found" if result else "missing"),
        })
        if received and worker_name:
            previous_received_by_worker[worker_name] = received

    terminal_messages = {"release finished", "release completed", "release succeeded", "done"}
    terminal = next((event for event in reversed(coordinator)
                     if event.get("role") == "orchestrator"
                     and event.get("message") in terminal_messages), None)
    receipts = [coordinator_receipt(e) for e in assigned]
    # A truncated log must remain partial even if it happens to contain a
    # terminal-looking event from earlier material, or misses one task receipt.
    complete = (terminal is not None and all(receipts)
                and (not receipts or _timestamp(terminal["time"]) >=
                     max(_timestamp(e["time"]) for e in receipts if e)))
    if terminal is None and assigned:
        terminal = next((e for e in reversed(receipts) if e), None)

    git_ms = [float(e["took"]) for e in coordinator + worker
              if e.get("message") == "git" and isinstance(e.get("took"), (int, float))]
    source_push_git_ms = None
    if input_pushed:
        candidates = [e for e in coordinator
                      if e.get("message") == "git" and e.get("time") == input_pushed["time"]
                      and isinstance(e.get("took"), (int, float))
                      and e.get("args", [None])[0] == "push"]
        if candidates:
            source_push_git_ms = max(float(e["took"]) for e in candidates)
    return {
        "initial_source_push_seconds": _seconds(kernel_done, input_pushed),
        "initial_source_push_git_seconds": (source_push_git_ms / 1000.0
                                             if source_push_git_ms is not None else None),
        "jobs": jobs,
        "full_run_wall_seconds": _seconds(release_start, terminal),
        "full_run_complete": complete,
        "observed_git_seconds": sum(git_ms) / 1000.0,
    }


def _format(value: float | None) -> str:
    return "-" if value is None else f"{value:.3f}"


def text_report(report: dict[str, Any]) -> str:
    lines = [
        f"initial source push: {_format(report['initial_source_push_seconds'])} s",
        f"initial source push git: {_format(report['initial_source_push_git_seconds'])} s",
        "task\tassign->claim\tfarm checkout\twrapper other\tbuild script\tfinish->result\tqueue gap",
    ]
    for job in report["jobs"]:
        lines.append("\t".join((
            job["task"], _format(job["assignment_to_claim_seconds"]),
            _format(job["farm_checkout_seconds"]), _format(job["wrapper_other_seconds"]),
            _format(job["build_script_seconds"]),
            _format(job["worker_completion_to_coordinator_result_seconds"]),
            _format(job["queue_gap_after_previous_result_seconds"]),
        )))
    qualifier = "" if report["full_run_complete"] else " (partial; last received result)"
    lines.append(f"full run wall: {_format(report['full_run_wall_seconds'])} s{qualifier}")
    lines.append(f"observed git subprocess time: {_format(report['observed_git_seconds'])} s")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("coordinator", type=Path, help="coordinator JSON-lines log")
    parser.add_argument("worker", type=Path, nargs="+", help="one or more worker JSON-lines logs")
    parser.add_argument("--result", type=Path, action="append", default=[],
                        help="result.json or directory to search (repeatable)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    coordinator, coordinator_ignored = read_json_lines([args.coordinator])
    worker, worker_ignored = read_json_lines(args.worker)
    try:
        results = read_results(args.result)
    except ValueError as error:
        parser.error(str(error))
    report = analyze(coordinator, worker, results)
    report["ignored_log_lines"] = coordinator_ignored + worker_ignored
    print(json.dumps(report, indent=2) if args.json else text_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
