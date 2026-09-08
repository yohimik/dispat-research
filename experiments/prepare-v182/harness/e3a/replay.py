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


def checked_plan(stdout, stderr):
    lines=(stdout+stderr).splitlines()
    events=[]
    for line in lines:
        if line.startswith('{'):
            try: events.append(json.loads(line))
            except ValueError: pass
    summaries=[e for e in events if e.get('message')=='release plan ready']
    if len(summaries)!=1:
        raise RuntimeError('missing or duplicate final plan summary: '+stdout+stderr)
    result=planjson.parse(lines)
    if sum(bool(r['changed']) for r in result.values())!=summaries[0]['releasing']:
        raise RuntimeError('extracted plan count differs from declared count')
    return result


def sh(args, cwd=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(json.dumps({"command": args, "cwd": cwd,
                                       "returncode": r.returncode,
                                       "stdout": r.stdout,
                                       "stderr": r.stderr}))
    return r.stdout


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
    if len(rels) != k:
        raise RuntimeError(f"expected {k} {profile} releases, found {len(rels)}")
    rows = []
    for i, (sha, expected) in enumerate(rels):
        wt = f"/tmp/replay-{profile}-{i}"
        subprocess.run(["git", "worktree", "remove", "--force", wt],
                       cwd=repo, capture_output=True)
        try:
            sh(["git", "worktree", "add", "--no-checkout", "--detach",
                wt, f"{sha}^"], repo)
            # sparse: package discovery needs only the manifests to exist
            sh(["git", "sparse-checkout", "set", "--no-cone",
                "/packages/*/package.json", "/*.json"], wt)
            sh(["git", "checkout", "-q"], wt)
            write_config(profile, wt)
            pr = subprocess.run(["dispat", "status", "--log-format", "json"],
                                cwd=wt, capture_output=True, text=True,
                                timeout=1800)
            if pr.returncode != 0:
                raise RuntimeError(json.dumps({
                    "command": ["dispat", "status", "--log-format", "json"],
                    "cwd": wt, "returncode": pr.returncode,
                    "stdout": pr.stdout, "stderr": pr.stderr}))
            plan = checked_plan(pr.stdout, pr.stderr)
            if profile == "gcn":
                cm = component_map(wt)
                expected = {cm.get(d, d): v for d, v in expected.items()}
            planned = {p: r_["next"] for p, r_ in plan.items() if r_["changed"]}
            exact = sum(1 for p, v in expected.items() if planned.get(p) == v)
            extra = sorted(set(planned) - set(expected))
            missing = sorted(set(expected) - set(planned))
            verdiff = {p: (expected[p], planned[p]) for p in expected
                       if p in planned and planned[p] != expected[p]}
            rows.append({"sha": sha, "released": len(expected),
                         "planned": len(planned), "exact": exact,
                         "missing": missing[:8], "extra_n": len(extra),
                         "verdiff": dict(list(verdiff.items())[:8])})
            print(json.dumps(rows[-1])[:400], flush=True)
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", wt],
                           cwd=repo, capture_output=True)
    if len(rows) != k:
        raise RuntimeError(f"expected {k} completed rows, found {len(rows)}")
    json.dump(rows, open(out_path, "w"), indent=1)


if __name__ == "__main__":
    repo, profile, k, out = (sys.argv[1], sys.argv[2], int(sys.argv[3]),
                             sys.argv[4])
    try:
        replay(repo, profile, k, out)
    except Exception as e:
        with open(out + ".failure.json", "w") as f:
            json.dump({"repo": repo, "profile": profile, "k": k,
                       "error": str(e)}, f, indent=1)
        raise
