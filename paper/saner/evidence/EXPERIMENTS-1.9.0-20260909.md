# Dispat 1.9.0 SANER experiment evidence — 2026-09-09

## Scope and immutable identity

This note aggregates the completed campaign `run-v1.9.0-linux-arm64-20260909-corrected`. It is a separate campaign against the released Linux ARM64 Dispat 1.9.0 binary. Its 14 provenance stages passed and its `COMPLETE` marker is present. It ran from 2026-09-09 09:40:14 UTC to 10:48:01 UTC.

- version output: `dispat 1.9.0 (linux_arm64)`
- binary SHA-256: `be3370c472cdbfe66fe4256d3fc1ff78ff19bdd5f041ef222187a52767fa4f35`
- ARM64 image: `yohimik/dispat-alpine@sha256:bf89800987e88a14683fb86b7dede7e9de1fedef82a454b8669655db98096d35`
- multi-architecture index: `yohimik/dispat-alpine@sha256:68b86c1a2508771420d6ac63503b71967228227efe3303f6f9a3f8aa90ea1520`
- runner image ID: `sha256:97363c9dbac292599987e66241d6da56abd7540df965b24bc20d20573fcac31f`
- gated source commit: `8402051e`; release commit: `37610088`
- release workflow: `https://github.com/yohimik/dispat/actions/runs/34302770429`

## Verified outcomes

The parser gate and frozen golden test passed.

The core differential holdout covered exactly seeds 90001–90300. All 300 rows were accepted and matched the reference oracle: 300 accepted matching, zero semantic rejections, zero invalid executions, zero rows with differences, and no divergence classes. This is 300/300 for this fixed sample, not a universal correctness result.

The recovery holdout retained 20 episodes. All 20 converged, preserved the checked invariant, and made progress on every run. Convergence required at most four runs. The verifier counted 248 raw command records. The run-count distribution was nine episodes in two runs, six in three runs, and five in four runs. There were no retained invariant errors.

The original three-node mixed topology covered five configurations × six repetitions = 30 executions. The six mixed and six serialized controls succeeded initially. The 18 injected-negative executions failed as expected: six missing-barrier, six base-publication-failure, and six app-build-failure cases. The 12 repair executions succeeded. All 24 cases eligible for a final unchanged run succeeded without repeating build or publication stages; the six missing-barrier cases intentionally had no final run. The verifier passed 522 repeated checks. In the six mixed fixtures, the observed local base-build/npm-publication overlap ranged from 0.101969 to 0.128675 seconds.

The separate four-node extension used assets (npm) → UI (npm) → base (Docker) → app (Docker), again with five configurations × six repetitions = 30 executions. Its initial, negative, repair, and unchanged outcomes had the same 12/18/12/24 counts as the three-node topology. The verifier passed 798 repeated checks, including both published npm versions, declared assets dependency, local-output propagation into both OCI artifacts, exact seeded ordering, injected failure codes, absent tags after failure, repair, and no-op behavior. In all six mixed fixtures, UI build overlapped delayed assets publication by 0.068203–0.077008 seconds. Base build began 6.298757–6.311191 seconds before UI publication ended and completed before UI publication began in all six observations. The latter is an admissible observed schedule showing the build did not wait for UI publication; positive base-build/UI-publication overlap is not claimed as a universal condition.

The CI integration fixture ran three repetitions and its verifier passed 81 repeated checks. Each repetition covered baseline publication, specification change, consumer change, an injected failed test, a missing-test negative, repair, and an unchanged run. Thus the retained negative observations comprise three failed-test and three missing-test cases; both stopped release stages, and the failed-test cases wrote no release tags. Repairs propagated the specification release to the consumer, while unchanged runs executed tests without release stages.

Verifier check totals are implementation checks repeatedly applied to fixtures. They are not statistically independent observations and must not be summed as an assertion count about the system.

## Retained failed attempt and interpretation limit

The earlier `run-v1.9.0-linux-arm64-20260909` remains a failed attempt, from 05:35:36 UTC to 07:37:14 UTC. Its final four-node verifier stage exited 1 because the original oracle incorrectly required strict base-build/UI-publication interval overlap. Its traces instead showed the valid schedule in which base build completed before UI publication began. The corrected predicate was frozen before the new full campaign: base build must start before UI publication ends, while overlap versus completed-before-start is reported descriptively. The failed attempt has no `COMPLETE` marker and must not be promoted to a formal passing result.

The two campaigns are not pooled. Even with fixed cases and the same schedule seed, runtime scheduling can differ: for example, the failed attempt's recovery evidence had a maximum of five runs and 251 raw command records, whereas the completed campaign had four and 248. The completed campaign is the confirmatory 1.9.0 dataset; the failed attempt documents the oracle correction and remains separate provenance.

These observations support results for the frozen fixtures, seeds, platform, and released binary. They do not establish scientific theorems, universal scheduler timing, or causal claims about the new feature.

## Evidence locations and audit commands

Campaign root:

`experiments/saner-2027/campaign-next-release-prepared/runs/run-v1.9.0-linux-arm64-20260909-corrected`

Retained failed attempt:

`experiments/saner-2027/campaign-next-release-prepared/runs/run-v1.9.0-linux-arm64-20260909`

The aggregation was checked from `provenance.json`, `COMPLETE`, `work/core/e1-core-90001-300.json`, `work/core/verification.json`, `work/recovery/{results,verification}.json`, both `work/mixed-*/run-*/{results,verification}.json` files, and `work/integration/results/verification.json`. Representative read-only commands:

```sh
python3 -m json.tool runs/run-v1.9.0-linux-arm64-20260909-corrected/provenance.json
python3 -m json.tool runs/run-v1.9.0-linux-arm64-20260909-corrected/work/core/verification.json
python3 -m json.tool runs/run-v1.9.0-linux-arm64-20260909-corrected/work/recovery/verification.json
python3 -m json.tool runs/run-v1.9.0-linux-arm64-20260909-corrected/work/mixed-docker/run-20260909-094025/verification.json
python3 -m json.tool runs/run-v1.9.0-linux-arm64-20260909-corrected/work/mixed-4node/run-20260909-103333/verification.json
python3 -m json.tool runs/run-v1.9.0-linux-arm64-20260909-corrected/work/integration/results/verification.json
```

## Archive reproduction check

The coordinator extracted the complete corrected `work.tar.gz` into a separate temporary directory and reran the core, recovery, three-node, and four-node verifiers in the immutable runner with networking disabled. All four passed. The archive SHA-256 is `664b0b118412660fd6c643859e80a61deb60c94a14d9c3e723e2df18eaf6df41`; all 9,190 regular files were also checked byte-for-byte against the retained work tree before extraction. See `ARCHIVES.md` for restoration instructions.
