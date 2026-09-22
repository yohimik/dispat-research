#!/usr/bin/env python3
"""Compare the products of two runs of the same recipe: the local baseline and
the distributed run.

    compare.py <baseline checkout> <distributed checkout>

For each package the install trees are compared file by file: the same set of
paths, the same modes, the same symlink targets, and the same content once the
install prefix is masked. The prefix is masked because build.py installs into
`<package>/_dispat/install` of whatever checkout runs it, and llvm-config, the
CMake package files and a few scripts embed that absolute path; two builds that
differ only there are the same build. Files that still differ are listed with
their sizes, so a real difference is never hidden behind the mask. The
toolchain archive is compared by its member list and sizes, and the receipts'
own fingerprints are printed beside the masked comparison.
"""
import hashlib
import json
import os
import stat
import sys
import tarfile
from pathlib import Path

PACKAGES = {"llvm": "llvm", "llvm-aarch64": ".ci/dispat/llvm-aarch64", "lld": "lld", "polly": "polly",
            "toolchain": ".ci/dispat/bundle"}


def masked_digest(path, prefix):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        data = stream.read()
    h.update(data.replace(prefix.encode(), b"@PREFIX@"))
    return h.hexdigest()


def describe(tree, prefix):
    # Only the executable bit of a file is part of the artifact, as in
    # build.py's fingerprint: the rest of a mode is the creating process's
    # umask, and directories carry no mode at all.
    records = {}
    for path in sorted(tree.rglob("*")):
        name = path.relative_to(tree).as_posix()
        info = path.lstat()
        mode = 0o755 if stat.S_IMODE(info.st_mode) & 0o111 else 0o644
        if path.is_symlink():
            records[name] = ("link", 0, os.readlink(path), 0)
        elif path.is_file():
            records[name] = ("file", mode, masked_digest(path, prefix), info.st_size)
        # Directories are not recorded: a file implies its parents, and an
        # empty directory is not part of what a consumer can read.
    return records


def compare_trees(package, left, right):
    a = describe(left, str(left))
    b = describe(right, str(right))
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    differing = [n for n in sorted(set(a) & set(b)) if a[n] != b[n]]
    print("%-10s %6d entries baseline, %6d distributed, %d only in baseline, %d only in distributed, %d differ" % (
        package, len(a), len(b), len(only_a), len(only_b), len(differing)))
    for n in only_a[:10]:
        print("   only baseline:    ", n)
    for n in only_b[:10]:
        print("   only distributed: ", n)
    for n in differing[:20]:
        print("   differs: %s  (%s %o %d bytes) vs (%s %o %d bytes)" % (
            n, a[n][0], a[n][1], a[n][3], b[n][0], b[n][1], b[n][3]))
    return not only_a and not only_b and not differing


def compare_archives(left, right):
    def members(folder):
        archives = list((folder / "dist").glob("*.tar*"))
        if len(archives) != 1:
            return None, {}
        with tarfile.open(archives[0]) as stream:
            return archives[0].name, {m.name.split("/", 1)[-1]: (m.size, m.mode, m.type) for m in stream}
    name_a, a = members(left)
    name_b, b = members(right)
    same = a == b and a
    print("toolchain archive: %s vs %s, %d members, %s" % (name_a, name_b, len(a), "same list, sizes and modes" if same else "DIFFERENT"))
    for n in sorted(set(a) ^ set(b))[:10]:
        print("   only one side:", n)
    for n in sorted(set(a) & set(b)):
        if a[n] != b[n]:
            print("   differs:", n, a[n], b[n])
    return bool(same)


def receipts(folder):
    path = folder / "build-info.json"
    if not path.is_file():
        return {}
    receipt = json.loads(path.read_text())
    return {"installSha256": receipt.get("installSha256"), "source": receipt.get("identity", {}).get("source"),
            "version": receipt.get("identity", {}).get("version")}


def main():
    baseline, distributed = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    ok = True
    for package, folder in PACKAGES.items():
        left = baseline / folder / "_dispat"
        right = distributed / folder / "_dispat"
        print("receipts %-10s baseline %s  distributed %s" % (package, receipts(left), receipts(right)))
        ok = compare_trees(package, left / "install", right / "install") and ok
    ok = compare_archives(baseline / PACKAGES["toolchain"] / "_dispat",
                          distributed / PACKAGES["toolchain"] / "_dispat") and ok
    print("PARITY" if ok else "NO PARITY")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
