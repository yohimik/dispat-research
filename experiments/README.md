# dispat-experiments

Reproducible experiment tree for the CCME/dispat paper. Everything runs in
Docker from this directory; the binary under test is built inside the image
from the vendored source archive.

- Binary: `dispat exp-342062d3` (git archive of commit `342062d3`,
  `CGO_ENABLED=0`, built in `docker/Dockerfile`).
- Images: `dispat-exp:runtime` (alpine+python+git), `dispat-exp:node`
  (node:22 + the same binary) — `cd docker && docker build -t
  dispat-exp:runtime . && docker build -t dispat-exp:node --target node .`
- All generators are seeded; results carry the pinned version.

## Layout

- `shared/planjson.py` — the frozen JSON-plan extractor (gate 0); every
  consumer parses dispat output through this one file.
- `shared/realize.py` — instance JSON -> real git repository (edges are
  config-declared; units are --allow-empty commits; tags are real).
- `e1/` — differential validation: `oracle.py` (the historical
  conference-v8/CCME-1 model, one
  function per Definition), `gen.py` (profiles core/full), `golden_test.py`
  (cases lifted from the paper), `run.py` (compare + classify PG1/PG2/
  PG2x/PG3, dossier UNKNOWNs). `ccme2_vectors.py` is a separate black-box
  conformance campaign for released CCME 2.0 vectors 133--138; it does not
  reuse that old oracle.
  Run: `docker run --rm -v $PWD:/exp -w /exp dispat-exp:runtime \
        python3 e1/run.py --n 1000 --profile core --out /exp/results/e1`
- `e2/` — orphan experiment: verdaccio 6 + `failproxy.py` (502s PUTs named
  in `e2/deny/`), `fixture.py` (six-package graph, lerna and dispat
  flavours), `orphan.sh` (the protocol; phases `lerna` / `dispat`; reset
  verdaccio between phases — lesson learned twice).
- `e3a/` — historical replay: `replay.py` with profiles `gcn`
  (release-please manifest diffs as expected data; sparse worktrees;
  component names derived npm-name-minus-scope) and `cc`
  (conventional-changelog; expected data = tags pointing at each lerna
  release commit).
- `e4/` — scale (`timing.py`: cells over P/shape/U/pad) and recovery
  (`recovery.py`: real `dispat release` against a file:// origin with a
  deny-list publish script; asserts G3/G5/G6 across the sequence).
- `results/` — one JSON/CSV per run, plus dossiers for any unclassified
  divergence.

## Session results (2026-08-28)

- E1 core: 1000/1000 exact agreement. E1 full: 1093 divergent rows, all
  classified (PG1 411, PG2 234, PG2x 59, PG3 389, UNKNOWN 0).
- E2: lerna tags-before-publish + EUNCOMMIT-blocked recovery observed;
  dispat no-tag-on-failure, same-version resume, empty third plan.
  Transcripts in `results/e2/`.
- E3a, E4: see `results/e3a/*.json`, `results/e4/*`.

## Known harness gotchas (cost hours; do not rediscover)

1. `logLevel: warn` in a fixture config suppresses the JSON plan events.
2. Planner edges come from config `packages.<name>.dependencies`;
   manifests only feed `dispat compute`.
3. Plan rows come in several messages: `● changed`, `↻ catch-up`, `held`;
   held rows carry the *withheld* version (changed=false).
4. Stage scripts bind through `flow:`; a stage with no script succeeds
   vacuously (publish becomes tag-only — that is §13.10a, not a bug).
5. Script writes to manifests in the version stage are reverted between
   stages; use dispat's native `autoVersion` for npm fixtures.
6. npm needs a real token even when verdaccio permits `$all` publish:
   create one via `PUT /-/user/org.couchdb.user:<name>`; and npm-CLI
   publishes from a package cwd do not read the workspace-root `.npmrc`.
7. Never share one registry between two tools' runs.
8. blob:none clones + full checkout = hours of lazy fetches; sparse
   worktrees with `packages/*/package.json` are enough for discovery.

## Stability repetitions (same session, later)

- Golden gate: PASS again.
- E1 core, disjoint seeds 5001–5500: 500/500 exact (cumulative
  1,500/1,500 across two independent ranges).
- E1 full, seeds 5001–5500: same four classes, consistent proportions
  (PG1 193, PG2 147, PG2x 23, PG3 200), zero unclassified.
