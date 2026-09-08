"""E3a: historical replay. For each of the last k releases of a repo:
checkout the release commit's parent in a worktree, plan with dispat, and
compare the planned (package, version) set against what the release
actually shipped. Reachability makes the replay time-safe: tags created
by later releases point at commits not reachable from the old checkout.

Profiles:
  gcn  googleapis/google-cloud-node — release-please manifest mode.
       Expected data: the diff of .release-please-manifest.json at each
       `chore: release main` merge. Tags: {component}-v{version}.
  cc   conventional-changelog — lerna independent + conventional commits.
       Expected data: the name@version tags pointing at each lerna
       release commit. Tags: {name}@{version} (dispat's default).
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
import planjson  # noqa: E402


def sh(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True,
                          text=True).stdout


def gcn_releases(repo, k):
    """[(commit, {pkg_dir: version})] newest first."""
    shas = sh(["git", "log", "--grep", "chore: release main",
               "--format=%H", "-n", str(k + 3)], repo).split()
    out = []
    for s in shas:
        try:
            new = json.loads(sh(["git", "show",
                                 f"{s}:.release-please-manifest.json"], repo))
            old = json.loads(sh(["git", "show",
                                 f"{s}^:.release-please-manifest.json"], repo))
        except json.JSONDecodeError:
            continue
        diff = {p.split("/")[-1]: v for p, v in new.items()
                if old.get(p) != v and p.startswith("packages/")}
        if diff:
            out.append((s, diff))
        if len(out) >= k:
            break
    return out


def cc_releases(repo, k):
    shas = sh(["git", "log", "--grep", "^Publish$",
               "--format=%H", "-n", str(k + 10)], repo).split()
    out = []
    for s in shas:
        tags = sh(["git", "tag", "--points-at", s], repo).split()
        diff = {}
        for t in tags:
            if "@" in t[1:]:
                name, _, ver = t.rpartition("@")
                diff[name] = ver
        if diff:
            out.append((s, diff))
        if len(out) >= k:
            break
    return out


CONFIG = {
    "gcn": """\
logFormat: json
spaces:
  packages:
    path: packages
    tagFormat: "{name}-v{version}"
""",
    "cc": """\
logFormat: json
spaces:
  packages:
    path: packages
    tagFormat: "{name}@{version}"
""",
}


def component_map(wt):
    """dir name -> release-please component (npm name minus scope)."""
    out = {}
    pdir = os.path.join(wt, "packages")
    for d in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
        pj = os.path.join(pdir, d, "package.json")
        if not os.path.exists(pj):
            continue
        try:
            name = json.load(open(pj)).get("name", d)
        except json.JSONDecodeError:
            name = d
        out[d] = name.rpartition("/")[2]
    return out


def write_config(profile, wt):
    if profile != "gcn":
        open(os.path.join(wt, "dispat.yaml"), "w").write(CONFIG[profile])
        return
    lines = ["logFormat: json", 'tagFormat: "{name}-v{version}"',
             "packages:"]
    for d, comp in component_map(wt).items():
        lines.append(f"  {comp}:")
        lines.append(f"    path: packages/{d}")
    open(os.path.join(wt, "dispat.yaml"), "w").write("\n".join(lines) + "\n")


def replay(repo, profile, k, out_path):
    rels = gcn_releases(repo, k) if profile == "gcn" else cc_releases(repo, k)
    rows = []
    for i, (sha, expected) in enumerate(rels):
        wt = f"/tmp/replay-{profile}-{i}"
        subprocess.run(["git", "worktree", "remove", "--force", wt],
                       cwd=repo, capture_output=True)
        r = subprocess.run(["git", "worktree", "add", "--no-checkout",
                            "--detach", wt, f"{sha}^"], cwd=repo,
                           capture_output=True, text=True)
        if r.returncode != 0:
            rows.append({"sha": sha, "error": r.stderr[-200:]})
            continue
        # sparse: package discovery needs only the manifests to exist
        subprocess.run(["git", "sparse-checkout", "set", "--no-cone",
                        "/packages/*/package.json", "/*.json"],
                       cwd=wt, capture_output=True)
        subprocess.run(["git", "checkout", "-q"], cwd=wt,
                       capture_output=True)
        write_config(profile, wt)
        pr = subprocess.run(["dispat", "status", "--log-format", "json"],
                            cwd=wt, capture_output=True, text=True,
                            timeout=1800)
        plan = planjson.parse(pr.stdout.splitlines() + pr.stderr.splitlines())
        if profile == "gcn":
            cm = component_map(wt)
            expected = {cm.get(d, d): v for d, v in expected.items()}
        planned = {p: r_["next"] for p, r_ in plan.items() if r_["changed"]}
        exact = sum(1 for p, v in expected.items() if planned.get(p) == v)
        extra = sorted(set(planned) - set(expected))
        missing = sorted(set(expected) - set(planned))
        verdiff = {p: (expected[p], planned[p]) for p in expected
                   if p in planned and planned[p] != expected[p]}
        rows.append({"sha": sha[:10], "released": len(expected),
                     "planned": len(planned), "exact": exact,
                     "missing": missing[:8], "extra_n": len(extra),
                     "verdiff": dict(list(verdiff.items())[:8])})
        print(json.dumps(rows[-1])[:400], flush=True)
        subprocess.run(["git", "worktree", "remove", "--force", wt],
                       cwd=repo, capture_output=True)
    json.dump(rows, open(out_path, "w"), indent=1)


if __name__ == "__main__":
    repo, profile, k, out = (sys.argv[1], sys.argv[2], int(sys.argv[3]),
                             sys.argv[4])
    replay(repo, profile, k, out)
