#!/usr/bin/env python3
"""Archive a finished campaign without changing its raw observations.

Usage: python3 tools/archive-campaign.py PATH/TO/RUN
Includes hidden files and nested Git metadata; verifies every regular file.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile


def digest(stream):
    result = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        result.update(block)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    provenance = json.loads((run / "provenance.json").read_text())
    if provenance["status"] not in ("COMPLETE", "FAILED"):
        raise SystemExit("Refusing to archive a running campaign")
    if (run / "ARCHIVE.json").exists() or (run / "work.tar.gz").exists():
        raise SystemExit("Refusing to overwrite an existing archive")
    work = run / "work"
    archive = run / "work.tar.gz"
    with tarfile.open(archive, "x:gz") as output:
        output.add(work, arcname="work")
    observed = set()
    with tarfile.open(archive, "r:gz") as saved:
        for member in saved:
            if not (member.isfile() or member.islnk()):
                continue
            relative = Path(member.name).relative_to("work")
            observed.add(relative)
            with saved.extractfile(member) as archived, (work / relative).open("rb") as live:
                if digest(archived) != digest(live):
                    raise SystemExit(f"Archive mismatch: {relative}")
    expected = {p.relative_to(work) for p in work.rglob("*")
                if p.is_file() and not p.is_symlink()}
    if observed != expected:
        raise SystemExit("Archive file inventory mismatch")
    with archive.open("rb") as stream:
        checksum = digest(stream)
    result = {
        "archive": archive.name, "sha256": checksum,
        "bytes": archive.stat().st_size, "files_verified": len(observed),
        "status": provenance["status"],
        "contents": "Complete work directory, including nested Git metadata and raw outcomes. Local work retained unchanged.",
    }
    with (run / "ARCHIVE.json").open("x") as output:
        output.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
