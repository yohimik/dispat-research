# Execution runbook: E1 + E2 + E3a(2) + E4b/c

2026-08-28. Companion to EXPERIMENTS.md; this is the operational plan.
Workdir for everything: `~/Projects/dispat-experiments/` (created at start;
nothing lands inside the dispat repo except final tables/figures for the
paper). Every script is seeded; every result row carries
`{experiment, seed, dispat_commit, host, docker: yes/no, timestamp}`.

## Phase 0 - pinned environment (day 0)

- [ ] Build the binary under test from the current checkout
      (`342062d3` today): `cd services/dispat && go build -o
      ~/Projects/dispat-experiments/bin/dispat .` - the root `./dispat`
      is from Aug 16 and MUST NOT be used. Record `dispat --version` +
      commit in `bin/PINNED`.
- [ ] Layout: `bin/ shared/ e1/ e2/ e3a/ e4/ results/{e1,e2,e3a,e4}/`.
- [ ] Gate 0: hand-build one 3-package instance, run
      `dispat status --log-format json`, confirm the per-package events
      carry `package, version, bump, reason, channel`; freeze the JSON
      field extraction in `shared/planjson.py`. Everything downstream
      parses through this one file.

**User prep (once):** Docker Desktop → Resources → Memory 16 GB, Apply.
AC power. Nothing else needed until the E4 timing windows, which I will
announce (then: close GoLand/browser/Discord; I run under `caffeinate`).

## Phase 1 - E1: oracle + differential (days 1–2)

Build order:
1. `e1/oracle.py` - implements paper §4 only, one function per
   Definition/Eq with a traceability comment (`# Def 4.7 adm clause 3`).
   *Open decision D1:* strongest form is a clean-room subagent given only
   the paper text (I have read the Go code, so my own writing is
   paper-derived-with-traceability, not clean-room). Default: I write it
   with traceability; flag D1 if you want the subagent variant.
2. `e1/golden_test.py` - 10 hand-encoded cases lifted from the paper
   itself: the Table 3 run schedule, the §6.3 channel pair, the
   Eq. train table rows, the §6.1 polyglot plan. Oracle must pass all
   before anything else runs. **Gate 1.2.**
3. `shared/realize.py` - instance → real git repo:
   - packages as dirs + explicit `dependencies:` in dispat.yaml (E is
     configured, not inferred - exact control);
   - history: baseline commit, then units as `git commit --allow-empty`
     with explicit-scope CCME messages (no derived scopes in v1);
   - σ as real tags (incl. prerelease baselines) at recorded commits;
   - merge histories from v1.1 of the generator onward.
4. `e1/gen.py` - seeded instances: P∈{5..50}, layered DAG w/ fan-out
   param, U∈{5..60} units weighted realistic (70% plain, 15% caret
   forms, 5% cancel/hold, 10% channel), σ mixes (all-released,
   part-unreleased, prerelease trains).
5. `e1/run.py` - realize → oracle plan vs `dispat status` plan → diff →
   divergence dossier (seed + tarball) on mismatch. 8 workers in
   /tmp/e1-*.
6. `e1/metamorphic.py` - run-sequence simulation: F chosen by seed
   (random subsets + worst-case blocking chains), tags written for the
   published set, re-plan both sides; assert G2/G3/G5/G6 as runtime
   checks each step until the plan empties.

Volumes: **Gate 1.3** = 1,000 instances, all divergences triaged
(bug / oracle bug / paper ambiguity - each class is a paper-relevant
finding). Then 10,000 + metamorphic overnight. Budget ≈ 1 h at 8
workers; disk churn cleaned per instance.

## Phase 2 - E4b/c: scale + recovery, native (day 3, quiet machine)

Runs before E2/E3 because it shares `realize.py` and needs the quiet
window while motivation is fresh.

- `e4/gen.py` extends realize: P∈{100, 1 000, 10 000}; shapes: layered,
  chain (worst depth), star (worst fan-out), scale-free; all packages
  baselined at c0 (k=1 distinct window - then a variant with 10 distinct
  baselines for the k-axis); U via --allow-empty so commit count scales
  free of file I/O; C axis: pad with 10k no-op commits.
- **E4b timing:** `hyperfine -w2 -r10 'bin/dispat status'` per cell +
  `/usr/bin/time -l` for peak RSS. Native macOS, pinned binary, no
  Docker (virtiofs would own the numbers). Matrix ≈ 3P × 4 shapes × 2U ×
  2C ≈ 48 cells ≈ 2–3 h. Output: `results/e4/timing.csv`, fit
  time vs (P+E) and vs C; report constants, not just slopes.
- **E4c recovery:** the real executor, not a simulation of it:
  - local bare repo as `file://` origin so the release lock and pushes
    are real;
  - `publish` script = `! grep -qx "$DISPAT_PACKAGE" deny.txt` - dispat
    itself experiences the failure, blocks dependents (W194), tags only
    successes;
  - harness loop: run release → rewrite deny.txt by failure prob
    p∈{0.01, 0.1, 0.3} → rerun until plan empty;
  - record per run: plan size, published/failed/blocked, catch-up count;
    20 seeds × {n≈10,100,1000};
  - assertions: runs ≤ n (G6), versions constant across runs (G3),
    no package ever enters a later plan (G5).
  Output: `results/e4/recovery.csv` → runs-to-convergence vs (n, p)
  figure.

## Phase 3 - E2: competitors + orphan (days 4–6, Docker)

1. `e2/compose.yaml`: verdaccio (anonymous publish on), `registry:2`,
   and `failproxy` - a ~60-line Python proxy in front of verdaccio that
   502s PUTs whose package name is in `DENY` env. Toolchains in
   `node:22` containers (lerna, nx pinned versions recorded).
   **Gate 2.1:** `npm publish --ignore-scripts` lands in verdaccio
   through the proxy.
