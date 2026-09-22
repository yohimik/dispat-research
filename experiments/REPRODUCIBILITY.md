# Reproducibility audit of the retained experiments

Audit date: 22 September 2026. Auditor: a research session working only inside this repository. Nothing under `experiments/` that existed before the audit was modified, moved or deleted; every command ran into the new directory `experiments/results/repro-20260922/` and every new helper lives under `experiments/tools/`.

The question answered here is narrow: can a stranger with Docker, the network and a checkout of this repository rerun each retained experiment family, and does the retained evidence still verify. The answer is given per family with the pins, the exact commands, the fresh-machine limits, the verification step and one of three statuses:

- **EXACT**: the byte-identical environment (runner image by immutable ID, binary by SHA-256) is available and the check ran in it.
- **RECIPE**: the environment is rebuildable from retained pins (digests, package locks, hashes); a rebuild gives a different image ID and possibly different auxiliary package versions, while the binary under test stays byte-identical.
- **HISTORICAL**: the environment is gone or was never pinned tightly enough to rebuild; only the evidence remains.

Two statuses are given where they differ: one for the machine that measured the campaigns (this Apple silicon host, whose Docker store still holds every locked runner image, see `results/repro-20260922/environment/pinned-images-present.log`) and one for a fresh machine.

## How the audit recorded itself

