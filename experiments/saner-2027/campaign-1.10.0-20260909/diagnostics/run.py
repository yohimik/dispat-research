#!/usr/bin/env python3
"""Separate engineering checks; never part of the 14-stage scientific sample."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"
OUT.mkdir(exist_ok=False)
fixture = OUT / "fixture"
fixture.mkdir()
(fixture / "dispat.json").write_text("{")
(fixture / "settings").mkdir()
(fixture / "settings/packages/core").mkdir(parents=True)
(fixture / "settings/packages/core/placeholder").write_text("")
(fixture / "settings/dispat.yaml").write_text("packages:\n  core:\n    path: packages/core\nparser:\n  $ref: ./parser.yaml\n")
(fixture / "settings/parser.yaml").write_text("types:\n  add: minor\nstrictTypes: true\n")
(fixture / "empty-path").mkdir()
binary = "/usr/local/bin/dispat"
assert hashlib.sha256(Path(binary).read_bytes()).hexdigest() == "03d1ba5fbaef35b69582e9489f40b5438f81ae6926e02ea6d02716b5b73d92fd"
cases = [
    ("valid-no-git-ignores-nearby-config", ["feat(core): accepted"], 0, None),
    ("warning-visible-under-quiet-json", ["--quiet-parser", "--log-level", "error", "--log-format", "json", "unlisted(core): warning"], 0, "W140"),
    ("empty-literal", [""], 1, "E002"),
    ("invalid-literal", ["hello world"], 1, None),
    ("multiline-valid", ["feat(core): accepted\n\n---\nfix(api): another unit"], 0, None),
    ("multiline-invalid", ["feat(core): accepted\n\n---\nnot conventional"], 1, None),
    ("no-git-comment-cleanup", ["# comment\nfeat(core): literal"], 1, None),
    ("leading-dash-literal", ["--", "--not-a-flag"], 1, None),
    ("explicit-reference-valid", ["--config", "settings/dispat.yaml", "add(core): accepted"], 0, None),
    ("explicit-reference-strict-refusal", ["--config", "settings/dispat.yaml", "unlisted(core): refused"], 1, "E140"),
    ("missing-config", ["--config", "missing.json", "feat: accepted"], 1, None),
    ("malformed-config", ["--config", "dispat.json", "feat: accepted"], 1, None),
    ("missing-argument", [], 2, None),
    ("extra-argument", ["feat: one", "fix: two"], 2, None),
    ("invalid-command-flag", ["--tag", "feat: one"], 2, None),
    ("invalid-log-format", ["--log-format", "xml", "feat: one"], 2, None),
]
env = os.environ.copy()
env["PATH"] = str(fixture / "empty-path")
env["DISPAT_UPDATE_CHECK"] = "1"
before = {str(p.relative_to(fixture)): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in fixture.rglob("*") if p.is_file()}
rows = []
for name, args, expected_exit, code in cases:
    command = [binary, "diagnostics", *args]
    result = subprocess.run(command, cwd=fixture, env=env, capture_output=True, text=True, timeout=15)
    passed = result.returncode == expected_exit and (code is None or code in result.stdout)
    if name == "warning-visible-under-quiet-json":
        events = [json.loads(line) for line in result.stdout.splitlines()]
        passed = passed and any(e.get("code") == "W140" and e.get("level") == "warn" for e in events)
    rows.append({"name": name, "argv": command, "expected_exit": expected_exit,
                 "expected_code": code, "exit": result.returncode,
                 "stdout": result.stdout, "stderr": result.stderr, "passed": passed})
    (OUT / "observations.json").write_text(json.dumps(rows, indent=2) + "\n")
after = {str(p.relative_to(fixture)): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in fixture.rglob("*") if p.is_file()}
unchanged = before == after and not (fixture / ".git").exists()
report = {"status": "PASS" if all(r["passed"] for r in rows) and unchanged else "FAIL",
          "cases": len(rows), "passed_cases": sum(r["passed"] for r in rows),
          "fixture_unchanged": unchanged,
          "scope": "Purpose-selected diagnostics engineering checks, no Git on PATH, no repository, network disabled by container. Not independent scientific samples or proof of absent internal operations."}
(OUT / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["status"] == "PASS" else 1)
