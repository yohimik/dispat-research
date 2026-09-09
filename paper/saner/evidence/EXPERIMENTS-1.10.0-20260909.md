# dispat 1.10.0 SANER experiment evidence — 2026-09-09

## Completed campaign and immutable identity

The current conference dataset is `run-v1.10.0-linux-arm64-20260909`, in `experiments/saner-2027/campaign-1.10.0-20260909/runs/`. It ran from **2026-09-09T17:02:20.892329+00:00** to **2026-09-09T17:11:00.123940+00:00**. All 14 stages passed and the COMPLETE marker is present. The process survived the requested app restart; it was neither interrupted nor restarted. There is one 1.10.0 attempt, with intentional negative controls retained within it.

- Exact version: `dispat 1.10.0 (linux_arm64)`.
- Official ARM64 image: `yohimik/dispat-alpine@sha256:f2a49c21eca0a3e30af1396eca538920b2faa475b50f12d4aae99236e2fe2955`.
- Image index: `yohimik/dispat-alpine@sha256:c7c03077f20d5763316d75ed22ba9ece0ec2908167a69747e56c35e5855e1af8`.
- Binary SHA-256: `03d1ba5fbaef35b69582e9489f40b5438f81ae6926e02ea6d02716b5b73d92fd`.
- Runner ID: `sha256:6f92932fbba5d33d61d777073f5fc155133063f4c3d4b2f950e3e5b9ed9a263e`.
- Release-lock SHA-256: `b01914fc4f72919dff59e20d85a76139ed0e008b00fae628ab0116f10875b02b`.
- Protocol-manifest SHA-256: `a3366e2fbdc590be7e8f6268bc7390146669cf7a0395837c2531a0af5554dcaa`.
- Gated source: `1bb3b397e4749461c1102869a56b1ceb600636ae`.
- CLI release commit: `7a96ae956de4d1682c61e6b73e50c06401e031f7`; final image/docs commit: `66cffcdae1fa8910ce3672f840ec5d0ea1fd1679`.
- Successful release: https://github.com/yohimik/dispat/actions/runs/34373760312.

`identity-measurements.json` retains measured commands and outputs; `FREEZE.json`, `release-lock.json`, `protocol-sha256.json` and the run's `provenance.json` identify the frozen inputs. The driver, protocol, Dockerfile and complete Alpine package lock were copied byte-for-byte from the corrected 1.9.0 protocol. Main containers use two CPUs and 4 GiB. Core, recovery and CI run without networking; mixed topologies publish to disposable private registries on Docker Desktop Linux ARM64.

The evaluated parser remains CCME 2.0.0. Specification 3.0.2 contains features outside the implemented fragment; the new standalone diagnostics command is not a change to the release model or an additional theorem. `release-source-review.json` records pinned-source inspection: the inspected release implementation, parser and conditional-command implementation did not change between the release tags. The conditional wrapper still defaults to a POSIX shell. Native Windows equivalence is not tested here.

## Verified observations and counting units

| Scope | Observations | Outcome | Repeated verifier checks |
|---|---:|---|---:|
| Core histories | 300 | 300 accepted matches; 0 refusals, invalid executions, or differences | Integrity accounting, not an independent sample count |
| Recovery episodes | 20 | All converged; progress on every run; at most 4 runs; 251 raw command records | Selected version/pending-set predicates |
| Three-package topology | 30 initial executions | 12 initial successes, 18 designed failures, 12 successful repairs, 24 successful unchanged no-op runs | 522 |
| Four-package topology | 30 initial executions | Separately, 12 initial successes, 18 designed failures, 12 successful repairs, 24 successful unchanged no-op runs | 798 |
| CI fixture | 3 repetitions | Required-test selection, failing/missing-test refusal, repair, unchanged release | 81 |

Parser and golden gates passed. Core seeds are exactly 90001–90300. Recovery includes both requested graph sizes (20 and 100), both failure probabilities (.1 and .3), and seeds 100–104. Nine episodes completed in two runs, five in three, and six in four; no invariant errors were retained. The maximum is an observation, not a universal liveness bound.

Each topology repeats mixed, serialized, missing-barrier, base-publication-failure and app-build-failure configurations six times in the frozen seeded order. The 18 designed failures per topology comprise six of each negative configuration. All 12 repairable executions completed at unchanged planned versions. Six missing-barrier cases per topology intentionally have no repair/final unchanged release. The other 24 completed cases performed no build/publication on the final unchanged release. Registry contents, tags and artifact contents were checked.

In the three-package mixed fixtures, base build overlapped npm publication in all six observations, ranging **0.110716–0.151483 seconds**. In the four-package mixed fixtures, UI build overlapped delayed assets publication by **0.070128–0.073725 seconds**. Base build started **6.292152–6.393487 seconds** before UI publication ended and completed before UI publication began in all six cases. This is an admissible schedule demonstrating local-output availability; strict overlap with UI publication is not required. Artificial delays expose stage availability and are not production throughput measurements.

