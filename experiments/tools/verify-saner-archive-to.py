#!/usr/bin/env python3
"""Relocatable form of tools/verify-saner-archive.py.

Usage:
  python3 experiments/tools/verify-saner-archive-to.py RUN OUTPUT_DIR
      [--runner-image IMAGE]

RUN is a completed 14-stage campaign run directory (provenance.json, COMPLETE,
ARCHIVE.json, work.tar.gz). The archive checksum is compared with
ARCHIVE.json, the archive is extracted into a temporary directory, and the
four retained-data verifiers (core, recovery, mixed-docker, mixed-4node) run
in Docker with networking disabled, exactly as tools/verify-saner-archive.py
runs them. The difference is only where the report goes: OUTPUT_DIR (created
exclusively) instead of RUN/archive-verification, so a run that already
carries its original verification can be rechecked without touching it.

--runner-image defaults to the run's locked runner image ID. Passing another
image (for example a digest-pinned rebuild) is recorded in the report and
makes the check a RECIPE-level recheck, not the exact retained environment.
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    parser.add_argument("--runner-image", default=None)
    args = parser.parse_args()
    run = args.run.resolve()
    output = args.output.resolve()
    provenance = json.loads((run / "provenance.json").read_text())
    if provenance["status"] != "COMPLETE" or not (run / "COMPLETE").exists():
        raise SystemExit("run is not COMPLETE; the retained-data verifiers only apply to a completed run")
    archive = run / "work.tar.gz"
    expected = json.loads((run / "ARCHIVE.json").read_text())
    digest = hashlib.sha256()
    with archive.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != expected["sha256"]:
        raise SystemExit("archive checksum mismatch")
    output.mkdir(parents=True, exist_ok=False)
    lock = provenance["release_lock"]
    image = args.runner_image or lock["runner_image"]
    report = {"started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "run": str(run), "archive_sha256": digest.hexdigest(),
              "runner_image": image,
              "runner_image_is_locked": image == lock["runner_image"],
              "stages": [],
              "scope": "Fresh extraction and offline re-verification of retained evidence into a separate output directory; not fresh experiment execution or independent scientific replication."}
    with tempfile.TemporaryDirectory(prefix="saner-archive-verify-") as temp:
        subprocess.run(["tar", "-xzf", str(archive), "-C", temp], check=True)
        work = pathlib.Path(temp) / "work"
        base = ["docker", "run", "--rm", "--network", "none", "--cpus", "2", "--memory", "4g",
                "-v", str(work) + ":/results", "-v", str(work / "harness") + ":/exp:ro",
                image, "python3"]
        stages = [("core", ["/results/verify-core.py", "/results/core", lock["dispat_version"]]),
                  ("recovery", ["/results/verify-recovery.py"])]
        for name in ("mixed-docker", "mixed-4node"):
            paths = list((work / name).glob("run-*/results.json"))
            if len(paths) != 1:
                raise SystemExit(f"expected exactly one {name} run in the archive")
            stages.append((name, ["/results/" + name + "/verify.py",
                                  "/results/" + name + "/" + paths[0].parent.name]))
        status = "PASS"
        for name, command in stages:
            result = subprocess.run(base + command, capture_output=True, text=True)
            (output / (name + ".log")).write_text(result.stdout + result.stderr)
            report["stages"].append({"name": name, "argv": base + command,
                                     "exit_code": result.returncode})
            if result.returncode != 0:
                status = "FAIL"
            (output / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    report["status"] = status
    report["completed_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (output / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": status, "stages": [(s["name"], s["exit_code"]) for s in report["stages"]],
                      "archive_sha256": report["archive_sha256"], "runner_image": image}, indent=2))
    sys.exit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()