2. Substrate B (smoke): the paper's six-package fixture; scenarios
   S1 fix-leaf, S2 feat+propagation, S3 breaking, S4 mixed-commit,
   S5 prerelease. For lerna (independent+fixed), nx (independent+fixed),
   dispat (explicit `^^` equivalents): capture computed plans, compare
   against `e2/expected/*.json` - the §6 frozen-directive model computed
   by hand per scenario. Divergence from expected = our doc-reading was
   wrong = fix paper §6 (either way a result). **Gate 2.2.**
3. Orphan runs (smoke fixture first): DENY one package mid-set →
   - lerna: `version` then `publish from-git`; record tags-before-
     artefacts, then `from-package` recovery on npm;
   - nx: `release version` + `release publish`, record behaviour + any
     documented recovery;
   - dispat: same failure; assert no tag for the failed package, rerun,
     identical versions, convergence.
   Two-target variant: one npm pkg + one scratch Docker image; fail the
   image push; record that from-package has no answer for it, dispat
   resumes. **Gate 2.3.**
4. Substrate A: mirror googleapis/google-cloud-node; retarget publish at
   verdaccio (`--ignore-scripts`, so no builds needed); dispat config
   generated (spaces + `dispat compute` edges + release-please-style
   tagFormat). Orphan run at real scale (~100 packages): dispat vs
   lerna-with-injected-config. **Gate 2.4.**
5. release-please: *open decision D2* - it is GitHub-API-coupled, no
   hermetic mode. Default: executed rows only for lerna/nx/dispat;
   release-please column from documentation, marked as such. Alternative
   if you approve: scratch GitHub repo + token for live
   `release-please release-pr` runs.

## Phase 4 - E3a: replay, 2 repos (days 7–9)

Repos: **google-cloud-node** (release-please manifest = machine-readable
expected data, independent versions) + **babel** (lerna fixed mode -
deliberately the contrasting shape; exercises dispat version groups).
*Open decision D3:* swap babel → nrwl/nx (independent, nx release) if
you prefer two independent-mode repos over the fixed-mode contrast.

Per repo:
1. Full mirror clone into `e3a/repos/`.
2. `e3a/expected_<repo>.py`: gcn - walk release-PR merge commits, diff
   `.release-please-manifest.json` to get {pkg: version} per release;
   babel - `v*` tags + lerna.json. **Gate 3.1:** extractor output
   verified by hand against 2 releases' GitHub pages.
3. `e3a/config_<repo>.py`: dispat.yaml generator - spaces from layout,
   edges from `dispat compute` at that checkout, tagFormat matched to
   the repo's scheme, type map from the repo's convention, lenient
   parsing. **Gate 3.2:** ≥95% of window commits parse at the newest
   release; iterate the type map until true, log the map used.
4. Replay loop, last k=10 releases each: checkout parent of release
   commit → `dispat status` JSON → compare planned vs expected →
   classify: (i) non-CC commit, (ii) manual override, (iii) predicted
   dependent-bump semantic difference (paper §6), (iv) unexplained →
   investigate, ours or theirs. Class-(iii) hits at predicted places
   are positive results.
5. Output: `results/e3a/<repo>.csv` + agreement rates + taxonomy table.

## Phase 5 - consolidation (day 10)

- `results/*/` → three paper tables (E2 orphan outcomes, E3a agreement,
  E4 fits) + two figures (runs-to-convergence; time vs P+E). Figures get
  the dataviz pass when drawn.
- Paper edits: Evaluation gains §"Experiments" with E2/E3a/E4 (E1 folds
  into the conformance paragraph); Threats updated (single machine, two
  repos, doc-mode release-please if D2 stays default).
- Everything (scripts, seeds, raw results) committed to the repo under
  `tests/experiments/` - only when you say to commit.

## Standing rules

- One pinned binary for all experiments; rebuild = new results dir.
- Correctness runs (E1/E2/E3a): Docker or native, background apps fine.
- Timing runs (E4b): native, quiet machine, `caffeinate -dims`, AC,
  announced start/stop, medians of ≥10.
- Any divergence anywhere: dossier first (seed + repro tarball), triage
  before continuing volume runs.
- Network: only for repo mirrors and npm image pulls; all measurement
  runs offline.

## Open decisions (answer when convenient; defaults in effect)

- **D1** oracle authorship: me-with-traceability (default) vs clean-room
  subagent from paper text only.
- **D2** release-please: documentation-mode (default) vs live scratch
  GitHub repo + token.
- **D3** second E3a repo: babel fixed-mode contrast (default) vs nx
  independent.

## Addendum (2026-08-28, execution start)

- Everything runs in Docker per user instruction; E4 timing keeps hot
  paths on container-internal filesystems (never bind mounts) and adds
  one native-vs-docker calibration cell to quantify the VM offset;
  growth curves are the claim, constants reported with the caveat.
- Docker VM raised to 16 GB (settings-store.json, restart) - done.
- Phase 0 complete: workdir ~/Projects/dispat-experiments; runtime image
  `dispat-exp:runtime` built from vendored `git archive 342062d3`
  (binary stamped exp-342062d3); gate 0 passed - JSON plan extraction
  frozen in shared/planjson.py; hand instance verifies direct minor +
  propagated patches with reasons and dueTo attribution.
- Config lesson recorded: planner edges come from config
  `packages.<name>.dependencies`, manifests only feed `dispat compute`;
  realize.py will declare edges explicitly (exact control, as planned).
