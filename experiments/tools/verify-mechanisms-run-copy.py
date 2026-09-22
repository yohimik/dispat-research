#!/usr/bin/env python3
"""Recheck a mechanism-campaign run from its archive without touching it.

Usage:
  python3 experiments/tools/verify-mechanisms-run-copy.py RUN OUTPUT_DIR
      [--runner-image IMAGE]

RUN is a run directory of experiments/saner-2027/campaign-mechanisms-20260910
(for example runs/full-01) whose expanded fixture trees were replaced by
expanded-fixtures.tar.gz. The tool

  1. copies the run's retained files into OUTPUT_DIR/run (OUTPUT_DIR is
     created exclusively; RUN is only read);
  2. checks the archive SHA-256 against archive-verification.json, extracts
     the archive into the copy, and checks every extracted regular file
     against that manifest's per-file SHA-256 and byte length;
  3. runs the campaign's own offline checker, verify.py, inside Docker with
     networking disabled, with the campaign directory mounted read-only, and
     writes its result to OUTPUT_DIR/verifier.json.

This is the "audit full-01 from its archive" procedure that the campaign
README describes, made into one command with explicit paths.
--runner-image defaults to the campaign's locked runner image ID.
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tarfile


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    parser.add_argument("--runner-image", default=None)
    args = parser.parse_args()
    run = args.run.resolve()
    campaign = run.parent.parent
    if not (campaign / "verify.py").is_file() or not (campaign / "release-lock.json").is_file():
        raise SystemExit("RUN must be a run directory under the mechanism campaign (campaign/runs/NAME)")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    copy = output / "run"
    shutil.copytree(run, copy, symlinks=True)
    manifest = json.loads((copy / "archive-verification.json").read_text())
    archive = copy / manifest["archive"]
    report = {"started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "source_run": str(run), "copy": str(copy)}
    observed = sha256(archive)
    report["archive_sha256_expected"] = manifest["archive_sha256"]
    report["archive_sha256_observed"] = observed
    if observed != manifest["archive_sha256"]:
        report["status"] = "FAIL"
        report["error"] = "archive checksum mismatch"
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        raise SystemExit("archive checksum mismatch")
    with tarfile.open(archive, "r:gz") as stream:
        stream.extractall(copy)
    mismatched, missing = [], []
    for rel, value in manifest["files"].items():
        path = copy / rel
        if not path.is_file():
            missing.append(rel)
        elif path.stat().st_size != value["bytes"] or sha256(path) != value["sha256"]:
            mismatched.append(rel)
    report["extracted_files_checked"] = len(manifest["files"])
    report["extracted_mismatched"] = mismatched
    report["extracted_missing"] = missing
    lock = json.loads((campaign / "release-lock.json").read_text())
    image = args.runner_image or lock["runner_image"]
    report["runner_image"] = image
    report["runner_image_is_locked"] = image == lock["runner_image"]
    command = ["docker", "run", "--rm", "--network", "none", "--cpus", "2", "--memory", "4g",
               "--platform", "linux/arm64",
               "-v", str(campaign) + ":/campaign:ro", "-v", str(output) + ":/replay",
               "-w", "/campaign", image,
               "python3", "verify.py", "/replay/run", "/replay/verifier.json"]
    report["verifier_argv"] = command
    result = subprocess.run(command, capture_output=True, text=True)
    (output / "verifier.log").write_text(result.stdout + result.stderr)
    report["verifier_exit"] = result.returncode
    report["status"] = ("PASS" if result.returncode == 0 and not mismatched and not missing
                        else "FAIL")
    report["completed_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    report["scope"] = "Offline consistency recheck of retained evidence from a fresh archive extraction; not a fresh execution."
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("status", "verifier_exit", "extracted_files_checked",
                                              "runner_image", "runner_image_is_locked")}, indent=2))
    sys.exit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
