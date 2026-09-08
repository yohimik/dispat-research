# Dispat 1.8.0 / CCME 2.0.0 campaign

Recorded 2026-09-06 on an Apple-silicon Docker Desktop host while other test
jobs and the pre-existing `verdaccio` and `failproxy` containers remained
active. Measurement containers were capped at 2 CPUs and 4 GiB. E4 timings
are therefore contended-host observations, not clean performance comparisons.

## Provenance

- Dispat tag `services/dispat/v1.8.0`, commit
  `9a33b9282499eb1fdd7929c29e3ff37c50955f24`.
- Official image
  `docker.io/yohimik/dispat-alpine@sha256:32d6b64509d6f35830c9b9e3846060dc3d2e4840f9d2d226279d99f5fa6cff5c`.
  The observed binary reports `dispat 1.8.0 (linux_arm64)`.
- Released CCME implementation tag `pkg/ccme/v2.0.0`, commit
  `cc2883d6cb8cd0ca07a16655f64c20255fc6a1db`.
- Released CCME specification tag `specs/ccme-spec/v2.0.0`, commit
  `d3ce8ae637232908ced82efb5cda550f60ed2fdf`; `SPEC.md` SHA-256
  `f625f85a01910953cf9b837cb8d74e69b4745b5ba43e34668683db415945e4e8`.
- Experiment image IDs: runtime
  `sha256:d4a42648510d6f1f9e750c4fac1ffad03686967bfa7b3b51676e2f8e714df222`,
  node `sha256:79f81d170077d584feddac2359bdf1bdcf4b8761cb889782d6619c16edf9da2b`,
  E5 `sha256:3db6fd22b87f541015ced552641a659c8f326fa9de5f6f036f9fc2fe809c7dbd`.

## Results

- Historical E1 oracle: core 1,500/1,500 exact over seeds 1--1000 and
  5001--5500. With the corrected plan-row extractor, full seeds 1--1000 have
  356 clean instances and 1,263 classified package-row differences (PG1 572,
  PG2 240, PG2x 9, PG3? 442, UNKNOWN 0); full seeds 5001--5500 have 194 clean
  instances and 651 classified package-row differences (PG1 290, PG2 135,
  PG2x 5, PG3? 221, UNKNOWN 0). The pre-fix 500-seed result remains at the E1
  root for audit (222 clean, 540 classified rows), while its corrected rerun is
  under `e1/corrected-parser/`. Counts are package rows, so one generated
  instance may contribute several. `PG1` is the old model's channel-entry
  guard gap; `PG2` prerelease-train discharge; `PG2x` a classified cascade
  from those domains; and `PG3?` the classifier's structural heuristic for
  the known old-model bump-axis liveness gap, not a proved diagnosis for every
  row. These labels compare Dispat with the preserved conference-v8/CCME-1
  model; they are not findings against released CCME 2.0, and zero UNKNOWN
  rows does not establish general conformance. `e1/canonical-manifest.json`
  binds the four final shards to the corrected extractor hash and marks the
  preserved pre-fix shard audit-only.
- CCME 2.0 vectors 133--138: 6/6 passed. The campaign covers fresh-window
  rerun discharge, suppression-lapse widening, channel resolvability and G8,
  inherited-channel baseline drift, and per-unit self-source exclusion.
  Vector 135 observes the downward eligibility result and W208 through the
  CLI; it does not independently exercise the planner's upward-audit API.
  Each fixture, raw stdout/stderr, parsed plan, exit status, and final declared
  counts are retained under `e1/ccme2-vectors-evidence/`.
- E2 Dispat orphan recovery: two isolated repetitions both showed no refused
  tag, same-version recovery, and an empty third plan.
- E3 replay, five releases per repository: google-cloud-node 36/42 exact and
  conventional-changelog 7/64 exact, matching the established historical
  replay profile rather than asserting that historical releases followed CCME.
- E4 recovery: two repetitions, 24/24 episodes converged, maximum five runs,
  with no structural G3 or G5 errors. Published/failed/blocked log-event counts
  are diagnostic; invariant decisions use successive parsed plans.
- E4 timing has all eight valid fresh cells in `e4/timing.csv`. Earlier U1000
  and pad5000 fixtures are excluded because the retained repositories fail
  native `git fsck` with missing parent objects. The final U1000 fixture passed
  `git fsck` before measurement. The final pad5000 fixture used `commit-tree`
  generation after a small fixture proved byte-identical commit IDs, refs,
  messages and Git-log output and both forms passed `git fsck`; the measured
  full fixture also passed `git fsck`. `e4/timing-status.json` records the
  final and failed dispositions without substituting historical values.
- E5 uses the main repository's experiment scripts mounted read-only and puts
  all records in this directory. Only the three Dispat cells are fresh; the
  nine competitor cells remain the existing 1.8 release evidence and are not
  claimed as rerun here.

## Harness corrections made before final measurement

The first CCME 2 vector-136 run passed 5/6 because `shared/planjson.py`
discarded channel-only rows. After adding that explicit row kind and declared
count checks, all six passed. The first E4 timing attempt completed the
100-package cell, then failed its 1,000-package warmup under the memory cap:
the runner retained prior workspaces. `e4/timing.py` now removes each workspace
after its cell and reports Linux maximum RSS through a fresh parent per cell,
with the correct KiB-to-MiB conversion. A partial retry then exposed that the
old in-process high-water mark contaminated later cells; the final CSV was
restarted after moving each RSS sample into its own fresh parent process.
