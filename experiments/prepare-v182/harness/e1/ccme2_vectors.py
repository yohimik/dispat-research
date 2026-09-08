"""Black-box CCME 2.0 conformance checks for released vectors 133--138.

The expectations below are transcribed from the released specification.  The
fixtures use real repositories and tags; they do not call Dispat's Go test
helpers or planner internals.  This is separate from the historical E1 oracle,
which remains a comparison against the conference-v8/CCME-1 model.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
import planjson  # noqa: E402
import realize   # noqa: E402


def unit(kind, scope, **kw):
    return {"type": kind, "scope": scope, "pd": 0, "pcd": 0,
            "breaking": False, "pb": None, "channel": None,
            "pchannel": None, "releaseAs": None, **kw}


def instance(packages, edges, commits, tags):
    return {"packages": packages, "edges": edges, "commits": commits,
            "tags": tags, "features": {"prerelease": []}}


ARTIFACT_DIR = None


def plan(inst, label):
    work = tempfile.mkdtemp(prefix="ccme2-vector-")
    try:
        realize.realize(inst, work)
        proc = subprocess.run(["dispat", "status", "--log-format", "json"],
                              cwd=work, capture_output=True, text=True)
        lines = (proc.stdout + proc.stderr).splitlines()
        assert proc.returncode == 0, "\n".join(lines[-20:])
        events = [json.loads(x) for x in lines if x.startswith("{")]
        parsed = planjson.parse(lines)
        ready = [e for e in events if e.get("message") == "release plan ready"]
        assert len(ready) == 1, "missing or duplicate release-plan-ready event"
        assert set(parsed) <= set(inst["packages"]), "unknown parsed package"
        assert ready[0].get("packages") == len(inst["packages"]), \
            "declared package count differs from fixture"
        assert ready[0].get("releasing") == sum(
            bool(row.get("changed")) for row in parsed.values()), \
            "declared releasing count differs from parsed rows"
        normalized = {p: parsed.get(p, {"changed": False})
                      for p in inst["packages"]}
        assert set(normalized) == set(inst["packages"])
        if ARTIFACT_DIR:
            os.makedirs(ARTIFACT_DIR, exist_ok=True)
            with open(os.path.join(ARTIFACT_DIR, f"{label}-fixture.json"), "w") as f:
                json.dump(inst, f, indent=1)
            with open(os.path.join(ARTIFACT_DIR, f"{label}-stdout.jsonl"), "w") as f:
                f.write(proc.stdout)
            with open(os.path.join(ARTIFACT_DIR, f"{label}-stderr.jsonl"), "w") as f:
                f.write(proc.stderr)
            with open(os.path.join(ARTIFACT_DIR, f"{label}-parsed.json"), "w") as f:
                json.dump({"exit": proc.returncode, "plan": normalized,
                           "ready": ready[0]}, f, indent=1)
        return normalized, events
    finally:
        shutil.rmtree(work, ignore_errors=True)


def changed(rows, package):
    row = rows.get(package, {})
    return (row.get("next"), row.get("bump"), row.get("channel")) \
        if row.get("changed") else None


def has_code(events, code):
    return any(e.get("code") == code for e in events)


def main(out_path):
    global ARTIFACT_DIR
    ARTIFACT_DIR = os.path.join(os.path.dirname(out_path), "ccme2-vectors-evidence")
    base = [{"id": "c0", "units": []}]
    results = []

    def check(vector, inst, assertions):
        rows, events = plan(inst, f"vector-{vector}")
        failures = [label for label, ok in assertions(rows, events) if not ok]
        results.append({"vector": vector, "pass": not failures,
                        "failures": failures})

    # 133: a commit already carried by the prerelease baseline stays in W(P)
    # for aggregation but is absent from Wfresh(P), so a no-op rerun is empty.
    check(133, instance(["p"], [], base + [
        {"id": "c1", "units": [unit("fix", ["p"])]}], [
        {"pkg": "p", "version": "1.0.0", "commit": "c0"},
        {"pkg": "p", "version": "1.0.1-beta.0", "commit": "c1"}]),
        lambda r, e: [("p re-admitted", changed(r, "p") is None)])

    # 134: publishing a cancelled provider changes the retry source set and
    # may expose a finite consumer catch-up.
    v134_history = base + [
        {"id": "c1", "units": [unit("feat", ["core"], pd=1)]},
        {"id": "c2", "units": [unit("cancel", ["core"])]}]
    before = instance(["core", "app"], [["app", "core"]], v134_history, [
        {"pkg": "core", "version": "1.0.0", "commit": "c0"},
        {"pkg": "app", "version": "1.0.0", "commit": "c0"}])
    after = instance(["core", "app"], [["app", "core"]], v134_history, [
        {"pkg": "core", "version": "1.0.0", "commit": "c0"},
        {"pkg": "core", "version": "1.1.0", "commit": "c2"},
        {"pkg": "app", "version": "1.0.0", "commit": "c0"}])
    rb, _ = plan(before, "vector-134-before")
    check(134, after, lambda r, e: [
        ("consumer changed before provider publication", changed(rb, "app") is None),
        ("consumer catch-up absent after provider publication",
         changed(r, "app") == ("1.0.1", "patch", "stable"))])

    # 135: a provider on beta cannot create upward stale debt for an rc
    # consumer; the same resolvability rule governs downward admission.
    check(135, instance(["core", "app"], [["app", "core"]], base + [
        {"id": "c1", "units": [unit("release", ["app"], channel="rc")]},
        {"id": "c2", "units": [unit("feat", ["core"], pd=1,
                                           channel="beta")]}], [
        {"pkg": "core", "version": "1.0.0", "commit": "c0"},
        {"pkg": "app", "version": "1.0.0", "commit": "c0"},
        {"pkg": "app", "version": "1.0.1-rc.0", "commit": "c1"}]),
        lambda r, e: [("rc consumer bumped", changed(r, "app") is None),
                      ("missing W208", has_code(e, "W208"))])

    # 136: rejected bump admission cannot run backwards and erase an
    # independently admitted propagated channel.
    check(136, instance(["core", "app"], [["app", "core"]], base + [
        {"id": "c1", "units": [unit("feat", ["core"], pd=1,
                                           channel="beta", pchannel="rc",
                                           pcd=1)]}], [
        {"pkg": "core", "version": "1.0.0", "commit": "c0"},
        {"pkg": "app", "version": "1.0.0", "commit": "c0"}]),
        lambda r, e: [("channel-only rc absent",
                       changed(r, "app") == ("1.0.1-rc.0", "none", "rc")),
                      ("missing W208", has_code(e, "W208"))])

    # 137: inherited channel is recomputed from the provider baseline.  A
    # graduation between retries is explicitly outside G3's fixed-input bound.
    v137_history = base + [
        {"id": "c1", "units": [unit("release", ["core"], channel="beta")]},
        {"id": "c2", "units": [unit("fix", ["core"], pd=1,
                                           pchannel="inherit", pcd=1)]},
        {"id": "c3", "units": [unit("release", ["core"], channel="stable")]}]
    v137_tags = [{"pkg": "core", "version": "1.0.0", "commit": "c0"},
                 {"pkg": "core", "version": "1.0.1-beta.0", "commit": "c1"},
                 {"pkg": "app", "version": "1.0.0", "commit": "c0"}]
    first, _ = plan(instance(["core", "app"], [["app", "core"]],
                             v137_history, v137_tags), "vector-137-before")
    check(137, instance(["core", "app"], [["app", "core"]], v137_history,
                        v137_tags + [{"pkg": "core", "version": "1.0.1",
                                      "commit": "c3"}]), lambda r, e: [
        ("first inherited beta absent",
         changed(first, "app") == ("1.0.1-beta.0", "patch", "beta")),
        ("retry did not inherit stable",
         changed(r, "app") == ("1.0.1", "patch", "stable"))])

    # 138: self-source exclusion is per unit.  cli is excluded as a target of
    # the core unit but remains a valid target of the utils unit.
    check(138, instance(["core", "utils", "cli"],
                        [["cli", "core"], ["cli", "utils"]], base + [
        {"id": "c1", "units": [unit("fix", ["cli", "core"], pd=1),
                                  unit("fix", ["utils"], pd=1)]}], [
        {"pkg": p, "version": "1.0.0", "commit": "c0"}
        for p in ("core", "utils", "cli")]),
        lambda r, e: [("cli patch absent",
                       changed(r, "cli") == ("1.0.1", "patch", "stable")),
                      ("wrong source attribution",
                       r.get("cli", {}).get("dueTo") == ["utils"])])

    summary = {"spec": "CCME 2.0.0", "vectors": "133-138",
               "passed": sum(r["pass"] for r in results),
               "total": len(results), "results": results,
               "dispat": subprocess.run(["dispat", "--version"],
                                          capture_output=True, text=True
                                          ).stdout.strip().splitlines()[-1]}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary))
    return 0 if summary["passed"] == summary["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else
                          "/results/ccme2-vectors.json"))
