"""E4 workspace generator: big synthetic workspaces, realized cheaply.
Shapes: layered (realistic), chain (worst depth), star (worst fan-out).
All packages baselined at c0 (k=1 distinct window class)."""
import os
import random
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
import realize  # noqa: E402


def graph(p, shape, seed):
    r = random.Random(seed)
    pkgs = [f"p{i:05d}" for i in range(p)]
    edges = []
    if shape == "layered":
        for i in range(1, p):
            for _ in range(r.randint(1, 3)):
                edges.append((pkgs[i], pkgs[r.randrange(max(1, i))]))
    elif shape == "chain":
        edges = [(pkgs[i], pkgs[i - 1]) for i in range(1, p)]
    elif shape == "star":
        edges = [(pkgs[i], pkgs[0]) for i in range(1, p)]
    return pkgs, sorted(set(edges))


def build(p, shape, units, pad, seed, workdir, publish_script=None):
    pkgs, edges = graph(p, shape, seed)
    r = random.Random(seed + 1)
    commits = [{"id": "c0", "units": []}]
    for k in range(1, units + 1):
        u = {"type": r.choice(["feat", "fix", "fix", "perf"]),
             "scope": [r.choice(pkgs)], "breaking": r.random() < 0.03,
             "pd": r.choice([0, 0, 1, 1, 2, -1])}
        commits.append({"id": f"c{k}", "units": [u]})
    for k in range(units + 1, units + 1 + pad):
        commits.append({"id": f"c{k}", "units": []})   # docs: pad
    tags = [{"pkg": q, "version": "1.0.0", "commit": "c0"} for q in pkgs]
    inst = {"packages": pkgs, "edges": edges, "commits": commits,
            "tags": tags, "head": f"c{units + pad}",
            "features": {"prerelease": []}}
    scripts = {"publish": publish_script} if publish_script else None
    extra = "changelog:\n  enabled: false\ngithub:\n  enabled: false" \
        if publish_script else ""
    realize.realize(inst, workdir, scripts=scripts, extra_cfg=extra)
    return inst


if __name__ == "__main__":
    p, shape, units, pad, seed, workdir = (int(sys.argv[1]), sys.argv[2],
                                           int(sys.argv[3]), int(sys.argv[4]),
                                           int(sys.argv[5]), sys.argv[6])
    build(p, shape, units, pad, seed, workdir)
    n = subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=workdir,
                       capture_output=True, text=True).stdout.strip()
    print(f"built P={p} shape={shape} commits={n} edges into {workdir}")
