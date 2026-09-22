#!/usr/bin/env python3
"""LLVM build recipes. Scheduling, transport and release authority belong to dispat."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = {"llvm": "llvm", "llvm-aarch64": ".ci/dispat/llvm-aarch64", "clang": "clang", "lld": "lld",
            "polly": "polly", "toolchain": ".ci/dispat/bundle"}
# A package built from another package's sources: the matrix fixture builds the
# llvm sources once per target, each as a package of its own with its own
# products folder.
SOURCES = {"llvm-aarch64": "llvm"}
# The toolchain bundles whatever LLVM_TOOLCHAIN_PROVIDERS names, so a fixture
# that leaves clang out still assembles a bundle from what it built.
PROVIDERS = {"llvm": (), "llvm-aarch64": (), "clang": ("llvm",), "lld": ("llvm",), "polly": ("llvm",),
             "toolchain": tuple(os.environ.get("LLVM_TOOLCHAIN_PROVIDERS", "llvm,clang,lld").split(","))}
SEMVER = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?")


def run(*args, capture=False):
    return subprocess.run([str(a) for a in args], cwd=ROOT, check=True,
                          text=True, stdout=subprocess.PIPE if capture else None).stdout


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def output(package):
    return ROOT / PACKAGES[package] / "_dispat"


def fingerprint(tree):
    """The digest of an install tree's fingerprint records."""
    return digest_records(fingerprint_records(tree))


