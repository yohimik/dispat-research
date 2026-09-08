#!/usr/bin/env python3
"""Validate and summarize the completed Dispat 1.8.2 experiment campaign."""

import argparse
import collections
import csv
import hashlib
import json
import sys
from pathlib import Path


STAGES = ("provenance", "images", "e1", "e2", "e3", "e4", "e5", "finalize")
SHARDS = (("core", 1, 1000), ("core", 5001, 500),
          ("full", 1, 1000), ("full", 5001, 500))


def fail(message):
    raise SystemExit(f"REFUSED: {message}")


def load(path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        fail(f"cannot read valid JSON {path}: {e}")


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def validate_campaign(root):
    identity = root / "campaign.identity"
    if not identity.is_file():
        fail(f"missing campaign identity: {identity}")
    identity_bytes = identity.read_bytes()
    missing = []
    bad = []
    for stage in STAGES:
        marker = root / ".complete" / stage
        if not marker.is_file():
            missing.append(stage)
        elif marker.read_bytes() != identity_bytes:
            bad.append(stage)
    if missing or bad:
        fail("campaign is incomplete or mixed; "
             f"missing markers={missing}, identity-mismatched markers={bad}")

    final_identity = root / "finalize" / "campaign.identity"
    if not final_identity.is_file() or final_identity.read_bytes() != identity_bytes:
        fail("finalize/campaign.identity is missing or differs from campaign.identity")
    manifest = root / "finalize" / "SHA256SUMS"
    if not manifest.is_file():
        fail("missing finalize/SHA256SUMS")
    checked = 0
    for lineno, line in enumerate(manifest.read_text().splitlines(), 1):
        try:
            expected, raw_path = line.split(None, 1)
        except ValueError:
            fail(f"malformed SHA256SUMS line {lineno}")
        path = Path(raw_path.strip())
        if not path.is_file():
            fail(f"manifest member is missing: {path}")
        actual = digest(path)
        if actual != expected:
            fail(f"manifest hash mismatch: {path} expected {expected}, got {actual}")
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError:
            fail(f"manifest member escapes result root: {path}")
        checked += 1
    if not checked:
        fail("final manifest is empty")
    fields = dict(line.split("=", 1) for line in identity.read_text().splitlines()
                  if "=" in line)
    if fields.get("version") != "1.8.2":
        fail(f"identity version is {fields.get('version')!r}, expected '1.8.2'")
    return fields, checked


def e1_summary(root):
    totals = collections.Counter()
    classes = collections.Counter()
    shards = []
    rows_by_seed = {}
    for profile, first, count in SHARDS:
        path = root / "e1" / f"{profile}-{first}-{count}" / f"e1-{profile}-{first}-{count}.json"
        data = load(path)
        summary, rows = data.get("summary", {}), data.get("rows", [])
        if summary.get("profile") != profile or summary.get("instances") != count:
            fail(f"E1 shard metadata mismatch: {path}")
        if len(rows) != count or [rows[0].get("seed"), rows[-1].get("seed")] != [first, first + count - 1]:
            fail(f"E1 seed coverage mismatch: {path}")
        invalid = sum(bool(row.get("invalid")) for row in rows)
        rejected = sum(bool(row.get("rejection")) for row in rows)
        malformed_rejections = []
        for row in rows:
            rejection = row.get("rejection")
            if not rejection:
                continue
            evidence = path.parent / str(rejection.get("evidence", ""))
            evidence_file = evidence / "rejection.json"
            evidence_data = load(evidence_file) if evidence_file.is_file() else {}
            if (profile != "full" or row.get("invalid")
                    or rejection.get("code") != "E195"
                    or rejection.get("returncode") != 1
                    or not evidence.is_dir()
                    or not evidence_file.is_file()
                    or evidence_data.get("seed") != row.get("seed")
                    or evidence_data.get("kind") != "semantic-rejection"
                    or evidence_data.get("code") != "E195"
                    or evidence_data.get("returncode") != 1
                    or not isinstance(evidence_data.get("stdout"), str)
                    or not isinstance(evidence_data.get("stderr"), str)):
                malformed_rejections.append(row)
        if malformed_rejections:
            fail(f"E1 has malformed or non-full-profile rejection rows: {path}")
        row_classes = collections.Counter(c for row in rows for _, c in row.get("diffs", []))
        # The frozen runner's `clean` is the legacy oracle-comparison count: a
        # validated E195 refusal with no diagnostic diff is included. Keep that
        # meaning visible, and derive the accepted subset separately.
        diagnostic_clean = sum(not row.get("invalid") and not row.get("diffs")
                               for row in rows)
        accepted_clean = sum(not row.get("invalid") and not row.get("rejection")
                             and not row.get("diffs") for row in rows)
        if (invalid != summary.get("invalid", 0)
                or rejected != summary.get("rejected", 0)
                or diagnostic_clean != summary.get("clean")
                or dict(row_classes) != summary.get("divergence_classes", {})):
            fail(f"E1 recomputed summary mismatch: {path}")
        totals.update(instances=count, diagnostic_clean=diagnostic_clean,
                      accepted_clean=accepted_clean, invalid=invalid,
                      rejected_diagnostic_plans=rejected)
        classes.update(row_classes)
        shards.append({"profile": profile, "first": first, "count": count,
                       "diagnostic_clean": diagnostic_clean,
                       "accepted_clean": accepted_clean, "invalid": invalid,
                       "rejected_diagnostic_plans": rejected,
                       "classes": dict(sorted(row_classes.items()))})
        for row in rows:
            rows_by_seed[(profile, row["seed"])] = {
                "packages": row.get("packages"),
                "invalid": bool(row.get("invalid")),
                "rejection": ({"code": row["rejection"].get("code"),
                               "returncode": row["rejection"].get("returncode")}
                              if row.get("rejection") else None),
                "diffs": row.get("diffs", [])}
    return dict(totals), dict(sorted(classes.items())), shards, rows_by_seed


def compare_e1(current_rows, old_root):
    _, _, _, old_rows = e1_summary(old_root)
    keys = sorted(set(current_rows) | set(old_rows))
    changed = [k for k in keys if current_rows.get(k) != old_rows.get(k)]
    return changed


def validate_e2(root):
    out = []
    expected = {"passed": True, "failed_publish_untagged": True,
                "same_version_recovery": True, "final_releasing": 0}
    for rep in ("dispat-rep1", "dispat-rep2"):
        path = root / "e2" / rep / "verdict.json"
        verdict = load(path)
        if verdict != expected:
            fail(f"E2 verdict failed or changed schema: {path}: {verdict}")
        out.append({"repetition": rep, **verdict})
    return out


def validate_e3(root, old_root):
    out = {}
    for profile in ("gcn", "cc"):
        cur, old = load(root / "e3" / f"{profile}.json"), load(old_root / "e3" / f"{profile}.json")
        if len(cur) != 5 or len(old) != 5:
            fail(f"E3 {profile} does not contain exactly five releases")
        rows = []
        for i, (a, b) in enumerate(zip(cur, old)):
            sha_matches = str(a.get("sha", ""))[:10] == str(b.get("sha", ""))[:10]
            av, bv = dict(a), dict(b)
            av.pop("sha", None); bv.pop("sha", None)
            rows.append({"index": i, "sha": a.get("sha"),
                         "historical_sha_matches_v181_prefix": sha_matches,
                         "metrics_equal_v181": av == bv})
        out[profile] = rows
    return out


def validate_e4(root):
    reps = []
    for rep in ("rep1", "rep2"):
        rows = load(root / "e4" / rep / "e4c-recovery.json")
        if len(rows) != 12:
            fail(f"E4 {rep} contains {len(rows)} episodes, expected 12")
        bad = [r for r in rows if not r.get("converged") or not r.get("g_ok")]
        if bad:
            fail(f"E4 {rep} contains failed recovery episodes")
        reps.append({"repetition": rep, "episodes": len(rows),
                     "total_runs": sum(r["runs"] for r in rows),
                     "max_runs": max(r["runs"] for r in rows)})
    cells = sorted((root / "e4" / "cells").glob("*.csv"))
    if [p.stem for p in cells] != [str(i) for i in range(8)]:
        fail("E4 timing cells are not exactly 0..7")
    timing = list(csv.DictReader((root / "e4" / "timing.csv").open()))
    if len(timing) != 8:
        fail(f"E4 combined timing has {len(timing)} rows, expected 8")
    for i, path in enumerate(cells):
        rows = list(csv.DictReader(path.open()))
        if len(rows) != 1 or rows[0] != timing[i]:
            fail(f"E4 timing cell {i} does not match combined timing row")
    return reps, timing


def validate_e5(root):
    paths = sorted((root / "e5").glob("*/verdict.json"))
    expected = {("orphan", ""), ("midrelease", "clean"),
                ("midrelease", "conflict")}
    got = set()
    rows = []
    for path in paths:
        d = load(path)
        key = (d.get("experiment"), d.get("scenario", ""))
        got.add(key)
        if d.get("tool") != "dispat" or d.get("passed") is not True or not all(c.get("ok") for c in d.get("checks", [])):
            fail(f"E5 failed verdict: {path}")
        rows.append({"experiment": key[0], "scenario": key[1],
                     "checks": len(d["checks"]), "passed": True})
    if len(paths) != 3 or got != expected:
        fail(f"E5 verdict set mismatch: got {sorted(got)}, expected {sorted(expected)}")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=Path("/Users/yohimik/Projects/dispat-experiments/results/v182-20260907"))
    ap.add_argument("--baseline", type=Path, default=Path("/Users/yohimik/Projects/dispat-experiments/results/v181-20260907"))
    args = ap.parse_args()
    identity, hashes = validate_campaign(args.results)
    totals, classes, shards, current_rows = e1_summary(args.results)
    changed = compare_e1(current_rows, args.baseline)
    vectors = load(args.results / "e1" / "ccme2-vectors.json")
    if vectors.get("passed") != 6 or vectors.get("total") != 6 or not all(r.get("pass") for r in vectors.get("results", [])):
        fail("CCME 2 vectors 133-138 did not all pass")
    report = {
        "campaign": {"version": identity["version"], "tag": identity.get("tag"),
                     "commit": identity.get("commit"), "image": identity.get("image"),
                     "verified_manifest_files": hashes},
        "E1": {"totals": totals, "divergence_classes": classes,
               "shards": shards, "normalized_changes_from_v181":
               [{"profile": p, "seed": s} for p, s in changed],
               "comparison_note": "Version strings and campaign metadata are excluded. Package counts, invalid status, E195 diagnostic-refusal status, and diagnostic-plan diffs are compared. Rejected full-profile rows are diagnostic comparisons only; they are not releasable plans or conformance results."},
        "CCME2": {"spec": vectors.get("spec"), "vectors": vectors.get("vectors"),
                  "passed": vectors.get("passed"), "total": vectors.get("total")},
        "E2": validate_e2(args.results),
        "E3": validate_e3(args.results, args.baseline),
        "E4": {}, "E5": validate_e5(args.results),
        "limits": [
            "E1 PG labels compare against the preserved conference-v8/CCME-1 oracle; they are not CCME 2 conformance claims.",
            "E1 full-profile E195 rows contain validated diagnostic plans from intentionally unreleasable generated histories; they are counted as rejected diagnostic comparisons, not successful release plans, invalid infrastructure samples, or conformance results.",
            "E3 replays historical releases and does not claim those releases followed CCME.",
            "E4 timings are host-sensitive and are not a controlled cross-version benchmark.",
            "The nine competitor E5 cells remain historical evidence; this campaign freshly runs exactly three Dispat E5 cells."],
        "harness_changes": [
            "E1 validates Git fixtures before planning, records invalid infrastructure samples separately, and recognizes only strictly validated E195 refusals as rejected full-profile diagnostic comparisons.",
            "E2 propagates container failures and emits an asserted verdict for each repetition.",
            "E3 checks Git and Dispat exits, requires five rows, and records full historical SHAs.",
            "E4 checks command exits and fails on nonconvergence or invariant violations."]}
    recoveries, timing = validate_e4(args.results)
    report["E4"] = {"recovery": recoveries, "timing_cells": timing}
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
