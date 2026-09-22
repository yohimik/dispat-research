#!/usr/bin/env python3
"""Restore one E3a replay repository from its lock into a chosen directory.

Usage:
  python3 experiments/tools/restore-one-replay-fixture.py LOCK_NAME DEST

LOCK_NAME is a file stem under experiments/fixture-locks (babel,
conventional-changelog, google-cloud-node). DEST must not exist. The steps
are those of tools/restore-replay-fixtures.py (clone without checkout or tags,
fetch the locked tag objects and head by object ID, set the refs, detach at
the head, assert every ref) applied to a single lock and a caller-chosen
directory, so one fixture can be restored for a small replay without
restoring all three into experiments/e3a/repos.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def git(*args):
    return subprocess.check_output(["git", *map(str, args)], text=True).strip()


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    name, dest = sys.argv[1], pathlib.Path(sys.argv[2]).resolve()
    lock = ROOT / "experiments" / "fixture-locks" / (name + ".json")
    if not lock.is_file():
        raise SystemExit(f"no lock {lock}")
    if dest.exists():
        raise SystemExit(f"Refusing to overwrite {dest}")
    spec = json.loads(lock.read_text())
    if spec["status"].strip():
        raise SystemExit(f"{lock}: dirty original needs a separately reviewed restoration.")
    dest.parent.mkdir(parents=True, exist_ok=True)
    git("clone", "--no-checkout", "--no-tags", spec["origin"].strip(), dest)
    refs = [line.split() for line in spec["tags"].splitlines() if line.strip()]
    for offset in range(0, len(refs), 100):
        git("-C", dest, "fetch", "--no-tags", "origin", *[oid for oid, _ in refs[offset:offset + 100]])
    for oid, ref in refs:
        git("-C", dest, "update-ref", ref, oid)
    head = spec["head"].strip()
    git("-C", dest, "fetch", "--no-tags", "origin", head)
    git("-C", dest, "checkout", "--detach", head)
    assert git("-C", dest, "rev-parse", "HEAD") == head
    for oid, ref in refs:
        assert git("-C", dest, "rev-parse", ref) == oid, ref
    print(f"Restored {name} at {head} with {len(refs)} locked tags into {dest}.")


if __name__ == "__main__":
    main()