def digest_records(records):
    data = json.dumps(records, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def fingerprint_records(tree):
    """Include the executable bit and symlink targets; refuse escaping links/devices.

    Only the executable bit of a file is part of the artifact: the rest of a
    mode is the umask of whatever process created the entry, and a tree that
    travelled between machines (dispat carries files as 0644 or 0755 and
    recreates directories) must fingerprint the same as the one that was built.
    Directories are not recorded at all for the same reason: a transport that
    carries files carries every directory a file needs and no empty one, and an
    empty directory is not something a consumer can read.
    """
    if not tree.is_dir() or tree.is_symlink():
        raise ValueError(f"missing install tree: {tree}")
    records = []
    for path in sorted(tree.rglob("*")):
        info = path.lstat()
        name = path.relative_to(tree).as_posix()
        is_executable = bool(stat.S_IMODE(info.st_mode) & 0o111)
        if path.is_symlink():
            target = os.readlink(path)
            if Path(target).is_absolute() or not path.resolve().is_relative_to(tree.resolve()):
                raise ValueError(f"nonrelocatable symlink: {path}")
            records.append((name, "link", target))
        elif path.is_file():
            records.append((name, is_executable, "file", digest(path)))
        elif path.is_dir():
            continue
        else:
            raise ValueError(f"unsupported installed file type: {path}")
    if not records:
        raise ValueError(f"empty install tree: {tree}")
    return records


def report_fingerprint_difference(package, tree, recorded):
    """Name the records that differ between a receipt and the tree it describes,
    so an integrity failure says what changed rather than that something did."""
    if not recorded:
        return
    then = {json.dumps(record, separators=(",", ":")) for record in recorded}
    now = {json.dumps(list(record), separators=(",", ":")) for record in fingerprint_records(tree)}
    for record in sorted(then - now):
        print(f"dispat LLVM: {package}: recorded but not present: {record}", file=sys.stderr)
    for record in sorted(now - then):
        print(f"dispat LLVM: {package}: present but not recorded: {record}", file=sys.stderr)


def identity(require_clean=True):
    version = os.environ.get("DISPAT_NEW_VERSION") or os.environ.get("LLVM_BUILD_VERSION", "")
    match = SEMVER.fullmatch(version)
    if not match:
        raise ValueError("set LLVM_BUILD_VERSION for local builds; releases use DISPAT_NEW_VERSION")
    cmake_version = (ROOT / "cmake/Modules/LLVMVersion.cmake").read_text()
    source_major = re.search(r"set\(LLVM_VERSION_MAJOR (\d+)\)", cmake_version).group(1)
    if match[1] != source_major:
        raise ValueError(f"release major {match[1]} does not match LLVM source major {source_major}")
    # A task on another machine builds from a snapshot of this tree rather
    # than from the commit itself, so the orchestrator names the commit.
    revision = os.environ.get("LLVM_BUILD_SOURCE") or run("git", "rev-parse", "HEAD", capture=True).strip()
    # Modified tracked source must never be labelled as the pristine commit.
    if require_clean and run("git", "status", "--porcelain", "--untracked-files=no", capture=True).strip():
        raise ValueError("commit tracked changes before producing source-labelled artifacts")
    machine = {"x86_64": "amd64", "aarch64": "arm64"}.get(platform.machine(), platform.machine())
    return {"source": revision, "version": version,
            "platform": f"{platform.system().lower()}/{machine}",
            "recipeSha256": digest(Path(__file__)),
            "targets": os.environ.get("LLVM_TARGETS_TO_BUILD", "X86"),
            "compiler": run(os.environ.get("CXX", "c++"), "--version", capture=True).strip(),
            "cCompiler": run(os.environ.get("CC", "cc"), "--version", capture=True).strip(),
            "cmake": run("cmake", "--version", capture=True).strip(),
            "ninja": run("ninja", "--version", capture=True).strip(),
            "libc": list(platform.libc_ver()),
            "environment": {key: os.environ.get(key, "") for key in
                            ("CC", "CXX", "CFLAGS", "CXXFLAGS", "LDFLAGS", "SDKROOT",
                             "MACOSX_DEPLOYMENT_TARGET", "CMAKE_PREFIX_PATH")}}


def verify_provider(package, expected):
    folder = output(package)
    receipt = json.loads((folder / "build-info.json").read_text())
    if receipt["identity"] != expected or receipt["package"] != package:
        raise ValueError(f"{package}: stale or incompatible provider output")
    if fingerprint(folder / "install") != receipt["installSha256"]:
        report_fingerprint_difference(package, folder / "install", receipt.get("installRecords"))
        raise ValueError(f"{package}: provider output integrity check failed")
    return receipt


def skip_checks():
    """A timing experiment builds and installs without the check-* targets; the
    tests are the larger half of the work and say nothing about transport."""
    return os.environ.get("LLVM_SKIP_CHECKS", "") == "1"


def fast_fixture():
    """The 40-minute fixture: no assertions, no examples, docs or benchmarks.
    The same flags on every node and in the local baseline, so the two builds
    compared are the same build."""
    return os.environ.get("LLVM_FAST", "") == "1"


def bundle_compression():
    """How the toolchain archive is compressed: xz for a release, gz or none for
    a timing fixture, where a single-threaded xz of the whole install tree
    would be the longest step on either side and say nothing about placement."""
    choice = os.environ.get("LLVM_BUNDLE_COMPRESSION", "xz")
    if choice not in ("xz", "gz", "none"):
        raise ValueError(f"LLVM_BUNDLE_COMPRESSION must be xz, gz or none, not {choice!r}")
    return "" if choice == "none" else choice


def positive_env(name, default):
    value = int(os.environ.get(name, default))
    if value < 1:
        raise ValueError(f"{name} must be positive")
    return value


def configure(package, current):
    folder = output(package)
    folder.mkdir(parents=True, exist_ok=True)
    previous = folder / "configured-input.json"
    if previous.exists() and json.loads(previous.read_text()) != current:
        raise ValueError(f"{folder}: inputs changed; remove this package's _dispat directory first")
    major, minor, patch, suffix = SEMVER.fullmatch(current["version"]).groups()
    source = SOURCES.get(package, package)
    args = ["cmake", "-G", "Ninja", "-S", ROOT / source, "-B", folder / "build",
            "-DCMAKE_BUILD_TYPE=Release", f"-DCMAKE_INSTALL_PREFIX={folder / 'install'}",
            "-DCMAKE_INSTALL_LIBDIR=lib", "-DBUILD_SHARED_LIBS=OFF", "-DLLVM_ENABLE_LTO=OFF",
            f"-DLLVM_ENABLE_ASSERTIONS={'OFF' if fast_fixture() else 'ON'}",
            f"-DLLVM_INCLUDE_TESTS={'OFF' if skip_checks() else 'ON'}",
            "-DLLVM_INCLUDE_EXAMPLES=OFF", "-DLLVM_INCLUDE_DOCS=OFF", "-DLLVM_INCLUDE_BENCHMARKS=OFF",
            f"-DLLVM_PARALLEL_LINK_JOBS={positive_env('LLVM_LINK_JOBS', '1')}"]
    if source == "llvm":
        args += ["-DLLVM_ENABLE_PROJECTS=", "-DLLVM_ENABLE_RUNTIMES=",
                 f"-DLLVM_TARGETS_TO_BUILD={current['targets']}", "-DLLVM_INSTALL_UTILS=ON",
                 f"-DLLVM_INSTALL_GTEST={'OFF' if skip_checks() else 'ON'}",
                 f"-DLLVM_BUILD_TESTS={'OFF' if skip_checks() else 'ON'}",
                 "-DLLVM_INSTALL_TOOLCHAIN_ONLY=OFF", "-DLLVM_BUILD_LLVM_DYLIB=OFF",
                 f"-DLLVM_VERSION_MAJOR={major}", f"-DLLVM_VERSION_MINOR={minor}",
                 f"-DLLVM_VERSION_PATCH={patch}", f"-DLLVM_VERSION_SUFFIX={suffix or ''}"]
    else:
        verify_provider("llvm", current)
        sdk = output("llvm") / "install"
        for required in ("lib/cmake/llvm/LLVMConfig.cmake", "bin/llvm-tblgen", "bin/FileCheck"):
            if not (sdk / required).is_file():
                raise ValueError(f"LLVM SDK is missing {required}; rebuilding it here is forbidden")
        args += [f"-DLLVM_DIR={sdk / 'lib/cmake/llvm'}", f"-DLLVM_TABLEGEN={sdk / 'bin/llvm-tblgen'}",
                 f"-DLLVM_EXTERNAL_LIT={ROOT / 'llvm/utils/lit/lit.py'}"]
    # Write the identity first: a failed configure cannot leave an unidentified cache.
    previous.write_text(json.dumps(current, indent=2) + "\n")
    run(*args)


def merge_install(source, destination):
    """Merge only identical overlaps, preserving symlinks rather than dereferencing them."""
    for path in sorted(source.rglob("*")):
        target = destination / path.relative_to(source)
        if path.is_dir() and not path.is_symlink():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            same = (path.is_symlink() and target.is_symlink() and
                    os.readlink(path) == os.readlink(target))
            if not path.is_symlink() and not target.is_symlink() and target.is_file():
                same = digest(path) == digest(target) and path.stat().st_mode == target.stat().st_mode
            if not same:
                raise ValueError(f"conflicting toolchain files: {target}")
        elif path.is_symlink():
            target.symlink_to(os.readlink(path))
        else:
            shutil.copy2(path, target)


def build(package, current):
    folder = output(package)
    # No previously successful receipt can survive an incomplete rebuild.
    (folder / "build-info.json").unlink(missing_ok=True)
    providers = {p: verify_provider(p, current)["installSha256"] for p in PROVIDERS[package]}
    if (folder / "install").exists():
        raise ValueError(f"{folder / 'install'} already exists; use a fresh task worktree")
    if package == "toolchain":
        (folder / "install").mkdir(parents=True)
        for provider in PROVIDERS[package]:
            merge_install(output(provider) / "install", folder / "install")
    else:
        configure(package, current)
        jobs = str(positive_env("LLVM_BUILD_JOBS", "4"))
        run("cmake", "--build", folder / "build", "--parallel", jobs)
        if not skip_checks():
            run("cmake", "--build", folder / "build", "--target", f"check-{package}", "--parallel", jobs)
        run("cmake", "--install", folder / "build")
    records = fingerprint_records(folder / "install")
    receipt = {"schema": 1, "package": package, "identity": current, "providers": providers,
               "installSha256": digest_records(records), "installRecords": records}
    if package == "toolchain":
        checks = {"llvm": "llvm-config", "clang": "clang", "lld": "ld.lld"}
        for provider, command in checks.items():
            if provider in PROVIDERS["toolchain"]:
                run(folder / "install/bin" / command, "--version")
        dist = folder / "dist"
        dist.mkdir(exist_ok=False)
        stem = f"llvm-toolchain-{current['version']}-{current['platform'].replace('/', '-')}"
        compression = bundle_compression()
        archive = dist / f"{stem}.tar{'.' + compression if compression else ''}"
        with tarfile.open(archive, "w:" + compression) as stream:
            stream.add(folder / "install", arcname=stem)
        if archive.stat().st_size >= 2 * 1024**3:
            raise ValueError("archive exceeds GitHub's 2 GiB per-asset limit; add reviewed splitting before release")
        receipt["archive"] = {"name": archive.name, "sha256": digest(archive)}
        (dist / "SHA256SUMS").write_text(f"{receipt['archive']['sha256']}  {archive.name}\n")
        (dist / "build-info.json").write_text(json.dumps(receipt, indent=2) + "\n")
    (folder / "build-info.json").write_text(json.dumps(receipt, indent=2) + "\n")


def release_ready():
    # Deliberately not an environment toggle: activation requires a reviewed change.
    state = json.loads((ROOT / ".ci/dispat/readiness.json").read_text())
    raise ValueError("Distributed LLVM releases are blocked:\n- " + "\n- ".join(state["blockers"]))


def export_assets():
    # Do not permit standalone publication to evade the same readiness gate.
    release_ready()
    current = identity()
    folder = output("toolchain")
    receipt = json.loads((folder / "build-info.json").read_text())
    if receipt["identity"] != current or receipt["package"] != "toolchain":
        raise ValueError("toolchain archive belongs to different build inputs")
    dist = folder / "dist"
    archive = dist / receipt["archive"]["name"]
    if archive.parent != dist or digest(archive) != receipt["archive"]["sha256"]:
        raise ValueError("toolchain archive integrity check failed")
    if json.loads((dist / "build-info.json").read_text()) != receipt:
        raise ValueError("archive metadata differs from admitted build metadata")
    if (dist / "SHA256SUMS").read_text() != f"{receipt['archive']['sha256']}  {archive.name}\n":
        raise ValueError("archive checksum file differs from build metadata")
    assets = [archive, dist / "SHA256SUMS", dist / "build-info.json"]
    for path in assets:
        if not path.is_file() or any(c.isspace() for c in str(path)):
            raise ValueError(f"invalid dispat GitHub asset path: {path}")
    destination = os.environ.get("DISPAT_OUTPUT")
    if not destination:
        raise ValueError("asset export must run inside a dispat publish stage")
    with open(destination, "a") as stream:
        stream.write("DISPAT_EXPORT_GITHUB=" + " ".join(str(p) for p in assets) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("configure", "build", "export", "release-ready"))
    parser.add_argument("package", choices=PACKAGES, nargs="?")
    args = parser.parse_args()
    if args.action == "release-ready":
        release_ready()
    if args.action == "export":
        export_assets()
        return
    if args.package is None or (args.action == "configure" and args.package == "toolchain"):
        parser.error("configure/build requires a source package; toolchain supports build only")
    current = identity(require_clean=args.action == "build")
    {"configure": configure, "build": build}[args.action](args.package, current)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        print(f"dispat LLVM: {error}", file=sys.stderr)
        sys.exit(1)
