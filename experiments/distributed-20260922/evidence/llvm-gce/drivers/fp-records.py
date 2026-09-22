#!/usr/bin/env python3
"""Print the fingerprint records of an install tree, one per line, the way
build.py's fingerprint sees them (name, executable bit, kind, digest or
target), so two trees can be diffed record by record.

    fp-records.py <install tree>
"""
import hashlib
import os
import stat
import sys
from pathlib import Path


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


tree = Path(sys.argv[1])
for path in sorted(tree.rglob("*")):
    info = path.lstat()
    name = path.relative_to(tree).as_posix()
    is_executable = bool(stat.S_IMODE(info.st_mode) & 0o111)
    if path.is_symlink():
        print(name, "link", os.readlink(path))
    elif path.is_file():
        print(name, "x" if is_executable else "-", "file", digest(path))
    elif path.is_dir():
        print(name, "directory", "empty" if not any(path.iterdir()) else "")
