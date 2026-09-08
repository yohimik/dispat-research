"""Realize an instance JSON (schema in e1/oracle.py) as a real git
repository that the pinned dispat binary can plan against.

Design decisions (RUNBOOK phase 1):
- edges are declared in dispat.yaml (`packages.<name>.dependencies`), not
  inferred from manifests, so E is exactly the instance's E;
- units become `git commit --allow-empty` with explicit-scope CCME
  messages, so history size is independent of file churn;
- tags are real git tags in the default `<name>@<version>` format.
"""
import json
import os
import subprocess
import sys


def sh(args, cwd, env=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                       env=env)
    if r.returncode != 0:
        raise RuntimeError(f"{args}: {r.stderr[-500:]}")
    return r.stdout


def message(u):
    """Unit -> CCME commit message. Mirrors oracle field semantics 1:1."""
    inline = ""
    pd = u.get("pd", 0)
    pb = u.get("pb")
    if pd == 1:
        inline += "^" + (pb or "")
    elif pd == -1:
        inline += "^^" + (pb or "")
    elif pd > 1:
        inline += ("^" + pb if pb else "") + "+" + str(pd)
    if u.get("channel"):
        inline += "%" + u["channel"]
    if u.get("pchannel"):
        inline += "%%" + u["pchannel"]
        pcd = u.get("pcd", 0)
        inline += "++*" if pcd == -1 else "++" + str(pcd)
    head = (u["type"] + "(" + ",".join(u["scope"]) + ")" + inline
            + ("!" if u.get("breaking") else "") + ": x")
    if u.get("releaseAs"):
        return head + "\n\nRelease-As: " + u["releaseAs"]
    return head


def realize(inst, workdir, scripts=None, extra_cfg=""):
    os.makedirs(workdir, exist_ok=True)
    sh(["git", "init", "-q", "."], workdir)
    # Large synthetic histories are short-lived. A background auto-gc can
    # outlive a cell and race its teardown under constrained Docker runs.
    sh(["git", "config", "gc.auto", "0"], workdir)
    lines = ["logFormat: json", "spaces:", "  packages:", "    path: packages"]
    if scripts:
        lines += ["    scripts:"] + [f"      {k}: {v}" for k, v in scripts.items()]
        lines += ["    flow:"] + [f"      {k}: {k}" for k in scripts]
    deps = {}
    for a, b in inst["edges"]:
        deps.setdefault(a, []).append(b)
    if deps:
        lines.append("packages:")
        for a in sorted(deps):
            lines.append(f"  {a}:")
            lines.append(f"    dependencies: [{', '.join(sorted(deps[a]))}]")
    if extra_cfg:
        lines.append(extra_cfg)
    with open(os.path.join(workdir, "dispat.yaml"), "w") as f:
        f.write("\n".join(lines) + "\n")
    for p in inst["packages"]:
        d = os.path.join(workdir, "packages", p)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, ".keep"), "w").close()
    sh(["git", "add", "-A"], workdir)

    shas = {}
    git_env = os.environ.copy()
    git_env.update({"GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
                    "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"})
    use_commit_tree = os.environ.get("REALIZE_COMMIT_TREE") == "1"
    tree = sh(["git", "write-tree"], workdir).strip() if use_commit_tree else None
    parent = None
    for index, c in enumerate(inst["commits"]):
        if index == 0:
            assert not c["units"], "root commit carries no units in v1"
            msg = "chore: baseline"
        else:
            msg = "\n---\n".join(message(u) for u in c["units"]) \
                if c["units"] else "docs: pad"
        if use_commit_tree:
            args = ["git", "commit-tree", tree, "-m", msg]
            if parent:
                args += ["-p", parent]
            parent = sh(args, workdir, env=git_env).strip()
            shas[c["id"]] = parent
        else:
            sh(["git", "commit", "-q", "--allow-empty", "-m", msg], workdir,
               env=git_env)
            shas[c["id"]] = sh(["git", "rev-parse", "HEAD"], workdir).strip()
    if use_commit_tree:
        sh(["git", "update-ref", "refs/heads/main", parent], workdir)
    for t in inst["tags"]:
        sh(["git", "tag", f"{t['pkg']}@{t['version']}", shas[t["commit"]]],
           workdir)
    return shas


if __name__ == "__main__":
    inst = json.load(open(sys.argv[1]))
    realize(inst, sys.argv[2])
    print("ok")
