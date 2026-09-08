# dispat v1.7.0 vs v1.7.2: the release that runs its own experiments

Date: 2026-09-04. Both binaries copied out of the official
`yohimik/dispat-alpine:<version>` images. 1.7.2 is the release commit
`e1ac8c51` (`fix(dispat)^^: the release announces itself and ships its
experiments`), released by run 33814918103 of the Release workflow.

## E5, the concurrent push, and the orphan control

Since 1.7.2 the twelve cells of `tests/experiments` run inside the
release itself, as the docs package's beforeBuild hook against the
image the run has just published, and the site page
https://dispat.dev/internals/experiments/ is built from the records.
The release run produced the records in `e5-1.7.2/`; the by-hand
Experiments workflow (run 33816831619, twelve runners) produced
`e5-1.7.2-hand/`. Both on linux_amd64.

| cell | 1.7.0 (local, 2026-09-02) | 1.7.2 release | 1.7.2 by hand |
|---|---|---|---|
| orphan-dispat | 7/7 | 7/7 | 7/7 |
| orphan-lerna | 3/5 | 3/5 | 3/5 |
| orphan-nx | 4/5 | 4/5 | 4/5 |
| orphan-changesets | 5/5 | 5/5 | 5/5 |
| midrelease-clean-dispat | 12/12 | 12/12 | 12/12 |
| midrelease-clean-lerna | 1/5 | 1/5 | 1/5 |
| midrelease-clean-nx | 2/6 | 2/6 | 2/6 |
| midrelease-clean-changesets | 3/5 | 3/5 | 3/5 |
| midrelease-conflict-dispat | 14/14 | 14/14 | 14/14 |
| midrelease-conflict-lerna | 2/5 | 2/5 | 2/5 |
| midrelease-conflict-nx | 2/6 | 2/6 | 2/6 |
| midrelease-conflict-changesets | 3/5 | 3/5 | 3/5 |

Every step's exit code agrees between the two 1.7.2 runs as well.
These are the first records taken after the harness review of
2026-09-04 fixed all 22 of its findings (the observer no longer fetches
into the clone under test, the proxy denies by exact path segment and
forwards chunked uploads, the shim's marker is atomic and its log is
one JSON object per call, the entrypoint no longer masks exits, fixture
dates are pinned); a local rerun on 1.7.1 with the fixed harness had
already matched the 1.7.0 records cell for cell.

## E1 on the v1.7.2 image

`campaign.log` beside this file. Golden gate PASS. Core profile:
1000/1000 (seeds 1..1000) and 500/500 (seeds 5001..5500) exact. Full
profile: 1000 instances, 412 clean, PG1 409 / PG2 240 / PG2x 58 / PG3
390; 500 instances, 222 clean, PG1 182 / PG2 135 / PG2x 23 / PG3 200;
nothing unclassified. Per-seed rows are identical to the 1.7.0 campaign
on all 3,000 instances, only the version string differs, which is
expected: the 1.7.0 to 1.7.2 diff touches no planner code (1.7.1 moved
the tiny binaries to the fork at 0.43.0-net.1; 1.7.2 changed the release
pipeline, the announcement and the tooling). Records in `e1-core/` and
`e1-full/`.

## E3a on the v1.7.2 image

`e3a/gcn.json` and `e3a/cc.json`, k=5 each, run from the `runtime` image
built on `dispat-alpine:1.7.2`. Every row is identical to the v1.6.0
campaign's (the last one that ran E3a): google-cloud-node 36 of 42
released package-versions exact with the same six misses and the same
extra packages per release; conventional-changelog the same per-release
exact/missing sets (lerna's implicit cascade is what the misses are).
Only the version string differs.

## E4 on the v1.7.2 image

`e4/rep1` and `e4/rep2`, run from the `runtime` image on a shared Apple
silicon host that was also running the docs and Go gates at the time, so
the absolute timings are a loaded-host reading; the paper's headline
range is still the v1.4.0 five-repetition campaign.

| cell | rep1 median s | rep2 median s | v1.4.0 range |
|---|---|---|---|
| 100 layered | 0.41 | 1.09 | 0.6 |
| 1,000 layered | 5.0 | 10.0 | 2.8 to 6.7 |
| 10,000 layered (19,919 edges) | 209.4 | 215.1 | 110 to 149 |
| 1,000 chain | 7.5 | 8.6 | about the layered cost |
| 10,000 chain | 206.1 | 219.8 | |
| 1,000 star | 7.9 | 4.7 | |
| 1,000 layered, 1,000 units | 27.3 | 24.5 | |
| 1,000 layered, 5,000 padding commits | 129.0 | 31.2 | |

The shape is the paper's: super-linear at the top end where per-package
git subprocess costs dominate, and the chain within a factor of two of
the layered cost at the same size. The padding cell's spread (129 s
against 31 s) is the host, not the planner: the run that took 129 s
overlapped the ten-thousand-package cell of the other gate.

Recovery (`e4c-recovery.json` in both folders): 24 episodes over 20-
and 100-package workspaces at per-publish failure probabilities 0.1 and
0.3, every one converged to an empty plan, in at most 4 runs (rep1) and
5 runs (rep2), against first plans of up to 45 packages. The checker
flagged 2 episodes per repetition (4 of 24); as in every earlier
campaign these are its log-string matching under concurrent output, not
counterexamples to G3, G5 or G6.
