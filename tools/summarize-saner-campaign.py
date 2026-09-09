#!/usr/bin/env python3
"""Reaggregate a completed 14-stage SANER campaign; print JSON, change no inputs."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


def read(path):
    return json.loads(path.read_text())


def summarize(run, work):
    provenance = read(run / "provenance.json")
    assert provenance["status"] == "COMPLETE" and (run / "COMPLETE").is_file()
    assert len(provenance["stages"]) == 14
    assert all(s["status"] == "PASS" for s in provenance["stages"])
    core = read(work / "core/verification.json")
    assert core["status"] == "INTEGRITY_PASS"
    recovery = read(work / "recovery/verification.json")
    assert recovery["status"] == "PASS"
    episodes = read(work / "recovery/results.json")
    recovery["run_distribution"] = dict(sorted(Counter(r["runs"] for r in episodes).items()))
    recovery["invariant_errors"] = sum(len(r["invariant_errors"]) for r in episodes)
    recovery["converged"] = sum(r["converged"] for r in episodes)
    recovery["source"] = "work/recovery/results.json"
    mixed = {}
    for name in ("mixed-docker", "mixed-4node"):
        paths = list((work / name).glob("run-*/results.json"))
        assert len(paths) == 1
        path = paths[0]
        rows = read(path)
        checks = read(path.parent / "verification.json")
        assert checks["status"] == "PASS"
        mixed[name] = {
            "source": "work/" + str(path.relative_to(work)),
            "executions": len(rows),
            "case_counts": dict(Counter(r["case"] for r in rows)),
            "initial_successes": sum(r["exit"] == 0 for r in rows),
            "initial_failures": sum(r["exit"] != 0 for r in rows),
            "repair_executions": sum(len(r["retries"]) for r in rows),
            "successful_repairs": sum(code == 0 for r in rows for code in r["retries"]),
            "unchanged_executions": sum(r["final_exit"] is not None for r in rows),
            "successful_unchanged": sum(r["final_exit"] == 0 for r in rows),
            "checks": checks["checks_executed"],
            "overlap": checks.get("overlap", []),
        }
    integration = read(work / "integration/results/verification.json")
    assert integration["status"] == "PASS"
    return {
        "run": run.name, "status": provenance["status"],
        "started_utc": provenance["started_utc"], "completed_utc": provenance["completed_utc"],
        "release_lock": provenance["release_lock"],
        "protocol_manifest_sha256": provenance["protocol_manifest_sha256"],
        "provenance_sha256": hashlib.sha256((run / "provenance.json").read_bytes()).hexdigest(),
        "core": core, "recovery": recovery, "mixed": mixed,
        "integration": {k: v for k, v in integration.items() if k != "checks"},
        "counting_boundary": "Histories, recovery episodes, topology executions, CI repetitions and repeated predicates remain separate units. No pooled success rate.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    if (run / "work").is_dir():
        result = summarize(run, run / "work")
    else:
        archive = run / "work.tar.gz"
        expected = read(run / "ARCHIVE.json")["sha256"]
        if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
            raise SystemExit("Archive checksum mismatch")
        with tempfile.TemporaryDirectory(prefix="saner-summary-") as temp:
            subprocess.run(["tar", "-xzf", str(archive), "-C", temp], check=True)
            result = summarize(run, Path(temp) / "work")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