Every executed step went through `tools/repro-step.py`, which writes `STEP.log` (the command's combined output, preceded by one comment line with the argv, working directory and start time) and appends one JSON line to `steps.jsonl` in the family directory. The per-family tables below are transcribed from those ledgers; `exit` is the process exit status and `expected` says whether that status was the one the step was allowed to return. Raw outputs, verifier reports and comparison inputs are beside the logs.

Helper scripts added by this audit (all new, none replaces an existing script):

| Script | Purpose |
|---|---|
| `experiments/tools/repro-step.py` | Runs one command, tees its output to `FAMILY/STEP.log`, appends the ledger line. Refuses to overwrite a log. |
| `experiments/tools/check-manifest.py` | Checks a retained checksum manifest (JSON maps as in `SHA256SUMS.json` and `FREEZE.json`, or `sha256sum` text) against files under a chosen root, with `--strip-prefix` for manifests written with historical absolute paths. Reads only; the optional report is created exclusively. |
| `experiments/tools/verify-saner-archive-to.py` | `tools/verify-saner-archive.py` with the report directory as an argument, so a run that already carries `archive-verification/` can be rechecked without touching it. Same four verifiers, same Docker command, `--runner-image` to substitute a rebuilt runner (recorded in the report). |
| `experiments/tools/verify-mechanisms-run-copy.py` | The mechanism campaign's "audit `full-01` from its archive" procedure as one command: copies the run, checks and extracts `expanded-fixtures.tar.gz`, rechecks every extracted file against `archive-verification.json`, runs the campaign's `verify.py` in Docker, writes `report.json` and `verifier.json` to a new directory. |
| `experiments/tools/restore-one-replay-fixture.py` | `tools/restore-replay-fixtures.py` for a single lock into a caller-chosen directory, so one replay repository can be restored for a small E3a rerun without restoring all three into `experiments/e3a/repos/`. |

Reproduction outputs: `experiments/results/repro-20260922/<family>/`. Git metadata created by the fresh integration-fixture reruns was moved into `results/repro-20260922/nested-git-20260922.tar.gz` (listed in `nested-git-20260922.json`) so the results tree contains no embedded repositories, following what `provenance/generated-fixture-git.tar.gz` does for the retained campaigns. Copies of retained evidence that the verifiers needed beside their inputs were removed after verification; the reports say what was copied and what was checked.

## Environment of this audit

Recorded in `results/repro-20260922/environment/`: Docker Desktop 4.82.0, engine 29.6.1 on linux/arm64 (`docker-version.log`, `docker-info.log`); macOS 27.0 on arm64, host Python 3.9.6, git 2.54.0, buildx v0.35.0 (`host.log`); research repository HEAD `e62ca30` (`research-git-head.log`). `pinned-images-present.log` shows that every locked runner and experiment image referenced by the campaigns below still exists locally by ID. `published-image-tags-resolve.log` records, for every released tag from 1.4.0 to 1.10.0, the index digest and per-platform manifest digests that `docker.io/yohimik/dispat-alpine` served on 22 September; the digests for 1.8.0, 1.8.1, 1.8.2, 1.9.0 and 1.10.0 equal the digests the campaigns recorded.

`verify-migration-snapshot.log`: `tools/verify-migration.py` reports 103 changed or missing files, all under `paper/` and `output/` except `experiments/README.md`, which gained its 22 September section. This is the expected result: the migration snapshot describes the 9 September import and the manuscript, review outputs and page previews changed or were removed afterwards (`provenance/cleanup-2026-09-10.json`). No campaign evidence file is in that list.

## Family A. Historical E1 to E5 on the vendored source archive (binary `exp-342062d3`)

**What and where.** The first differential campaign of 28 August 2026, described in `experiments/README.md` ("Session results (2026-08-28)" and "Stability repetitions"). E1 core 1,000/1,000 and 500/500 exact, E1 full classified rows, E2 orphan transcripts, E3a replays, E4 timing and recovery. Evidence: `experiments/results/e1/e1-core-1-1000.json`, `e1-core-5001-500.json`, `e1-full-1-1000.json`, `e1-full-5001-500.json`; `results/e2/*.log`, `results/e2/transcript*.txt`; `results/e3a/gcn.json`, `results/e3a/cc.json`; `results/e4/timing.csv`, `results/e4/e4c-recovery.json` (and the stray copy `experiments/--help/e4c-recovery.json` of 6 September).

**Pins.** Source: `experiments/docker/src/` is `git archive 342062d3` of github.com/yohimik/dispat (`experiments/bin/PINNED`, `experiments/docker/Dockerfile` header). Build: `docker/Dockerfile` stage `build`, `CGO_ENABLED=0`, `-ldflags "-X ...cli.Version=exp-342062d3"`, base `golang:${GO_VERSION}-alpine` with `GO_VERSION=1.26` (mutable tag). Runtime base `python:3.12-alpine` plus unpinned `apk add git bash hyperfine coreutils`; node image `node:22-slim` plus competitor tools pinned by version (`lerna@10.0.1 nx@23.1.2 @nx/js@23.1.2 turbo@2.10.12 @changesets/cli@3.0.1`). Seeds: E1 core and full 1 to 1000 and 5001 to 5500; E4 timing seed 42 (`e4/timing.py`); E4 recovery seeds 0 to 2 per (n, p) cell (`e4/recovery.py`). Result files carry the version label `exp-342062d3` in `summary.dispat` but no binary SHA-256 and no image ID (`results/e1/e1-core-1-1000.json`). The E1 generator of that campaign predates the `PYTHONHASHSEED` fix (`experiments/README.md`, gotcha 12), so the seed-to-instance mapping of the retained files is the one produced by the current `e1/gen.py` only where the fix did not change it; the 50-seed check below shows the core rows are unchanged for seeds 1 to 50.

**Rerun into a new directory** (from `experiments/`, `OUT` an absolute path that does not exist):

```sh
docker build -t dispat-exp:srcbuild --target runtime --build-arg BIN_STAGE=build docker
docker build -t dispat-exp:srcbuild-node --target node --build-arg BIN_STAGE=build docker
mkdir -p "$OUT/e1"
docker run --rm --network none --cpus 2 --memory 4g -v "$PWD:/exp:ro" -w /exp dispat-exp:srcbuild sh e1/gate0.sh
docker run --rm --network none --cpus 2 --memory 4g -v "$PWD:/exp:ro" -w /exp dispat-exp:srcbuild python3 e1/golden_test.py
docker run --rm --network none --cpus 2 --memory 4g -v "$PWD:/exp:ro" -v "$OUT/e1:/results" -w /exp dispat-exp:srcbuild \
  python3 e1/run.py --profile core --seed0 1 --n 1000 --workers 2 --out /results/core-1-1000
DISPAT_EXPERIMENT_IMAGE=dispat-exp:srcbuild-node ./e2/run.sh dispat "$OUT/e2-dispat"
docker run --rm --network none --cpus 2 --memory 4g -v "$PWD:/exp:ro" -v "$OUT:/results" -w /exp dispat-exp:srcbuild python3 e4/timing.py 0,1
docker run --rm --network none --cpus 2 --memory 4g -v "$PWD:/exp:ro" -v "$OUT/e4:/results" -w /exp dispat-exp:srcbuild python3 e4/recovery.py /results
```

`e1/run.py` accepts `--n`, `--seed0`, `--profile`, `--out`, `--workers` and creates `--out` itself; `e2/run.sh` takes `PHASE [OUTDIR]` and `DISPAT_EXPERIMENT_IMAGE`; `e4/timing.py` takes an optional comma-separated list of cell indexes 0 to 7 and prints CSV on stdout; `e4/recovery.py` takes the output directory as its only argument. E3a is Family H.

**Fresh machine.** The source archive builds today: two builds (`build-runtime-from-vendored-source.log`, cached, and `build-runtime-from-vendored-source-nocache.log`, `--no-cache`, 18 module downloads) both produced a binary reporting `dispat exp-342062d3 (linux_arm64)` with SHA-256 `2d33ac7d7e2dad15178e3bec2a550a3eb033442b8431a16ffff69cda481084aa` (`inspect-runtime-from-vendored-source-nocache.log`), built with `golang:1.26-alpine` at `sha256:c20c649e9cedf9434017488cc805c5986f11dd542460aad982ade13cdc377873`. Whether that equals the August binary cannot be known: no hash was recorded then. `--no-cache` does not clear BuildKit `--mount=type=cache` module and build caches, so a first build elsewhere downloads more. The three base tags are mutable and `apk add` is unpinned, so the image ID and auxiliary tool versions differ per rebuild.

**Verification.** No manifest covers `results/e1`, `e2`, `e3a`, `e4`; the row-level comparison in the table below is the check.

**Status.** RECIPE for the binary (rebuilt from the archive, deterministic across two builds today), HISTORICAL for the image and toolchain identity (never recorded). Plan-level outcomes reproduce exactly on the checked seeds.

| Step (`results/repro-20260922/historical-e1-e5/`) | exit | expected | Result |
|---|---|---|---|
| `build-runtime-from-vendored-source` | 0 | yes | cached build, image `f90e395c…` |
| `build-runtime-from-vendored-source-nocache` | 0 | yes | 8.3 s, image `f1629765…`, binary `2d33ac7d…`, same hash as the cached build |
| `inspect-runtime-from-vendored-source-nocache` | 0 | yes | `dispat exp-342062d3 (linux_arm64)` |
| `golden-gate-vendored-source-binary` | 0 | yes | `golden: PASS` |
| `parser-gate0-root-harness`, `golden-gate-root-harness` (1.8.2 runtime, root harness) | 0 | yes | plan events parse; `golden: PASS` |
| `e1-core-1-50-vendored-source-binary` | 0 | yes | 50/50 clean; rows for seeds 1 to 50 identical to `results/e1/e1-core-1-1000.json` and to `results/v140/e1-core/e1-core-1-1000.json` (`e1-srcbuild/core-1-50/e1-core-1-50.json`) |
| `nested-git-archive-sha256` | 0 | yes | `provenance/generated-fixture-git.tar.gz` = `12a70790…`, as `provenance/migration.json` records |

## Family B. Released-image campaigns 1.4.0 to 1.8.1

**What and where.** The same E1 to E5 protocol rerun on each released binary: `results/v140/` (1.4.0, 30 August), `results/v160/` (1.6.0, 31 August, comparison in `results/compare-v140-v160.md`), `results/v170/` (1.7.0, `v170/compare-v160-v170.md`, E5 cells for 1.6.0 and 1.7.0), `results/v172/` (1.7.2, `v172/campaign.log`, `v172/campaign-e3a-e4.log`, `v172/compare-v170-v172.md`), `results/v180-20260906/` (1.8.0 and CCME 2.0.0, `README.md`, `provenance.json`, `SHA256SUMS`, `e4/timing-status.json`), `results/v181-20260907/` (1.8.1, run by `prepare-v181/campaign.sh`; `campaign.identity`, `provenance/`, `images/`, `finalize/SHA256SUMS`) with the seed-580 follow-ups `results/v181-20260907-seed580-review/` and `results/v181-20260907-seed580-harness-fix/`.

**Pins.** 1.4.0 to 1.7.2: the mutable tag `docker.io/yohimik/dispat-alpine:X.Y.Z` (`docker/Dockerfile`, `BIN_STAGE=relimg`), release commits `5e3a2337` (1.4.0) and `f9c2acf2` (1.6.0) named in `results/compare-v140-v160.md`, local image IDs only in `v172/campaign.log` (`ebfce5d8…` runtime, `33c8dd58…` node); no digest and no binary hash recorded. 1.8.0: image index `sha256:32d6b64509d6f35830c9b9e3846060dc3d2e4840f9d2d226279d99f5fa6cff5c`, tag commit `9a33b928…`, CCME 2.0.0 commits and `SPEC.md` SHA-256, experiment image IDs `d4a42648…`, `79f81d17…`, `3db6fd22…` (`v180-20260906/provenance.json`). 1.8.1: image `yohimik/dispat-alpine@sha256:0096da187ec55d8079eb28778975381ae3ad54c8c76a77542afea65e41531fe9`, commit `3b8f2793…`, binary `7b78c0d809cbc1c6218b65a7884028e95e5d479df54378edcaf47810f0366637`, harness hash `4015c4d3…`, fixture heads `54e244b4…` (google-cloud-node) and `340ad83e…` (conventional-changelog), image IDs `da722d8c…`, `52870cf6…`, `b6fcf6d9…` (`v181-20260907/campaign.identity`, `provenance/binary-sha256.txt`, `images/image-ids.sh`). Seeds as in Family A.

**Rerun into a new directory.** For 1.4.0 to 1.8.0 use the Family A commands with `--build-arg DISPAT_VERSION=X.Y.Z` (or `X.Y.Z@sha256:INDEX_DIGEST` to pin) instead of `BIN_STAGE=build`. For 1.8.1 the campaign script is retained: from `experiments/`,

```sh
DISPAT_RELEASE_COMMIT=3b8f2793e728e180db4e0700b050850d24c37482 \
  ./prepare-v181/campaign.sh --released --out results/v181-YYYYMMDD-NAME
```

`campaign.sh` accepts only `--released`, `--out` and `--stage`; the output must be a direct child of `results/` matching `^v181-[0-9]{8}(-[A-Za-z0-9._-]+)?$`; it requires `DISPAT_SOURCE_REPO` (default `/Users/yohimik/Projects/dispat`) to be a clone of github.com/yohimik/dispat whose `origin` serves the tag `services/dispat/v1.8.1`, `rg` on the host, the three replay repositories restored under `experiments/e3a/repos/` at the locked heads, and it resolves the tag to a digest itself. Note that `prepare-v181/campaign.sh` hashes the root harness (`e1`, `e2`, `e3a/replay.py`, `e4`, `shared`, `docker/Dockerfile`), which has changed since (`e1/run.py`, `e2/orphan.sh`, `e2/run.sh`, `e3a/replay.py`, `e4/recovery.py` differ from `prepare-v182/harness/`), so a new v181 run records a different `harness=` line than `results/v181-20260907/campaign.identity`.

**Fresh machine.** All nine release tags still resolve on Docker Hub (`environment/published-image-tags-resolve.log`), and for 1.8.0 and 1.8.1 the served index digests equal the recorded ones. For 1.4.0 to 1.7.2 nothing recorded at campaign time can be compared with the digest served today, so byte identity of those binaries rests on the tags not having been re-pushed. The experiment images cannot be rebuilt byte-identically (mutable bases, unpinned `apk add`, unpinned `apt-get`); the released binary inside them is what the digest pins. The 1.8.1 campaign also needs the product repository clone and a full restore of `google-cloud-node` (4,955 locked tags) and `conventional-changelog`.

**Verification.** `results/v180-20260906/SHA256SUMS` (8,131 entries, paths relative to `experiments/`) and `results/v181-20260907/finalize/SHA256SUMS` (216 entries, historical absolute paths under `/Users/yohimik/Projects/dispat-experiments/`):

```sh
python3 experiments/tools/check-manifest.py experiments/results/v181-20260907/finalize/SHA256SUMS \
  --root experiments/results/v181-20260907 --strip-prefix /Users/yohimik/Projects/dispat-experiments/results/v181-20260907
python3 experiments/tools/check-manifest.py experiments/results/v180-20260906/SHA256SUMS --root experiments
```

The v180 manifest lists 5,884 files under nested `.git` directories that the migration moved into `provenance/generated-fixture-git.tar.gz` (`RESTORATION.md`); they verify against an extraction of that archive with `--root EXTRACTION/experiments`.

**Status.** RECIPE for 1.8.0 and 1.8.1 (digest-pinned binary, local-only image IDs). RECIPE by tag only for 1.4.0 to 1.7.2, HISTORICAL if the tags are ever moved.

| Step (`results/repro-20260922/historical-e1-e5/`) | exit | expected | Result |
|---|---|---|---|
| `check-v181-finalize-SHA256SUMS` | 0 | yes | 216/216 match after prefix relocation |
| `check-v180-SHA256SUMS` | 1 | no | 2,247/8,131 match in the tree, 0 mismatched, 5,884 missing: all nested `.git` entries |
| `check-v180-SHA256SUMS-against-nested-git-archive` | 1 | yes | the 5,884 missing entries all match inside `provenance/generated-fixture-git.tar.gz`; 0 unaccounted (`check-v180-SHA256SUMS-nested-git-archive-2.json`) |
| `environment/published-image-tags-resolve` | 0 | yes | 1.4.0, 1.6.0, 1.7.0, 1.7.2, 1.8.0, 1.8.1 resolve; 1.8.0 and 1.8.1 digests equal the recorded ones |

## Family C. The 1.8.2 campaign of 7 September

**What and where.** The last complete E1 to E5 campaign, run by `prepare-v182/campaign.sh` with the frozen harness snapshot `prepare-v182/harness/`. Evidence: `results/v182-20260907/` (`README.md`, `campaign.identity`, `provenance/`, `images/`, `e1/` with `canonical-manifest.json`, `ccme2-vectors.json`, `ccme2-vectors-evidence/`, four shards and `rejections-full/`; `e2/dispat-rep1`, `e2/dispat-rep2`; `e3/gcn.json`, `e3/cc.json`; `e4/timing.csv`, `e4/cells/`, `e4/rep1`, `e4/rep2`, `e4/fixture/`; `e5/orphan-dispat`, `e5/midrelease-clean-dispat`, `e5/midrelease-conflict-dispat`; `finalize/SHA256SUMS`). The stopped first attempt: `results/v182-20260907-attempt1/` with its own `harness-snapshot/`. Interpretation: `output/experiments-v182-state.md`, `output/experiments-v182-summary.json`, `output/experiments-v182-guard-check.txt`, `output/summarize-v182-experiments.py`; campaign logs `output/experiments-v182-campaign.log` and `output/experiments-v182-campaign-rerun.log`.

**Pins** (`results/v182-20260907/campaign.identity` and `provenance/`): `dispat 1.8.2 (linux_arm64)`, tag `services/dispat/v1.8.2` at `a7011cbcb9e88e52e7336f6fc8f1b207a8e7a311`, image `yohimik/dispat-alpine@sha256:4c0ad4b8268dd10dbb136008798c1b07ffc1c0c7c534b8465a9f5edcab0e7bfd` (the index; its linux/arm64 manifest is `sha256:1f29b870…` per today's inspection), binary SHA-256 `78b0b37b4b74ed393f366ff4d36a98aa69a48fa781cc6a704ad17a0160107a68` equal to the GitHub asset `dispat-linux-arm64` (`provenance/github-release.json`), harness hash `f5b18dda1e2ce52b8766882ddb8eb69f5d91e15ed87ddc5524caa4ae1b6774be` over `prepare-v182/`, fixture heads `54e244b4…` and `340ad83e…`, image IDs runtime `sha256:6344948a97b83fd26dc35cf47d7858453fdf8e700ee7ece4f66e5ae3cefe1a75`, node `sha256:d061baca…`, E5 `sha256:6748c967…` (`images/image-ids.sh`), extractor `shared/planjson.py` SHA-256 `3d5eef3e…` (`e1/canonical-manifest.json`). Seeds: core and full 1 to 1000 and 5001 to 5500, CCME 2 vectors 133 to 138, E4 timing seed 42, E4 recovery seeds 0 to 2 per cell, E2 two repetitions.

**Rerun into a new directory.** The whole campaign, from `experiments/`:

```sh
DISPAT_RELEASE_COMMIT=a7011cbcb9e88e52e7336f6fc8f1b207a8e7a311 \
  ./prepare-v182/campaign.sh --released --out results/v182-YYYYMMDD-NAME
```

Same argument rules as `prepare-v181/campaign.sh` (Family B), plus `gh release view services/dispat/v1.8.2 --repo yohimik/dispat` in the provenance stage (an authenticated `gh`), and it hashes `prepare-v182/` as a whole, so any new file under that directory changes the identity line. Single experiments, as executed in this audit, from `experiments/` with `H=$PWD/prepare-v182/harness`:

```sh
docker build -t dispat-exp:v182-rt --target runtime \
  --build-arg 'DISPAT_VERSION=1.8.2@sha256:4c0ad4b8268dd10dbb136008798c1b07ffc1c0c7c534b8465a9f5edcab0e7bfd' docker
docker run --rm --network none --cpus 2 --memory 4g -v "$H:/exp:ro" -w /exp dispat-exp:v182-rt python3 e1/golden_test.py
docker run --rm --network none --cpus 2 --memory 4g --tmpfs /workspaces:rw,size=1g -e TMPDIR=/workspaces \
  -v "$H:/exp:ro" -v "$OUT/e1:/results" -w /exp dispat-exp:v182-rt \
  python3 e1/run.py --profile core --seed0 1 --n 50 --workers 2 --out /results/core-1-50
DISPAT_EXPERIMENT_IMAGE=sha256:d061bacaae4a1edec2a76368f3cc18bd2b397b7519e6af8ec2ab5a2d09772f1d "$H/e2/run.sh" dispat "$OUT/e2-dispat"
docker run --rm --cpus 2 --memory 4g -v "$H/e5:/exp:ro" -v "$OUT/e5:/results" sha256:6748c967a6257d2d3a1784dc2c6a51a5e43885833e536f499c0be4b0793f5fe5 orphan dispat
```

On a fresh machine replace the two image IDs by images built from `prepare-v182/harness/docker/Dockerfile` (`--target node`) and `prepare-v182/harness/e5/Dockerfile` with the same `DISPAT_VERSION` build argument. `e5/run.sh` takes `<experiment> <tool> [scenario]` with experiments `orphan|midrelease`, tools `lerna|nx|changesets|dispat`, scenarios `clean|conflict`.

**Fresh machine.** The digest-pinned runtime image rebuilt with `--no-cache` in 5.9 s (`build-runtime-relimg-1.8.2-nocache.log`): the binary hash is the locked `78b0b37b…`, the image ID is `7c8232c5…` rather than the campaign's `6344948a…`, and the auxiliary packages are whatever `python:3.12-alpine` and Alpine serve that day (`inspect-runtime-relimg-1.8.2-nocache.log` lists them). E2 additionally pulls the mutable tags `verdaccio/verdaccio:6` and `python:3.12-alpine`; the digests used today are in `v182/e2-auxiliary-image-digests.log` (`verdaccio@sha256:fcb86134…`, the same digest that `campaign-1.10.0-20260909/docker/dependency-images.json` pins). E3 needs the replay repositories (Family H); E4 timings are host-sensitive (Family I); the campaign script needs the product clone and `gh`.

**Verification.** `results/v182-20260907/finalize/SHA256SUMS` (753 files, historical absolute paths):

```sh
python3 experiments/tools/check-manifest.py experiments/results/v182-20260907/finalize/SHA256SUMS \
  --root experiments/results/v182-20260907 --strip-prefix /Users/yohimik/Projects/dispat-experiments/results/v182-20260907
```

The per-experiment outcomes are compared row by row with the retained shards; `e1/canonical-manifest.json` binds shard hashes and the extractor hash. The 503 E195 rejection dossiers were checked by `output/experiments-v182-guard-check.txt`.

**Status.** EXACT on this machine (images `6344948a…`, `d061baca…`, `6748c967…` present and used); RECIPE on a fresh machine.

| Step (`results/repro-20260922/v182/`) | exit | expected | Result |
|---|---|---|---|
| `check-finalize-SHA256SUMS` | 0 | yes | 753/753 match |
| `golden-gate-v182-harness`, `gate0-v182-harness` (rebuilt image `376e8a66…`) | 0 | yes | `golden: PASS`; plan events parse |
| `golden-gate-exact-v182-runtime` (image `6344948a…`) | 0 | yes | `golden: PASS` |
| `e1-core-1-50-v182-harness` | 0 | yes | 50/50 clean; every row identical to seeds 1 to 50 of `results/v182-20260907/e1/core-1-1000/e1-core-1-1000.json` |
| `e1-core-1-50-exact-v182-runtime` | 0 | yes | rows identical to the retained shard and to the rebuilt-image run (`e1-exact-image/core-1-50/`) |
| `e1-full-1-20-v182-harness` | 0 | yes | 8 clean, 6 E195 rejections, PG1 8, PG2 4, PG3? 5; every row identical to seeds 1 to 20 of `results/v182-20260907/e1/full-1-1000/e1-full-1-1000.json` (rejection evidence path aside) |
| `e2-dispat-phase-exact-v182-node-image` | 0 | yes | 18 s; refused run leaves only `cli@1.0.0`, recovery publishes `cli@1.0.1`, third plan empty; `e2-dispat/verdict.json` identical to `results/v182-20260907/e2/dispat-rep1/verdict.json` |
| `e5-orphan-dispat-exact-v182-image` | 0 | yes | 82 s; `VERDICT: all expectations hold`; `e5/orphan-dispat/verdict.json` identical to `results/v182-20260907/e5/orphan-dispat/verdict.json` (8 checks) |
| `historical-e1-e5/build-runtime-relimg-1.8.2-nocache` | 0 | yes | digest-pinned rebuild succeeds; binary `78b0b37b…`; new image ID |

## Family D. The 9 September 1.8.2 SANER campaign

**What and where.** The first SANER protocol execution (`saner-2027/PLAN.md`) on 1.8.2: parser and golden gates, core holdout seeds 90001 to 90300, 20 recovery episodes, the npm to Docker to Docker mixed chain (30 executions), the CI fixture (3 repetitions), and a separate macOS control. Evidence in `saner-2027/campaign-20260909/`: `CAMPAIGN-STATUS.md`, `core/e1-core-90001-300.json`, `core-holdout.log`, `recovery/results.json`, `recovery/traces/`, `recovery/verification.json`, `mixed-docker/run-20260908-224925/`, `mixed-docker/verification.json`, `mixed/mac-verification.json` and `mixed/run-20260909-023901/`, `integration/results/`, `binary-provenance.log`, `images.json`, `harness-hashes.json`, `harness-final-hashes.json`, and the retained setup failures `parser-gate-missing-identity.log`, `recovery-trace-setup-failure*.log`, `recovery-original-harness/`, `core-prior-runtime/`.

**Pins.** Runner `sha256:4dff2f294ebecc7bde6e0456ca7776d6ad20e21aa8fc9729ad0c926dc66a86c9` (`docker/runner-image.json`, tag `dispat-saner:20260909-locked`), built from `docker/Dockerfile` (SHA-256 `8f8054a5…`; `FROM yohimik/dispat-alpine@sha256:4c0ad4b8…` and `FROM docker@sha256:eccaacfe…`) with `docker/apk.lock` (SHA-256 `fc573cf7…`, byte-identical to the 1.10.0 campaign's lock); binary `78b0b37b…` (`binary-provenance.log`); toolchain in `docker/toolchain.txt`; harness in `harness/` (identical to `campaign-1.10.0-20260909/protocol/harness/`); recovery seeds 100 to 104 with n 20 and 100 and p .1 and .3 (`recovery-holdout.py`); mixed schedule seed 20260909 (`mixed-docker/run.py`).

**Rerun into a new directory.** `run-canonical.py` writes its logs beside itself and reads `docker/runner-image.json`, so copy the campaign's `harness/`, `docker/`, `run-canonical.py`, `recovery-holdout.py`, `mixed-docker/run.py`, `mixed-docker/verify.py`, `integration/run.py` and `verify-recovery.py` into a new directory with empty `core/` and `recovery/` (as `RESTORATION.md`, "September 9 Docker campaign", describes), put the runner's ID into the copied `docker/runner-image.json`, and run `python3 NEW/run-canonical.py`. The mixed stage mounts `/var/run/docker.sock`. The integration fixture alone is Family J.

**Fresh machine.** The runner recipe is the same `apk.lock` as Family F and fails today for the same reason (see there). The mixed chain and CI fixture need only Docker; the mixed chain needs the socket.

**Verification.** `verify-recovery.py` and `mixed-docker/verify.py` rewrite `verification.json` beside their inputs, so run them on a copy:

```sh
cp -R experiments/saner-2027/campaign-20260909/recovery COPY/recovery && cp experiments/saner-2027/campaign-20260909/verify-recovery.py COPY/
python3 COPY/verify-recovery.py
cp -R experiments/saner-2027/campaign-20260909/mixed-docker/run-20260908-224925 COPY/mixed-docker/ && cp experiments/saner-2027/campaign-20260909/mixed-docker/verify.py COPY/mixed-docker/
python3 COPY/mixed-docker/verify.py COPY/mixed-docker/run-20260908-224925
python3 experiments/saner-2027/campaign-1.10.0-20260909/protocol/verify-core.py COPY/core 1.8.2
```

**Status.** EXACT on this machine (runner `4dff2f29…` present); RECIPE on a fresh machine, currently blocked by the package mirror.

| Step (`results/repro-20260922/companion-20260909/`) | exit | expected | Result |
|---|---|---|---|
| `verify-recovery-on-copy` | 0 | yes | `{"status": "PASS", "episodes": 20, "maximum_runs": 5, "progress_every_run": 20, "raw_command_records": 254}`, identical to `recovery/verification.json` |
| `verify-mixed-docker-on-copy` | 0 | yes | 405 assertions, 30 cases, 12 recoveries; identical to `mixed-docker/run-20260908-224925/verification.json` and, without the check list, to `mixed-docker/verification.json` |
| `verify-core-on-copy-with-1.10.0-verifier` | 0 | yes | `INTEGRITY_PASS`, 300 rows, 300 accepted matching (`copy/core/verification.json`) |
| `locked-runner-identity` | 0 | yes | runner `4dff2f29…` reports `dispat 1.8.2 (linux_arm64)`, binary `78b0b37b…` |
| `integration-fresh-run-locked-1.8.2-runner` | 0 | yes | see Family J |

## Family E. The 1.9.0 failed attempt and corrected rerun

**What and where.** `saner-2027/campaign-next-release-prepared/` (`CAMPAIGN-PLAN.md`, `ARCHIVES.md`, `release-lock.json`, `execute.py`, `protocol/`, `protocol-sha256.json`, `docker/`). Runs: `runs/run-v1.9.0-linux-arm64-20260909/` (FAILED at `mixed-4node-verification`, no `COMPLETE`; `provenance.json`, stage logs, `ARCHIVE.json`, `work.tar.gz`) and `runs/run-v1.9.0-linux-arm64-20260909-corrected/` (COMPLETE, 14 stages). Report: `paper/saner/evidence/EXPERIMENTS-1.9.0-20260909.md`.

**Pins** (`release-lock.json`): `dispat 1.9.0 (linux_arm64)`, image `yohimik/dispat-alpine@sha256:bf89800987e88a14683fb86b7dede7e9de1fedef82a454b8669655db98096d35`, index `…@sha256:68b86c1a…`, binary `be3370c472cdbfe66fe4256d3fc1ff78ff19bdd5f041ef222187a52767fa4f35`, runner `sha256:97363c9dbac292599987e66241d6da56abd7540df965b24bc20d20573fcac31f`, gated source `8402051e`, release commit `37610088`. Archives: failed `8405e669…` (9,189 files), corrected `664b0b11…` (9,190 files). The `protocol/`, `execute.py`, `protocol-sha256.json`, `docker/Dockerfile` and `docker/apk.lock` retained here are byte-identical to `campaign-1.10.0-20260909/` (the corrected four-node predicate is the one in both); the failed attempt's own protocol hashes are inside its `provenance.json`.

**Rerun into a new directory.** From `saner-2027/campaign-next-release-prepared/`:

```sh
python3 execute.py --release-lock "$PWD/release-lock.json" --run-id run-v1.9.0-linux-arm64-YYYYMMDD --with-4node-extension
python3 execute.py --release-lock "$PWD/release-lock.json" --run-id run-v1.9.0-linux-arm64-YYYYMMDD --with-4node-extension --execute
```

`execute.py` accepts `--release-lock` (required), `--run-id`, `--execute`, `--with-4node-extension`; it refuses an existing `runs/RUN_ID`, checks `protocol/` against `protocol-sha256.json`, inspects the locked runner ID and its `org.dispat.research.source-image` label, and runs the 14 stages. Afterwards `python3 tools/archive-campaign.py RUN` and `python3 tools/verify-saner-archive.py RUN` from the repository root.

**Fresh machine.** As Family F: the runner cannot be rebuilt from `docker/apk.lock` today, and `execute.py` refuses any runner whose ID differs from the lock, so a fresh machine needs a new lock with a rebuilt runner (which the lock file format allows) once the recipe builds again.

**Verification.** `tools/summarize-saner-campaign.py RUN` (archive checksum, temporary extraction, reaggregation; refuses a run without `COMPLETE`) and the four offline verifiers via `experiments/tools/verify-saner-archive-to.py RUN NEW_DIR`. The retained `tools/verify-saner-archive.py` would create `archive-verification/` inside the retained corrected run, which this audit avoided by writing elsewhere, and it refuses the failed attempt because that run has no `COMPLETE`; the corrected run's original extraction check is described in `paper/saner/evidence/EXPERIMENTS-1.9.0-20260909.md`.

**Status.** Corrected run: EXACT on this machine, RECIPE (blocked) on a fresh one. Failed attempt: HISTORICAL by design (evidence of the oracle correction; no verifier accepts it).

| Step (`results/repro-20260922/v190/`) | exit | expected | Result |
|---|---|---|---|
| `summarize-corrected-from-archive` | 0 | yes | archive `664b0b11…` verified, 14 stages PASS, core 300/300, recovery 20 episodes at most 4 runs with 248 records, mixed 522 and 798 checks, integration 81 |
| `summarize-failed-attempt-refused` | 1 | yes | `AssertionError` on `status == COMPLETE`, as designed |
| `verify-archive-corrected-exact-runner` | 0 | yes | core, recovery, mixed-docker, mixed-4node all exit 0 in runner `97363c9d…` (`archive-verification-corrected/verification.json`) |
| `verify-archive-failed-attempt-refused` | 1 | yes | "run is not COMPLETE" |
| `release-identity-gate-exact-runner` | 0 | yes | binary `be3370c4…`, `dispat 1.9.0 (linux_arm64)` |
| `golden-gate-exact-runner` | 0 | yes | `golden: PASS` |
| `core-sample-90001-20-exact-runner` | 0 | yes | 20/20 clean; rows identical to seeds 90001 to 90020 of the archived `work/core/e1-core-90001-300.json` of the corrected run |

## Family F. The 1.10.0 campaign with its Docker runner and apk lock

**What and where.** The paper's companion dataset: `saner-2027/campaign-1.10.0-20260909/` (`README.md`, `CAMPAIGN-PLAN.md`, `ARCHIVES.md`, `FREEZE.json`, `release-lock.json`, `identity-measurements.json`, `release-source-review.json`, `protocol/`, `protocol-sha256.json`, `execute.py`, `docker/`, `campaign.log`, `summary.json`, `POSTPROCESSING.json`, `SHA256SUMS.json`), run `runs/run-v1.10.0-linux-arm64-20260909/` (`provenance.json`, `COMPLETE`, stage logs, `ARCHIVE.json`, `work.tar.gz`, `archive-verification/`, `recovery-comparison.json`), and the diagnostics addendum `diagnostics/` (`run.py`, `FREEZE.json`, `provenance.json`, `execution.log`, `results/observations.json`, `results/verification.json`, `results/fixture/`). Report: `paper/saner/evidence/EXPERIMENTS-1.10.0-20260909.md`.

**Pins** (`release-lock.json`, `FREEZE.json`, `docker/`): `dispat 1.10.0 (linux_arm64)`, image `yohimik/dispat-alpine@sha256:f2a49c21eca0a3e30af1396eca538920b2faa475b50f12d4aae99236e2fe2955` (linux/arm64 manifest), index `…@sha256:c7c03077f20d5763316d75ed22ba9ece0ec2908167a69747e56c35e5855e1af8`, binary `03d1ba5fbaef35b69582e9489f40b5438f81ae6926e02ea6d02716b5b73d92fd`, runner `sha256:6f92932fbba5d33d61d777073f5fc155133063f4c3d4b2f950e3e5b9ed9a263e` (labelled with the source image, `identity-measurements.json`), release lock SHA-256 `b01914fc…`, protocol manifest `a3366e2f…` (52 protocol files; `FREEZE.json` adds the campaign's own ten files), `docker/Dockerfile` `2e2bf7c0…` (`FROM docker@sha256:eccaacfe…`), `docker/apk.lock` `fc573cf7…` (75 Alpine 3.24.1 packages, listed in `identity-measurements.json` as installed), auxiliary images `verdaccio@sha256:fcb86134…`, `registry@sha256:1be55279…`, `moby/buildkit@sha256:28a89871…` (`docker/dependency-images.json`), gated source `1bb3b397…`, CLI release commit `7a96ae95…`, release commit `66cffcda…`. Seeds: core 90001 to 90300; recovery seeds 100 to 104 with n 20 and 100 and p .1 and .3 (`protocol/recovery-holdout.py`); mixed schedule seed 20260909 (`protocol/mixed-docker/run.py`, `protocol/mixed-4node/run.py`). Archive `835208a0cd9066ec6bf7ec424a4d9cdee06ca4482a061f7a7d7cc02738611793`, 3,380,083 bytes, 9,157 files. Diagnostics script SHA-256 `2a589909…` (`diagnostics/FREEZE.json`, `diagnostics/provenance.json`).

**Rerun into a new directory.** From `saner-2027/campaign-1.10.0-20260909/`:

```sh
python3 execute.py --release-lock "$PWD/release-lock.json" --run-id run-v1.10.0-linux-arm64-YYYYMMDD --with-4node-extension
python3 execute.py --release-lock "$PWD/release-lock.json" --run-id run-v1.10.0-linux-arm64-YYYYMMDD --with-4node-extension --execute
python3 ../../../tools/archive-campaign.py runs/run-v1.10.0-linux-arm64-YYYYMMDD
python3 ../../../tools/verify-saner-archive.py runs/run-v1.10.0-linux-arm64-YYYYMMDD
```

Budget 45 to 90 minutes plus 30 to 60 for the four-node extension (`campaign-next-release-prepared/CAMPAIGN-PLAN.md`); the mixed stages need the Docker socket and use the fixed container names `saner-next-release-mixed` and `saner-next-release-mixed-4node`. The diagnostics addendum reruns from a copy of `diagnostics/run.py` in an empty directory (its `results/` must not exist):

```sh
mkdir -p NEW/diagnostics && cp diagnostics/run.py NEW/diagnostics/
docker run --rm --network none --cpus 2 --memory 4g -v "NEW/diagnostics:/diagnostics" \
  sha256:6f92932fbba5d33d61d777073f5fc155133063f4c3d4b2f950e3e5b9ed9a263e python3 /diagnostics/run.py
```

**Fresh machine.** The runner recipe is documented (`docker/Dockerfile` plus `docker/apk.lock`, both digest-pinned to their base images) and was rebuilt here twice. With BuildKit's layer cache the rebuild reproduces the recorded package list exactly (75 packages identical to `identity-measurements.json`) with binary `03d1ba5f…` and a new image ID `677334788c…` (`mechanisms/rebuild-runner-from-apk-lock.log`, `inspect-rebuilt-runner.log`). With `--no-cache`, which is what a fresh machine gets, the rebuild fails: `apk add` reports `xz-libs-5.8.4-r0: breaks: world[xz-libs=5.8.3-r0]` because the Alpine 3.24 repository has replaced `xz-libs 5.8.3-r0` (`mechanisms/rebuild-runner-from-apk-lock-nocache.log`). So on 22 September a fresh machine can build neither the exact runner nor a runner satisfying the lock; relaxing the lock changes the environment and needs a new release lock and run name, as `campaign-mechanisms-20260910/README.md` already requires. No `docker save` export of `6f92932f…` exists in the repository. The pinned published image and binary remain fetchable (`environment/published-image-tags-resolve.log`).

**Verification.** From the repository root:

```sh
python3 tools/summarize-saner-campaign.py experiments/saner-2027/campaign-1.10.0-20260909/runs/run-v1.10.0-linux-arm64-20260909
python3 experiments/tools/verify-saner-archive-to.py experiments/saner-2027/campaign-1.10.0-20260909/runs/run-v1.10.0-linux-arm64-20260909 NEW_DIR
python3 experiments/tools/check-manifest.py experiments/saner-2027/campaign-1.10.0-20260909/SHA256SUMS.json --root experiments/saner-2027/campaign-1.10.0-20260909
python3 experiments/tools/check-manifest.py experiments/saner-2027/campaign-1.10.0-20260909/FREEZE.json --root experiments/saner-2027/campaign-1.10.0-20260909
```

`tools/verify-saner-archive.py` refuses this run because `archive-verification/` already exists; the relocatable copy writes elsewhere. `diagnostics/FREEZE.json` is not a file map (it holds one `sha256`, the script's), so `check-manifest.py` does not apply to it; compare `shasum -a 256 diagnostics/run.py` with that value.

**Status.** EXACT on this machine (runner `6f92932f…` present and used for every check below); RECIPE on a fresh machine, currently blocked by the Alpine mirror.

| Step (`results/repro-20260922/v1100/`) | exit | expected | Result |
|---|---|---|---|
| `check-SHA256SUMS-json` | 0 | yes | 103/103 retained files match |
| `check-FREEZE-json` | 0 | yes | 62/62 frozen inputs match |
| `check-diagnostics-FREEZE-json` | 1 | no | checker misapplied to a non-map file (all four keys "missing"); superseded by the next row |
| `diagnostics-script-hash` | 0 | yes | `diagnostics/run.py` = `2a589909…`, equal to `FREEZE.json` and `provenance.json` |
| `summarize-from-archive` | 0 | yes | output identical to the retained `summary.json` |
| `verify-archive-exact-runner` | 0 | yes | core `INTEGRITY_PASS` 300/300, recovery PASS 20 episodes 251 records, mixed-docker 522 checks, mixed-4node 798 checks (`archive-verification/`) |
| `release-identity-gate-exact-runner` | 0 | yes | binary `03d1ba5f…`, `dispat 1.10.0 (linux_arm64)` |
| `parser-gate-exact-runner`, `golden-gate-exact-runner` | 0 | yes | plan events parse; `golden: PASS` |
| `core-sample-90001-20-exact-runner` | 0 | yes | 20/20 clean; rows identical to seeds 90001 to 90020 of the archived `work/core/e1-core-90001-300.json` |
| `diagnostics-fresh-run-exact-runner` | 0 | yes | 16/16 cases pass, fixture unchanged; `diagnostics-rerun/results/observations.json` identical to the retained observations once the timestamps inside dispat's log lines are removed |
| `mechanisms/rebuild-runner-from-apk-lock` (cached) | 0 | yes | package list identical to the recorded runner; image ID `67733478…` |
| `mechanisms/rebuild-runner-from-apk-lock-nocache` | 1 | no | `xz-libs=5.8.3-r0` no longer served |

## Family G. The mechanism campaign of 10 September

**What and where.** 140 controlled recovery cases and a finite projection on 1.10.0: `saner-2027/campaign-mechanisms-20260910/` (`README.md`, `PROTOCOL.md`, `RESULTS.md`, `PILOT-FREEZE.json`, `FULL-FREEZE.json`, `FULL-PROVENANCE.json`, `release-lock.json`, `execute.py`, `publisher.py`, `run.py`, `verify.py`, `archive.py`, `postprocess.py`, `provenance.py`, `freeze.py`, `manifest.py`, `summary.json`, `full-01.log`, `full-01-execution.jsonl`, `pilot-01.log`, `archive-replay-verifier.log`, `negative-verifier-check.log`, `NEGATIVE-VERIFIER-CHECK.json`, `overwrite-refusal.log`, `SHA256SUMS.json`). Runs: `runs/full-01/` (140 case directories with `commands/NNNN.json` and `observation.json`, `cases.json`, `identity.json`, `model-states.jsonl`, `summary.json`, `verifier.json`, `archive-replay-verifier.json`, `archive-verification.json`, `expanded-fixtures.tar.gz`) and `runs/pilot-01/` (10 cases).

**Pins.** Same release lock as Family F (`release-lock.json` SHA-256 `b01914fc…`, runner `6f92932f…`, binary `03d1ba5f…`); case order seed 20260910 (`execute.py`, `FULL-FREEZE.json`); script hashes in `FULL-FREEZE.json` (`execute.py` `253ea14a…`, `publisher.py` `01fe9bfd…`, `verify.py` `ff6bdf97…`); full archive `0c94a5490f2e22eba90407c37588dd9860b6191f43b132ede6e7807fe3585fda` (16,464 files, 8,367,533 bytes), pilot archive `1ffa7415…` (1,160 files); host and image identity in `FULL-PROVENANCE.json`.

**Rerun into a new directory.** From the campaign directory:

```sh
python3 run.py full-02
docker run --rm --network none --cpus 2 --memory 4g --platform linux/arm64 -v "$PWD:/campaign" -w /campaign \
  sha256:6f92932fbba5d33d61d777073f5fc155133063f4c3d4b2f950e3e5b9ed9a263e python3 verify.py runs/full-02 runs/full-02/verifier.json
python3 archive.py runs/full-02 --remove-expanded
python3 postprocess.py runs/full-02 summary-full-02.json
```

`run.py NAME` refuses an existing `runs/NAME`, `NAME.log` or `NAME-execution.jsonl` and always uses the locked runner ID; `execute.py OUTPUT [--pilot]` refuses an existing output and asserts the binary hash against `release-lock.json`; `verify.py RUN OUTPUT` and `postprocess.py RUN OUTPUT` create their output exclusively; `archive.py RUN [--remove-expanded]` refuses an existing archive. The full matrix took 113.65 s in the retained run (`full-01-execution.jsonl`). A ten-case pilot in a copy of the four scripts, as executed here, takes about 7 s:

```sh
mkdir -p NEW/campaign/runs && cp execute.py publisher.py verify.py release-lock.json NEW/campaign/
docker run --rm --network none --cpus 2 --memory 4g --platform linux/arm64 -v "NEW/campaign:/campaign" -w /campaign \
  sha256:6f92932fbba5d33d61d777073f5fc155133063f4c3d4b2f950e3e5b9ed9a263e python3 execute.py runs/pilot-02 --pilot
```

**Fresh machine.** Exactly the Family F limit: the campaign's `README.md` already states that the runner image ID is local-only and gives the digest-pinned rebuild recipe from `../campaign-1.10.0-20260909/docker/Dockerfile` and `apk.lock`; this audit shows that the recipe reproduces the package list from a warm cache and fails from a cold one on 22 September. The README's instruction to treat a rebuilt runner as a separate provenance run with a new lock stands.

**Verification.** Offline, without Docker: `check-manifest.py SHA256SUMS.json --root CAMPAIGN` (4,896 files). With the runner: the relocatable replay `experiments/tools/verify-mechanisms-run-copy.py CAMPAIGN/runs/full-01 NEW_DIR`, which is the README's copy-extract-verify procedure.

**Status.** EXACT on this machine; RECIPE on a fresh machine, currently blocked.

| Step (`results/repro-20260922/mechanisms/`) | exit | expected | Result |
|---|---|---|---|
| `check-SHA256SUMS-json` | 0 | yes | 4,896/4,896 retained files match |
| `check-FULL-FREEZE-json` | 0 | yes | 9/9 frozen scripts match |
| `verify-full-01-from-archive-exact-runner` | 0 | yes | archive `0c94a549…` verified; 16,464 extracted files match `archive-verification.json`; `verify.py` PASS, 140/140 cases, strata and model counts identical to `runs/full-01/verifier.json` and `archive-replay-verifier.json` (`full-01-replay/report.json`, `verifier.json`) |
| `verify-pilot-01-from-archive-exact-runner` | 0 | yes | 1,160 files match; PASS 10/10, identical to `runs/pilot-01/verifier.json` |
| `pilot-fresh-run-exact-runner` | 0 | yes | new ten-case matrix in 6.9 s: `summary.json` identical to `runs/pilot-01/summary.json`, `identity.json` identical |
| `pilot-fresh-run-verify` | 0 | yes | PASS, identical to `runs/pilot-01/verifier.json` (run path and time aside) |
| `pilot-fresh-run-archive-fixtures` | 0 | yes | 1,160 fixture files archived (`pilot-repro/campaign/runs/pilot-repro/expanded-fixtures.tar.gz`), expanded copies removed |
| `rebuild-runner-from-apk-lock` / `-nocache` | 0 / 1 | yes / no | see Family F |

## Family H. Fixture replays (E3a)

**What and where.** `e3a/replay.py` replays the last five releases of `googleapis/google-cloud-node` (profile `gcn`) and `conventional-changelog/conventional-changelog` (profile `cc`) and compares the planned package versions with what shipped. Evidence: `results/e3a/gcn.json`, `results/e3a/cc.json` (28 August), `results/v140/e3a/`, `results/v160/e3a/`, `results/v172/e3a/`, `results/v180-20260906/e3a/`, `results/v181-20260907/e3/`, `results/v182-20260907/e3/gcn.json` and `cc.json` (36/42 and 7/64 exact package-version observations). The `babel` lock has no retained replay result.

**Pins.** `fixture-locks/google-cloud-node.json` (origin, head `54e244b4980e362ac9194d29c299b949ff778fda`, 4,955 tag object IDs, clean status), `fixture-locks/conventional-changelog.json` (head `340ad83ee93939fc4a8c8f2da1bf728111299941`, 878 tags), `fixture-locks/babel.json` (head `a946b816…`, 925 tags); the three `.patch` files are empty (no local modifications). The campaign scripts assert those heads and a clean status. The replay uses `git worktree add --detach WT SHA^` with a sparse checkout of `packages/*/package.json` and `dispat status --log-format json`; the profile config is written by `replay.py`.

**Rerun into a new directory.** Restore one fixture and replay, from the repository root with `OUT` absolute and new:

```sh
python3 experiments/tools/restore-one-replay-fixture.py conventional-changelog "$OUT/repos/conventional-changelog"
docker run --rm --network none --cpus 2 --memory 4g -v "$PWD/experiments/prepare-v182/harness:/exp:ro" \
  -v "$OUT/repos:/fixtures" -v "$OUT:/results" -w /exp dispat-exp:v182-rt python3 e3a/replay.py /fixtures/conventional-changelog cc 5 /results/cc.json
```

`replay.py` takes `REPO PROFILE K OUT` positionally. For all three fixtures into the canonical location, `python3 tools/restore-replay-fixtures.py` (refuses existing checkouts). The root `e3a/replay.py` differs from the frozen `prepare-v182/harness/e3a/replay.py`; use the frozen one to compare with the v182 numbers.

**Fresh machine.** Needs the upstream repositories to still serve the locked objects; the restore of `conventional-changelog` (14 MB) took 23 s today. `google-cloud-node` is several gigabytes and was not restored in this audit. The restored clone was removed after the replay (its identity is in `e3a/restored-clone-identity-before-removal.log`: head `340ad83e…`, 878 tags, no worktrees left).

**Verification.** Row-level comparison with the retained JSON (the `sha` field is full length in the v182 files and ten characters in `results/e3a/`).

**Status.** RECIPE (restorable from the locks; upstream availability is the dependency). The replay outcome reproduced exactly.

| Step (`results/repro-20260922/e3a/`) | exit | expected | Result |
|---|---|---|---|
| `restore-conventional-changelog` | 0 | yes | restored at `340ad83e…` with 878 locked tags in 23.2 s |
| `replay-cc-5-v182-harness` | 0 | yes | `cc.json` identical to `results/v182-20260907/e3/cc.json` (7 exact of 64 released) and to `results/e3a/cc.json` |
| `restored-clone-identity-before-removal` | 0 | yes | recorded, then the clone was deleted |

## Family I. Scale cells (E4)

**What and where.** `e4/timing.py` measures `dispat status` wall time and RSS over eight cells (P, shape, U, pad); `e4/recovery.py` runs seeded failing releases against a `file://` origin; `e4/verify_fixture_provenance.sh` reproduces the commit-tree equivalence check. Evidence: `results/e4/timing.csv`, `results/e4/e4c-recovery.json`; `results/v140/e4/` (with `timing-headline-5x.csv`), `results/v160/e4/`, `results/v172/e4/`, `results/v180-20260906/e4/` (`timing-status.json`, failed attempts, `fixture-provenance/`), `results/v181-20260907/e4/`, `results/v182-20260907/e4/` (`timing.csv`, `cells/0.csv` to `7.csv`, `rep1/`, `rep2/`, `fixture/`).

**Pins.** Cells and seed 42 in `e4/timing.py`; recovery cells n 20 and 100, p .1 and .3, seeds 0 to 2 in `e4/recovery.py`; `REALIZE_COMMIT_TREE=1` for pad 5000; container limits 2 CPUs and 4 GiB; the harness snapshot used by v182 is `prepare-v182/harness/e4/`.

**Rerun into a new directory** (from `experiments/`, `H=$PWD/prepare-v182/harness`, `dispat-exp:v182-rt` as in Family C):

```sh
docker run --rm --network none --cpus 2 --memory 4g -e E4_FAILURE_DIR=/failures -v "$H:/exp:ro" -v "$OUT/failures:/failures" -w /exp dispat-exp:v182-rt python3 e4/timing.py 0 > "$OUT/cells/0.csv"
docker run --rm --network none --cpus 2 --memory 4g -v "$H:/exp:ro" -v "$OUT/rep1:/results" -w /exp dispat-exp:v182-rt python3 e4/recovery.py /results
docker run --rm --network none --cpus 2 --memory 4g -v "$H:/exp:ro" -v "$OUT/fixture:/results" -w /exp dispat-exp:v182-rt sh e4/verify_fixture_provenance.sh /results
```

Cell indexes 0 to 7 are `(100,layered,200,0)`, `(1000,layered,200,0)`, `(10000,layered,200,0)`, `(1000,chain,200,0)`, `(10000,chain,200,0)`, `(1000,star,200,0)`, `(1000,layered,1000,0)`, `(1000,layered,200,5000)`; the 10,000-package cells take about 20 s of measurement each plus generation, so the full grid is minutes, not seconds.

**Fresh machine.** Any host runs the cells; the numbers are host-sensitive (`experiments/README.md`, gotchas 14, 17 and 18; `results/v180-20260906/README.md`), so only order of magnitude and cell ranking are comparable.

**Verification.** No verifier beyond `git fsck` inside `timing.py` and the provenance script; compare the CSV with `results/v182-20260907/e4/timing.csv`.

**Status.** RECIPE. The smallest cell reproduced within noise.

| Step (`results/repro-20260922/e4/`) | exit | expected | Result |
|---|---|---|---|
| `timing-cell-0-100-layered-v182-harness` | 0 | yes | `100,layered,200,0,185,0.016,0.016,0.017,15`; retained v182: `…,0.017,0.017,0.017,15` |
| `timing-cell-0-repeat-2` | 0 | yes | `…,0.018,0.017,0.018,17` |
| `verify-fixture-provenance-small-only-skipped` | 0 | yes | not run (two 1,000-package fixtures plus a padded one; outside the budget); the retained record is `results/v182-20260907/e4/fixture/` |

E4 recovery (12 episodes per repetition) was not rerun; `results/v182-20260907/e4/rep1/recovery.log` and `rep2/` remain the evidence.

## Family J. The CI/integration fixture

**What and where.** `integration/run.py` builds a fixture with one unchanged workflow entrypoint, adds a specification package and an executable consumer, injects a failed and a missing required test, repairs, and reruns unchanged, three repetitions, 81 checks. Evidence: `saner-2027/campaign-20260909/integration/results/` (1.8.2), the archived `work/integration/results/` inside the 1.9.0 and 1.10.0 `work.tar.gz` archives, and the integration stage logs `integration.log` of each run.

**Pins.** The script itself (`protocol/integration/run.py` SHA-256 `1b7690d8…` in `FREEZE.json`; the copy in `campaign-20260909/integration/run.py` is the same protocol file), the runner of each campaign, container settings `--network none --cpus 2 --memory 4g --tmpfs /workspaces`.

**Rerun into a new directory.** `run.py` creates `results/` beside itself and refuses if it exists, so copy it:

```sh
mkdir -p NEW/integration && cp experiments/saner-2027/campaign-1.10.0-20260909/protocol/integration/run.py NEW/integration/
docker run --rm --network none -e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=init.defaultBranch -e GIT_CONFIG_VALUE_0=main \
  -e GIT_AUTHOR_NAME=Experiment -e GIT_AUTHOR_EMAIL=experiment@example.invalid -e GIT_COMMITTER_NAME=Experiment -e GIT_COMMITTER_EMAIL=experiment@example.invalid \
  --cpus 2 --memory 4g --tmpfs /workspaces:rw,size=1g -e TMPDIR=/workspaces \
  -v "$PWD/experiments/saner-2027/campaign-1.10.0-20260909/protocol/harness:/exp:ro" -v "NEW:/results" -w /exp \
  sha256:6f92932fbba5d33d61d777073f5fc155133063f4c3d4b2f950e3e5b9ed9a263e python3 /results/integration/run.py
```

The Git identity variables are required (the first 9 September attempt failed without them, `campaign-20260909/parser-gate-missing-identity.log`). The fixture compiles `tools/main.c` with the runner's `gcc`.

**Fresh machine.** Only the runner is the limit (Families D and F). The fixture itself needs no network.

**Verification.** `results/verification.json` is written by the run (81 checks); compare the check list and the per-repetition `N-observations.json` with the retained ones. The order of concurrent `tests` events inside a snapshot is not deterministic (`experiments/README.md`, "only plans are deterministic"), so compare events as multisets.

**Status.** EXACT on this machine in both runners; RECIPE elsewhere.

| Step | exit | expected | Result |
|---|---|---|---|
| `integration/integration-fresh-run-exact-runner` (1.10.0 runner) | 0 | yes | 3 repetitions PASS, 81 checks identical to the archived list; per-snapshot exit, tags, packages and event multisets identical; entrypoint hashes identical |
| `companion-20260909/integration-fresh-run-locked-1.8.2-runner` (runner `4dff2f29…`) | 0 | yes | same comparison against `campaign-20260909/integration/results/`: identical up to event order |
| `v1100/diagnostics-fresh-run-exact-runner` | 0 | yes | listed under Family F |

## Summary

| Family | This machine | Fresh machine | Executed check | Result |
|---|---|---|---|---|
| A. Historical E1 to E5, vendored source | RECIPE (binary), HISTORICAL (image identity) | same | source build twice, golden gate, 50 core seeds | binary `2d33ac7d…` both builds; rows identical to `results/e1` |
| B. Released-image campaigns 1.4.0 to 1.8.1 | RECIPE (1.8.0, 1.8.1); tag-only (1.4.0 to 1.7.2) | same | manifests v180 (with nested-git archive) and v181; tag resolution | all files match; all tags resolve |
| C. 1.8.2 campaign | EXACT | RECIPE | manifest, gates, E1 core 50 and full 20, E2, E5 orphan, E4 cell 0, E3a cc | all identical to retained records |
| D. 9 September 1.8.2 SANER campaign | EXACT | RECIPE, blocked by apk mirror | recovery, mixed and core verifiers on copies; fresh integration run | all PASS and identical |
| E. 1.9.0 failed and corrected | EXACT (corrected); HISTORICAL (failed) | RECIPE, blocked | summariser, archive verifiers, gates, 20 core seeds | PASS; failed attempt refused as designed |
| F. 1.10.0 campaign | EXACT | RECIPE, blocked | manifests, summariser, archive verifiers, gates, 20 core seeds, diagnostics rerun, runner rebuild | PASS; cold rebuild fails on `xz-libs` |
| G. Mechanism campaign | EXACT | RECIPE, blocked | manifests, full-01 and pilot-01 archive replays, fresh pilot matrix | PASS; fresh pilot identical to `pilot-01` |
| H. E3a replays | RECIPE | RECIPE | restore `conventional-changelog`, replay five releases | identical to v182 and to 28 August |
| I. E4 scale cells | RECIPE | RECIPE | cell 0 twice | within noise of `results/v182-20260907/e4/timing.csv` |
| J. CI/integration fixture | EXACT | RECIPE | fresh runs in both runners | identical up to event order |

## Gaps that block exact reproduction on a fresh machine

1. **No export of the locked runners.** The runners `6f92932f…` (1.10.0 and mechanisms), `97363c9d…` (1.9.0), `4dff2f29…` (9 September 1.8.2) and the experiment images `6344948a…`, `d061baca…`, `6748c967…` (1.8.2), `da722d8c…`, `52870cf6…`, `b6fcf6d9…` (1.8.1), `d4a42648…`, `79f81d17…`, `3db6fd22…` (1.8.0) exist only in this machine's Docker store. `docker save IMAGE | gzip > FILE` of each, with its SHA-256 recorded, would make the EXACT status portable. `docker image inspect --format '{{.Size}}'` reports 195 MB for `6f92932f…`, 31 MB for `6344948a…`, 194 MB for `d061baca…` and 193 MB for `6748c967…` before compression, and the other runners are the same recipe. Where to keep such files is a repository-size decision.
2. **The Alpine package lock no longer resolves.** `campaign-1.10.0-20260909/docker/apk.lock` (shared by `campaign-20260909` and `campaign-next-release-prepared`) pins `xz-libs=5.8.3-r0`; the 3.24 repository now serves `5.8.4-r0` only (`results/repro-20260922/mechanisms/rebuild-runner-from-apk-lock-nocache.log`). Closing options: keep the image export of item 1; or record a second lock produced by a fresh rebuild together with a new release lock and treat it as a separate provenance line, as the mechanism README prescribes; or pin the runner's `apk` repositories to a dated snapshot mirror, which is not part of the current recipe.
3. **Historical binaries without hashes.** `results/e1` to `results/e4` (binary `exp-342062d3`) and `results/v140` to `results/v172` (tags 1.4.0 to 1.7.2) record no binary SHA-256 and no image digest. Today's values are in `results/repro-20260922/historical-e1-e5/inspect-runtime-from-vendored-source-nocache.log` and `environment/published-image-tags-resolve.log`; adopting them as the reference is a decision, since they cannot be tied to the August measurements.
4. **Mutable base images and unpinned packages in the experiments Dockerfile.** `experiments/docker/Dockerfile` uses `golang:1.26-alpine`, `python:3.12-alpine`, `node:22-slim`, `alpine:3` and `apk add git bash hyperfine coreutils`; `prepare-v182/harness/e5/Dockerfile` uses `node:22-slim` and `apt-get`; `e2/run.sh` pulls `verdaccio/verdaccio:6` and `python:3.12-alpine` by tag. The dispat binary is digest-pinned through `DISPAT_VERSION`, everything around it is not. Recording the digests each campaign resolved (as `campaign-1.10.0-20260909/docker/dependency-images.json` does) would let a rebuild pin them.
5. **Campaign scripts that need this host.** `prepare-v181/campaign.sh` and `prepare-v182/campaign.sh` read the product clone at `DISPAT_SOURCE_REPO` (default `/Users/yohimik/Projects/dispat`), call `gh release view` and `rg`, and require all three replay repositories under `experiments/e3a/repos/`. A stranger needs a clone of github.com/yohimik/dispat, an authenticated `gh`, `rg`, and the multi-gigabyte `google-cloud-node` restore before the script starts.
6. **Verifiers that write beside their inputs.** `campaign-20260909/verify-recovery.py`, `mixed-docker/verify.py`, `protocol/verify-core.py`, `integration/run.py` and `diagnostics/run.py` write into the directory they check or refuse if it exists; `tools/verify-saner-archive.py` refuses a run that already has `archive-verification/`. This audit worked around it with copies and the relocatable tools listed above; it is a usability gap, not an evidence gap.
7. **Not executed in this audit** (cost, not blockers): the full 300-seed holdouts, recovery holdouts and mixed chains of Families D to F; the full 140-case mechanism matrix; E4 recovery and the 1,000 and 10,000-package timing cells; the `google-cloud-node` and `babel` restores; the E2 competitor phases and the nine competitor E5 cells; the v181 and v182 campaign scripts end to end.
