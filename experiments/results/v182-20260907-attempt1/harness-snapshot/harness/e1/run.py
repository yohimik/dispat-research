"""E1 differential runner: gen -> realize -> dispat vs oracle -> classify.

Divergence classes (known paper gaps, RUNBOOK phase 1):
  PG1  channel-entry patch: channel-only release from a clean stable
       baseline; paper's Eq(7)+guard refuses, dispat applies one patch.
  PG2  prerelease-train discharge: work published by a prerelease never
       leaves the paper's window; dispat's fresh-window discharges it.
  PG3  bump-axis liveness: paper Eq(4/5) admits carets on none-bump
       units (pb defaults to patch); dispat's bump axis requires a bump.
  GUARD oracle refused (computed <= baseline) and dispat agrees nothing
       ships: counted as agreement.
Anything else -> UNKNOWN, dossier written.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tarfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
sys.path.insert(0, os.path.dirname(__file__))
import realize            # noqa: E402
import planjson           # noqa: E402
from gen import gen       # noqa: E402
from oracle import Oracle  # noqa: E402


class DispatExecutionError(RuntimeError):
    def __init__(self, result):
        super().__init__(f"dispat status exited {result.returncode}")
        self.result = result


def dispat_plan(workdir):
    r = subprocess.run(["dispat", "status", "--log-format", "json"],
                       cwd=workdir, capture_output=True, text=True)
    if r.returncode != 0:
        raise DispatExecutionError(r)
    return planjson.parse(r.stdout.splitlines() + r.stderr.splitlines())


def failure_dossier(root, seed, inst, workdir, result):
    dst = os.path.join(root, f"seed{seed}")
    os.makedirs(dst, exist_ok=True)
    fsck = subprocess.run(["git", "fsck", "--no-dangling"], cwd=workdir,
                          capture_output=True, text=True)
    with open(os.path.join(dst, "stdout.log"), "w") as f:
        f.write(result.stdout)
    with open(os.path.join(dst, "stderr.log"), "w") as f:
        f.write(result.stderr)
    with open(os.path.join(dst, "failure.json"), "w") as f:
        json.dump({"seed": seed, "kind": "invalid-execution",
                   "command": result.args,
                   "returncode": result.returncode,
                   "stdout": result.stdout, "stderr": result.stderr,
                   "fixture_git_fsck": {"returncode": fsck.returncode,
                                        "stdout": fsck.stdout,
                                        "stderr": fsck.stderr},
                   "inst": inst}, f, indent=1)
    with tarfile.open(os.path.join(dst, "fixture.tar.gz"), "w:gz") as archive:
        archive.add(workdir, arcname="fixture")
    return os.path.relpath(dst, os.path.dirname(root))


def compare(inst, om, dm):
    """Per-package compare; returns (verdict, detail)."""
    pre = set(inst["features"]["prerelease"])
    diffs = []
    for p in inst["packages"]:
        o, d = om.get(p, {}), dm.get(p, {})
        if o.get("guard"):
            if not d.get("changed"):
                continue                       # GUARD agreement
            if o["channel"] != "stable":
                diffs.append((p, "PG1"))
                continue
        oc, dc = o.get("changed", False), d.get("changed", False)
        same = (oc == dc and
                (not oc or (o["next"] == d["next"]
                            and o["bump"] == d["bump"]
                            and o["channel"] == d["channel"])))
        if same:
            continue
        if p in pre:
            diffs.append((p, "PG2"))
        elif pre and (o.get("channel") != d.get("channel")
                      or "catch-up" in str(d.get("reason", ""))):
            diffs.append((p, "PG2x"))
        elif any(u.get("pd", 0) != 0
                 and Oracle.bump_of(u) == "none"
                 for c in inst["commits"] for u in c["units"]):
            diffs.append((p, "PG3?"))
        else:
            diffs.append((p, "UNKNOWN"))
    # Cascade resolution: a row that only diverges because dispat
    # propagated from a package already classified into a PG class, or
    # from a package with a prerelease baseline (the domain the PG
    # classes describe), is that class's secondary effect, which is
    # what PG2x names. dispat's dueTo carries the attribution; the
    # label text is release-version-dependent (1.4.0 said "catch-up
    # from X", 1.6.0 says "propagated from X, Y"), so the rule keys on
    # the sources, not the phrasing.
    classed = dict(diffs)
    resolved = []
    for p, v in diffs:
        if v == "UNKNOWN":
            srcs = dm.get(p, {}).get("dueTo") or []
            if pre and any(classed.get(s) in ("PG1", "PG2", "PG2x")
                           or s in pre for s in srcs):
                v = "PG2x"
        resolved.append((p, v))
    return resolved


def one(seed, profile, dossier_dir):
    inst = gen(seed, profile)
    w = tempfile.mkdtemp(prefix="e1-")
    try:
        realize.realize(inst, w)
        try:
            check = subprocess.run(["git", "fsck", "--full", "--no-dangling"], cwd=w, capture_output=True, text=True)
            if check.returncode:
                raise DispatExecutionError(check)
            dm = dispat_plan(w)
        except DispatExecutionError as e:
            failure = failure_dossier(
                os.path.join(os.path.dirname(dossier_dir),
                             f"failures-{profile}"),
                seed, inst, w, e.result)
            return {"seed": seed, "packages": len(inst["packages"]),
                    "diffs": [], "invalid": True, "failure": failure}
        om = Oracle(inst).plan()
        diffs = compare(inst, om, dm)
        unknown = [d for d in diffs if d[1] == "UNKNOWN"]
        if unknown and dossier_dir:
            dst = os.path.join(dossier_dir, f"seed{seed}")
            os.makedirs(dst, exist_ok=True)
            json.dump({"inst": inst, "oracle": om, "dispat": dm,
                       "diffs": diffs},
                      open(os.path.join(dst, "dossier.json"), "w"), indent=1)
        return {"seed": seed, "packages": len(inst["packages"]),
                "diffs": diffs}
    finally:
        shutil.rmtree(w, ignore_errors=True)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--profile", default="core")
    ap.add_argument("--out", default="/results")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    dossier = os.path.join(a.out, f"dossiers-{a.profile}")
    rows = []
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(a.workers) as ex:
        for row in ex.map(one, range(a.seed0, a.seed0 + a.n),
                          [a.profile] * a.n, [dossier] * a.n,
                          chunksize=8):
            rows.append(row)

    classes = {}
    for row in rows:
        for _, cls in row["diffs"]:
            classes[cls] = classes.get(cls, 0) + 1
    invalid = sum(1 for r in rows if r.get("invalid"))
    clean = sum(1 for r in rows if not r["diffs"] and not r.get("invalid"))
    summary = {"profile": a.profile, "instances": a.n, "clean": clean,
               "invalid": invalid,
               "divergence_classes": classes,
               "dispat": subprocess.run(["dispat", "--version"], capture_output=True, text=True).stdout.strip().splitlines()[-1]}
    json.dump({"summary": summary, "rows": rows},
              open(os.path.join(a.out, f"e1-{a.profile}-{a.seed0}-{a.n}.json"),
                   "w"), indent=1)
    print(json.dumps(summary))
    if invalid:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