- E2 dispat orphan phase, fresh registry: identical outcomes
  (fail-no-tag / same-version resume / empty third plan).
- E4c repetition: all 12 episodes converged again in <=4 runs; exact
  trajectories differ between repetitions (concurrent executor; only
  plans are deterministic, which E1 checks), invariant spot-checks
  clean 16/24 cumulative, flags = harness log-matching.

## Telegram delivery guard

`tools/tg.py` is the ONLY permitted path to the delivery bot. It
hard-codes the owner (id 360613745, @yohimik, private), refuses any
other target before making a request (env overrides included), verifies
at runtime that the id still resolves to that username, and its watch
mode drops updates from anyone else — so even if a stranger
deliberately starts the bot, nothing is ever sent to them and their
messages are never acted on. Token via TG_BOT_TOKEN env only; never in
a file. Ad-hoc curl to the bot API is no longer allowed in this tree.

## Competitor tool pins (2026-08-30 refresh)

Latest published versions queried from registry.npmjs.org on 2026-08-30:
lerna 10.0.1, nx 23.1.2, turbo 2.10.12, release-please 17.11.2,
@changesets/cli 3.0.1. Turborepo does not version or publish; its docs
delegate both to Changesets, so the turbo phase runs turbo for
orchestration and changesets for version+publish. release-please has no
local publish step (GitHub-API-bound, delegates publishing to CI); its
executed evidence is the E3a replay on google-cloud-node, and E2 records
the delegation as a protocol property rather than mocking GitHub.

## E2 extension results (2026-08-30, latest tool versions)

Runner: `./e2/run.sh <phase>` (fresh verdaccio+failproxy per phase).
Each phase repeated twice; protocol-relevant transcript lines identical.

- lerna 10.0.1: same protocol as lerna 8 — tags at version time (before
  publish), denied cli leaves cli@1.0.1 tag orphaned, recovery blocked
  by EUNCOMMIT until manual cleanup, then from-package succeeds via
  registry query.
- nx 23.1.2 (nx release): tags at version time; transitive patch
  propagation to all five dependents (core minor -> everything else
  patch); denied cli orphans cli@1.0.1; recovery = `nx release publish`
  again, which skips already-published versions by registry query. No
  dirty-tree block (cleaner than lerna), idempotency still npm-derived.
