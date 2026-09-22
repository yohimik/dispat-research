#!/usr/bin/env python3
"""Check a retained checksum manifest against the files it describes.

Usage:
  python3 experiments/tools/check-manifest.py MANIFEST --root DIR
      [--strip-prefix OLD] [--output FILE] [--ignore PATH ...]

Manifest forms understood:
  * JSON object {relative_path: sha256} (campaign SHA256SUMS.json, FREEZE.json
    "files" maps, mechanism manifests with {path: {"sha256": ...}}).
  * sha256sum text lines "HASH  PATH". Paths that start with --strip-prefix
    have that prefix removed and are then resolved under --root, so manifests
    written with a historical absolute path can be checked after relocation.

The manifest and the files are only read. The optional --output report is
created exclusively (never overwritten). Exit status is 0 when every listed
file exists and matches, 1 otherwise.
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import sys


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def entries(manifest_path, strip_prefix):
    text = manifest_path.read_text()
    if text.lstrip().startswith("{"):
        data = json.loads(text)
        files = data.get("files", data) if isinstance(data, dict) else data
        for rel, value in files.items():
            digest = value["sha256"] if isinstance(value, dict) else value
            yield rel, digest
        return
    for line in text.splitlines():
        if not line.strip():
            continue
        digest, _, path = line.partition(" ")
        path = path.lstrip(" *")
        if strip_prefix and path.startswith(strip_prefix):
            path = path[len(strip_prefix):].lstrip("/")
        yield path, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("manifest", type=pathlib.Path)
    parser.add_argument("--root", type=pathlib.Path, required=True)
    parser.add_argument("--strip-prefix", default=None)
    parser.add_argument("--output", type=pathlib.Path, default=None)
    parser.add_argument("--ignore", nargs="*", default=[],
                        help="manifest paths to skip (for example the manifest itself)")
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = args.manifest.resolve()
    if args.output and args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    checked = ok = 0
    mismatched, missing = [], []
    skipped = set(args.ignore)
    for rel, digest in entries(manifest, args.strip_prefix):
        if rel in skipped:
            continue
        checked += 1
        path = root / rel
        if not path.is_file():
            missing.append(rel)
            continue
        if sha256(path) == digest:
            ok += 1
        else:
            mismatched.append(rel)
    report = {"manifest": str(manifest), "root": str(root),
              "checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "checked": checked, "ok": ok, "mismatched": mismatched,
              "missing": missing,
              "status": "PASS" if not mismatched and not missing else "FAIL"}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    summary = dict(report)
    summary["mismatched"] = mismatched[:20]
    summary["missing"] = missing[:20]
    print(json.dumps(summary, indent=2))
    sys.exit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
