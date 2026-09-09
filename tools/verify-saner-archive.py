#!/usr/bin/env python3
"""Extract a completed campaign archive afresh and recheck its evidence offline."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    provenance = json.loads((run / "provenance.json").read_text())
    assert provenance["status"] == "COMPLETE" and (run / "COMPLETE").exists()
    archive = run / "work.tar.gz"
    expected = json.loads((run / "ARCHIVE.json").read_text())
    digest = hashlib.sha256()
    with archive.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    assert digest.hexdigest() == expected["sha256"], "archive checksum mismatch"
    output = run / "archive-verification"
    output.mkdir(exist_ok=False)
    report = {"started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "archive_sha256": digest.hexdigest(), "stages": [],
              "scope": "Fresh extraction and offline re-verification of retained evidence; not fresh experiment execution or independent scientific replication."}
    with tempfile.TemporaryDirectory(prefix="saner-archive-verify-") as temp:
        subprocess.run(["tar", "-xzf", str(archive), "-C", temp], check=True)
        work = Path(temp) / "work"
        lock = provenance["release_lock"]
        base = ["docker", "run", "--rm", "--network", "none", "--cpus", "2", "--memory", "4g",
                "-v", str(work) + ":/results", "-v", str(work / "harness") + ":/exp:ro",
                lock["runner_image"], "python3"]
        stages = [("core", ["/results/verify-core.py", "/results/core", lock["dispat_version"]]),
                  ("recovery", ["/results/verify-recovery.py"])]
        for name in ("mixed-docker", "mixed-4node"):
            paths = list((work / name).glob("run-*/results.json"))
            assert len(paths) == 1
            stages.append((name, ["/results/" + name + "/verify.py",
                                  "/results/" + name + "/" + paths[0].parent.name]))
        for name, command in stages:
            result = subprocess.run(base + command, capture_output=True, text=True)
            (output / (name + ".log")).write_text(result.stdout + result.stderr)
            report["stages"].append({"name": name, "argv": base + command, "exit_code": result.returncode})
            report["status"] = "RUNNING" if result.returncode == 0 else "FAIL"
            (output / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
            result.check_returncode()
    report["status"] = "PASS"
    report["completed_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (output / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "stages": len(report["stages"]),
                      "archive_sha256": report["archive_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