- turbo 2.10.12 + changesets 3.0.1: turbo orchestrates (6/6 tasks) but
  neither versions nor publishes. changesets: range-gated propagation
  (core major -> out-of-range patch on cli,ui,api; theme,docs untouched
  because ui's patch stays inside ^1.0.0). Tag-after-publish like
  dispat (denied cli left NO cli tag), but recovery is a registry query
  ("5 packages are already published") and the release intent is a
  changeset file consumed at version time, so the plan is not a
  function of git history and cannot be replayed.

New gotchas:
9.  nx release needs @nx/js installed, `release.projects: ["*"]`
    explicitly, and `--yes` is mutually exclusive with `--skip-publish`.
10. changesets only recognises an npm workspace when package-lock.json
    exists at the root (manypkg detection); an empty `{}` suffices.
11. `bash -l` resets PATH and loses /opt/tools/node_modules/.bin; run
    phases with non-login shells.

## Binary provenance (2026-08-30 change)

The binary under test is no longer compiled from the vendored archive by
default. `docker/Dockerfile` takes it from the official released Docker
image (`docker.io/yohimik/dispat-alpine:$DISPAT_VERSION`, whose binary
is the published GitHub-release asset installed by the official
install.sh), selected by `BIN_STAGE=relimg` (default). `relbin` takes a
manually downloaded asset from `docker/bin/dispat`; `build` is the old
source-archive mode. All experiments pin ONE released version:

    docker build -t dispat-exp:runtime --build-arg DISPAT_VERSION=X.Y.Z .
    docker build -t dispat-exp:node --target node --build-arg DISPAT_VERSION=X.Y.Z .

Release-chain ordering observed: git tags first, GitHub release assets
later, Docker Hub images last. Experiments wait for the full chain.

## v1.4.0 campaign (2026-08-30, released binary)

Binary under test: `dispat 1.4.0 (linux_arm64)` extracted from the
official `yohimik/dispat-alpine:1.4.0` image (release commit
5e3a2337). Results under `results/v140/`. SPEC.md is byte-identical to
the previous pin, so the model and vectors carry over.

- Golden gate: PASS.
- E1 core: 1000/1000 and 500/500 (seeds 5001+) exact — 1,500/1,500.
- E2 dispat phase: identical protocol to the previous pin (no tag on
  failure, same-version resume, empty third plan), repeated twice,
  identical transcripts.
- Old-vs-new spot check: the one initially UNCLASSIFIED full-profile
  row (seed 588's p13) replays IDENTICALLY on the old binary — a
  classifier gap (cascade of a PG2 row via dispat's dueTo), not a
  behaviour change. Classifier extended with cascade resolution.

New gotchas:
12. gen.py iterated the prerelease SET while consuming RNG draws, so
    seed->instance depended on PYTHONHASHSEED (differed per process;
    batch vs single runs disagreed). Fixed with sorted(); two-process
    digest check now identical. Full-profile class proportions from
    earlier runs shifted slightly for this reason, not because the
    binary changed.
13. e1/run.py needs its --out directory to exist; it only fails at the
    final write, after the whole run.

## v1.4.0 campaign, remaining results

- E1 full (deterministic generator, cascade-aware classifier):
  1000 seeds -> 412 clean, classes PG1 409 / PG2 240 / PG2x 58 /
  PG3 390, zero unclassified; seeds 5001-5500 -> 222 clean,
  PG1 182 / PG2 135 / PG2x 23 / PG3 200, zero unclassified.
- E3a: gcn 36/42 and cc rows byte-identical to the previous campaign.
- E4b: full 8-cell grid at results/v140/e4/timing.csv; headline cells
  re-measured 5 containers each (timing-headline-5x.csv):
  100 -> 0.6s; 1k -> 2.8-6.7s; 10k -> 110-149s; chain 1k ~= layered 1k.
  Spread is host core scheduling (bimodality across containers,
  stable within one); A/B old-vs-new binary interleaved showed no
  binary slowdown.
- E4c: rep1+rep2 = 24/24 episodes converged, max 5 runs, first plans
  up to 45 packages, invariant spot-checks clean 18/24 (flags are the
  known log-matching harness issue).

Gotcha 14: run one heavy docker container at a time and expect
bimodal container-level performance on Apple-silicon Docker Desktop;
measure with multiple container repetitions, not one.

## v1.6.0 comparison campaign (2026-08-31)

Full re-run on the released 1.6.0 binary (official image, commit
f9c2acf2), identical seeds/cells; results in results/v160/ and the
comparison in results/compare-v140-v160.md. Verdict: plan-equivalent
to v1.4.0 everywhere (E1 per-seed identical on 3,000 instances, E2
protocol identical, E3a byte-identical, E4 within noise; recovery
24/24 <=4 runs). Only difference: plan rows now report the complete
propagation source set (dueTo/reason wording changed).

Gotcha 15: plan metadata (dueTo, reason strings) is release-version-
dependent even when plan semantics are frozen; classifiers and
parsers must key on structure, not phrasing.

Gotcha 16: Dispat 1.8 emits channel-only plan rows with the message
`◈ channel-only`. The old frozen extractor ignored those rows. The CCME 2
vector-136 run exposed this as a false failure; the extractor now accepts the
row kind and the CCME 2 runner cross-checks parsed releases against the final
declared count.

Gotcha 17: `e4/timing.py` used to retain every generated workspace until the
container exited and divided Linux `ru_maxrss` by 1024 twice. At the 4 GiB
campaign cap this made the 1,000-package warmup exit non-zero after the first
cell and reported zero MiB for the successful cell. It also reused the
Python parent's process-lifetime child high-water mark across cells. It now
removes each cell before generating the next and measures RSS through a fresh
parent per cell, converting Linux KiB to MiB once.

Gotcha 18: a long capped E4 run twice observed a generated commit whose parent
object could not be traversed. Background Git maintenance is one suspected
cause, so fixtures now disable `gc.auto`, but the failed fixture was removed by
the old cleanup path before it could be checked and the cause is unresolved.
Remaining cells are written to separate files before assembly so completed
evidence survives a later failure.

For long padding histories, the E4 runner uses `git commit-tree` after a small
fixture established identical commit IDs, refs, messages and log output versus
ordinary `git commit`, with both repositories passing `git fsck`. The full
fixture is also checked before any measurement.