The three CI repetitions include three failing-test and three missing-required-test negatives, which block release stages; failing-test attempts write no release tags. Repairs propagate a specification change to its consumer. Unchanged invocations execute selected tests without release stages. This is a controlled integration fixture, not measured onboarding effort.

Histories, recovery episodes, the two topologies, CI repetitions and repeated predicates remain distinct units. No pooled success rate or independent replication claim is made.

## Difference from the preserved 1.9.0 campaign

The completed 1.9.0 run remains in `campaign-next-release-prepared/runs/run-v1.9.0-linux-arm64-20260909-corrected`, with its original 248 command records and 9/6/5 run distribution. The 1.10.0 observations are not a relabeling or pooled extension of it.

`runs/run-v1.10.0-linux-arm64-20260909/recovery-comparison.json` identifies the extra attempt in requested graph size 100, failure probability .3, seed 100. Initial versions and the first denied-package set match. The first attempt leaves 20 packages pending in 1.10.0 versus 18 in 1.9.0; p00063 and p00099 additionally remain pending. The subsequent remaining counts are 20→2→1→0 versus 18→2→0. Later failure draws use the changing pending set, so the seeded deny sets then differ. One additional release/tag/status triplet accounts for the three extra raw commands. These traces do not establish that diagnostics caused the difference, nor do fixed seeds guarantee identical concurrent execution schedules.

The first 1.9.0 attempt remains a failed oracle attempt, without COMPLETE. Its invalid strict-overlap predicate rejected a valid base-build-completed-before-UI-publication schedule. The predicate was corrected before the complete 1.9.0 rerun; this 1.10.0 campaign uses that corrected frozen protocol without further oracle changes. Both old attempts and their archives remain intact.

Saved 1.8.2 full-profile diagnostics, scale cells, targeted vectors, and historical competitor/replay measurements were **not rerun on 1.10.0** and remain explicitly historical in the paper. The restricted core oracle does not establish full semantic conformance or implementation refinement of the mathematical model.

## Separate diagnostics engineering addendum

`diagnostics/` contains a separately frozen script, provenance, all raw stdout/stderr/exit observations, and verification: **16/16 purpose-selected cases passed**. It checks valid, warning, invalid, empty and multiline literal messages; leading-dash input and lack of Git comment cleanup; explicit referenced parser configuration; malformed/missing explicit configuration; nearby malformed configuration ignored in default mode; quiet JSON warnings; and usage errors. The fixture has no Git repository, no Git on PATH, and no network, and its files remained unchanged.

These engineering checks are outside the 14-stage campaign and its scientific sample counts. They support the bounded diagnostics description, not a claim that syntax validity establishes scope existence, a correct release plan, authorization, or all possible absence of internal operations.

## Archive integrity and reproduction

- Complete retained work archive: `runs/run-v1.10.0-linux-arm64-20260909/work.tar.gz`.
- SHA-256: `835208a0cd9066ec6bf7ec424a4d9cdee06ca4482a061f7a7d7cc02738611793`.
- Size: 3,380,083 bytes; **9,157 regular files verified byte-for-byte**, including retained fixture Git metadata.
- Fresh extraction plus all four offline retained-data verifiers passed in the exact runner. Records are under `archive-verification/` within the run.
- `summary.json` is the reaggregation used above; raw verdicts remain in `work/core`, `work/recovery`, `work/mixed-docker/run-20260909-170231`, `work/mixed-4node/run-20260909-170554`, and `work/integration/results`.

From the repository root, reaggregate the retained local work tree:

```sh
python3 tools/summarize-saner-campaign.py experiments/saner-2027/campaign-1.10.0-20260909/runs/run-v1.10.0-linux-arm64-20260909
```

The tools `archive-campaign.py` and `verify-saner-archive.py` deliberately refuse overwriting existing evidence. To repeat extraction verification, copy the completed run metadata and archive to a new review directory without its existing `archive-verification/`, then run `python3 tools/verify-saner-archive.py /absolute/path/to/review-run`. Offline verification rechecks retained observations; it is not another execution or independent scientific replication.

The private source repository and historical paths are identifiable. No conference submission or public artifact publication occurred. Author review, anonymity-history assessment and exact AI-model-name confirmation remain separate pre-submission decisions.

## Verified manuscript delivery

`output/pdf/saner-2027-paper.pdf` has exactly ten content pages plus two references-only pages, with 40 references. All twelve pages were rendered and visually inspected. PDF SHA-256: `b695e2d5b28adc1c65e4ac6d404226fae67cad1e00dfbdd956bae12105ebbf60`. Source and render hashes and the layout review are recorded in `PDF-1.10.0-20260909.json` beside this report.
