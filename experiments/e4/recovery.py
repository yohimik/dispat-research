"""E4c: recovery convergence with the real executor. A file:// bare origin
makes the release lock and pushes real; the publish script fails for any
package named in .deny/; the harness re-runs `dispat release` until the
plan is empty, recording per-run outcomes.

Asserts across the sequence: runs <= n (G6), versions constant per
package (G3), no package enters a later plan (G5)."""
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from gen import build       # noqa: E402
import planjson             # noqa: E402


def sh(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def release_events(w):
    r = sh(["dispat", "release", "--log-format", "json"], w)
    pub, fail, blocked = {}, set(), set()
    for line in (r.stdout + r.stderr).splitlines():
        if not line.startswith("{"):
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        m, p = e.get("message", ""), e.get("package")
        if not p:
            continue
        if "published" in m:
            pub[p] = e.get("version", "")
        elif "failed" in m:
            fail.add(p)
        elif e.get("code") == "W194" or "skipped" in m:
            blocked.add(p)
    return pub, fail, blocked


def episode(n_pkgs, p_fail, seed, shape="layered"):
    w = tempfile.mkdtemp(prefix="e4c-")
    try:
        build(n_pkgs, shape, units=max(10, n_pkgs // 5), pad=0, seed=seed,
              workdir=w, publish_script="'[ ! -f \"../../.deny/${DISPAT_PACKAGE}\" ]'")
        origin = tempfile.mkdtemp(prefix="e4c-origin-") + "/o.git"
        subprocess.run(["git", "init", "-q", "--bare", origin])
        sh(["git", "remote", "add", "origin", origin], w)
        sh(["git", "push", "-q", "origin", "main"], w)

        rng = random.Random(seed)
        first_plan = planjson.parse(
            sh(["dispat", "status", "--log-format", "json"], w
               ).stdout.splitlines())
        plan0 = {p for p, r in first_plan.items() if r["changed"]}
        ver0 = {p: r["next"] for p, r in first_plan.items() if r["changed"]}
        n = len(plan0)

        runs, rows, invariant_errors = 0, [], []
        remaining = set(plan0)
        while runs < n + 5:
            runs += 1
            deny = {p for p in remaining if rng.random() < p_fail}
            if deny == remaining and remaining:      # guarantee progress
                deny.discard(sorted(remaining)[0])
            dd = os.path.join(w, ".deny")
            shutil.rmtree(dd, ignore_errors=True)
            os.makedirs(dd)
            for p in deny:
                open(os.path.join(dd, p), "w").close()
            pub, fail, blocked = release_events(w)
            nxt = planjson.parse(
                sh(["dispat", "status", "--log-format", "json"], w
                   ).stdout.splitlines())
            now = {p for p, r in nxt.items() if r["changed"]}
            if not now <= remaining:
                invariant_errors.append(
                    {"run": runs, "invariant": "G5", "packages": sorted(now - remaining)})
            for p in now:
                if nxt[p]["next"] != ver0[p]:
                    invariant_errors.append(
                        {"run": runs, "invariant": "G3", "package": p,
                         "expected": ver0[p], "actual": nxt[p]["next"]})
            rows.append({"run": runs, "planned": len(remaining),
                         "remaining": len(now),
                         "published_log_events": len(pub),
                         "failed_log_events": len(fail),
                         "blocked_log_events": len(blocked)})
            remaining = now
            if not remaining:
                break
        return {"n": n, "p_fail": p_fail, "seed": seed, "runs": runs,
                "converged": not remaining, "g_ok": not invariant_errors,
                "invariant_errors": invariant_errors,
                "trace": rows}
    finally:
        shutil.rmtree(w, ignore_errors=True)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/results"
    os.makedirs(out, exist_ok=True)
    results = []
    for n_pkgs in (20, 100):
        for p_fail in (0.1, 0.3):
            for seed in range(3):
                results.append(episode(n_pkgs, p_fail, seed))
                r = results[-1]
                print(f"n={r['n']} p={p_fail} seed={seed} "
                      f"runs={r['runs']} converged={r['converged']} "
                      f"g_ok={r['g_ok']}", flush=True)
    json.dump(results, open(os.path.join(out, "e4c-recovery.json"), "w"),
              indent=1)
