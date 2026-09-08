"""Seeded instance generator. Profiles:

  core: the (H1,H2) domain — stable baselines everywhere, no channel
        directives, no caret on none-bump types, cancels/holds allowed.
        Expected differential result: zero divergences.
  full: adds channel commits, prerelease baselines, carets on none-bump
        types — the features where the paper's model is known to be
        incomplete; divergences expected in classes PG1..PG3 (run.py).
"""
import random


def gen(seed, profile="core"):
    r = random.Random(seed)
    n = r.randint(5, 20)
    pkgs = [f"p{i:02d}" for i in range(n)]
    # layered DAG: each package may depend on packages of lower index
    edges = []
    for i in range(1, n):
        for _ in range(r.randint(0, min(3, i))):
            j = r.randrange(i)
            e = (pkgs[i], pkgs[j])
            if e not in edges:
                edges.append(e)

    commits = [{"id": "c0", "units": []}]
    tags = []
    prerelease = set()
    for i, p in enumerate(pkgs):
        v = f"{r.randint(1, 3)}.{r.randint(0, 9)}.{r.randint(0, 9)}"
        tags.append({"pkg": p, "version": v, "commit": "c0"})
        if profile == "full" and r.random() < 0.2:
            prerelease.add(p)

    nu = r.randint(4, 12)
    held_or_cancelled = set()
    for k in range(1, nu + 1):
        cid = f"c{k}"
        u = {"type": None, "scope": [], "breaking": False, "pd": 0}
        roll = r.random()
        scope = [r.choice(pkgs)]
        if r.random() < 0.25 and n > 1:
            scope.append(r.choice([p for p in pkgs if p != scope[0]]))
        u["scope"] = sorted(set(scope))
        if roll < 0.05 and u["scope"][0] not in held_or_cancelled:
            u["type"] = "cancel"
            u["scope"] = [u["scope"][0]]
            held_or_cancelled.add(u["scope"][0])
        elif roll < 0.08 and u["scope"][0] not in held_or_cancelled:
            u["type"] = "release"
            u["scope"] = [u["scope"][0]]
            u["releaseAs"] = "none"
            held_or_cancelled.add(u["scope"][0])
        else:
            u["type"] = r.choice(["feat", "fix", "fix", "perf",
                                  "docs", "chore"])
            u["breaking"] = r.random() < 0.06
            bumpless = u["type"] in ("docs", "chore") and not u["breaking"]
            may_caret = (not bumpless) or profile == "full"
            if may_caret and r.random() < 0.45:
                u["pd"] = r.choice([1, 1, 2, -1])
                if r.random() < 0.3:
                    u["pb"] = r.choice(["patch", "minor", "major"])
            if profile == "full" and r.random() < 0.12:
                if r.random() < 0.5:
                    u["channel"] = r.choice(["beta", "rc"])
                else:
                    u["pchannel"] = r.choice(["beta", "rc"])
                    u["pcd"] = r.choice([1, 2, -1])
        commits.append({"id": cid, "units": [u]})

    # prerelease baselines sit mid-history (their stable base is at c0).
    # sorted: iterating the raw set consumes RNG draws in hash order,
    # which varies per process and made seed->instance irreproducible.
    for p in sorted(prerelease):
        st = next(t for t in tags if t["pkg"] == p)
        x, y, z = (int(q) for q in st["version"].split("."))
        j = r.randint(1, nu)
        tags.append({"pkg": p, "version": f"{x}.{y + 1}.0-beta.{r.randint(0, 3)}",
                     "commit": f"c{j}"})

    return {"packages": pkgs, "edges": edges, "commits": commits,
            "tags": tags, "head": f"c{nu}", "seed": seed,
            "profile": profile,
            "features": {"prerelease": sorted(prerelease)}}


if __name__ == "__main__":
    import json
    import sys
    print(json.dumps(gen(int(sys.argv[1]),
                         sys.argv[2] if len(sys.argv) > 2 else "core")))
