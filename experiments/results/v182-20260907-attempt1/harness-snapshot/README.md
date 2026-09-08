# Dispat 1.8.2 experiment campaign (fresh rerun)

This directory prepares a full post-release rerun without modifying
`results/v180-20260906`. The campaign script refuses to run unless all of the
following are true:

- `--released` is supplied;
- `DISPAT_RELEASE_COMMIT` is a full 40-character commit ID;
- the remote tag `services/dispat/v1.8.2` resolves to that commit;
- `docker.io/yohimik/dispat-alpine:1.8.2` pulls successfully;
- the binary copied from that published image reports `dispat 1.8.2`.

The new result root is `results/v182-YYYYMMDD`. It must not exist on the first
run. Every stage writes under `.staging` and is moved into place only after it
succeeds. Its completion marker contains the campaign identity. A resume first
rechecks the release commit, published image digest, harness hashes, and E3
fixture heads/state, and refuses any mismatch. If a stage fails, inspect and
move its `.staging/<stage>` directory aside before retrying; partial or
unmarked raw results are never overwritten.

## Required invocation after the official release

From this repository:

```sh
DISPAT_RELEASE_COMMIT=<40-char-release-commit> \
  ./prepare-v182/campaign.sh --released --out results/v182-$(date +%Y%m%d)
```

Run one heavy Docker container at a time. E4 intentionally uses 2 CPUs and 4
GiB. The version tag is resolved to a registry digest, and both Dockerfiles
receive `1.8.2@sha256:...`, pinning every derived image to those published
bytes. The script records the digest, extracted binary hash and version,
release tag/commit, source-tree commit and dirty state, harness hashes, fixture
identity, image IDs, and complete result hashes. After image construction, all
experiment containers are addressed by their recorded image IDs; mutable local
tags are not used by E1--E5 or by a resumed campaign.

Stages may be selected for a controlled retry:

```sh
DISPAT_RELEASE_COMMIT=<commit> ./prepare-v182/campaign.sh --released \
  --out results/v182-YYYYMMDD --stage e4
```

Valid stages are `provenance`, `images`, `e1`, `e2`, `e3`, `e4`, `e5`, and
`finalize`. Dependencies must already have completion markers when selecting a
later stage.

## Campaign contents

- E1: golden gate; canonical core and full profiles for seeds 1--1000 and
  5001--5500; released CCME 2.0 vectors 133--138 with raw evidence. Each E1
  shard keeps its complete runner output directory, including any
  `dossiers-<profile>` evidence. `canonical-manifest.json` validates the seed
  bounds and binds every shard and the shared plan extractor by SHA-256.
- E2: two isolated Dispat orphan-recovery repetitions, each with a fresh
  registry.
- E3: five historical releases from `google-cloud-node` and
  `conventional-changelog`. These are fixture replays, not claims that the
  historical releases followed CCME.
- E4: two complete recovery repetitions; fixture equivalence and native
  `git fsck` evidence; all eight timing cells, written separately and assembled
  only after every cell succeeds.
- E5: the three Dispat cells (`orphan`, `midrelease clean`, `midrelease
  conflict`) from the main repository's scripts mounted read-only. The nine
  competitor cells remain historical 1.8.0 evidence unless separately rerun;
  they are not copied into or represented as fresh 1.8.2 results.

## Known gaps and interpretation limits

- The historical E1 oracle remains the preserved conference-v8/CCME-1 model.
  Its PG labels are comparison classifications, not CCME 2 conformance claims.
- Vector 135 observes downward eligibility and W208 through the CLI; it does
  not independently call the planner's upward-audit API.
- E3 expected data are historical fixtures and retain their established replay
  semantics.
- E4 timings on Docker Desktop are host-sensitive; record host contention and
  do not treat a single campaign as a clean cross-version benchmark.
- Competitor versions are pinned by the main repository lockfile and are
  historical unless their nine E5 cells are explicitly rerun and identified as
  such in a separate campaign.

## v182 harness isolation and validation

The campaign runs a dedicated harness snapshot under `prepare-v182/harness`; old harness files and v181 evidence remain untouched. E1 checks fixture Git integrity before invoking Dispat, uses tmpfs workspaces to avoid the previously observed overlay fixture issue, and archives failures without silently retrying or dropping seeds. E2 checks expected exit statuses, registry versions, tags, and final plan explicitly, preserving separate run logs. E3 and E4 reject malformed/failed status executions. E4 timing uses the original container filesystem, 2 CPUs and 4GiB, so the E1 filesystem change does not alter benchmark cells. E5 uses a copied, hash-pinned harness from the completed release checkout.

All derived experiment image IDs are fixed after construction. Base and auxiliary images may resolve newer dependency layers than historical campaigns; this is recorded environment provenance, not a claim of byte-identical rebuilds. The Dispat binary itself must match the official GitHub Linux ARM64 asset digest.
