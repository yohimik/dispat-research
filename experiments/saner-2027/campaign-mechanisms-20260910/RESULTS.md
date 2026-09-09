# Controlled recovery mechanisms: results

The frozen full run completed all 140 generated cases with 140 passes, no failed or invalid cases, and no exclusions. The independently implemented offline consistency check reconstructed every candidate plan from command output, checked tag snapshots and publisher events, validated the four stored artifact identities per case, and independently enumerated the finite model. It reported no discrepancies. This is a consistency check of the retained evidence, not an independent scientific replication.

The run used the newest released CLI, `services/dispat/v1.10.0`, in the pinned Linux ARM64 runner image `sha256:6f92932fbba5d33d61d777073f5fc155133063f4c3d4b2f950e3e5b9ed9a263e`. The binary SHA-256 was `03d1ba5fbaef35b69582e9489f40b5438f81ae6926e02ea6d02716b5b73d92fd`. Docker ran with networking disabled, two CPUs, and 4 GiB RAM. Execution ran from 2026-09-09 20:39:05.988761 UTC through 20:40:59.642604 UTC, taking 113.653827 seconds.

## Observed mechanism checks

| Check | Passed / denominator |
|---|---:|
| Repeated fault preserved the residual plan and tags | 130 / 130 |
| Successful repair left an empty plan | 130 / 130 |
| Exactly one durable artifact write per obligation | 140 / 140 |
| Foreign artifact identity conflict was refused | 10 / 10 |
| Final no-op left the plan empty and tags unchanged | 140 / 140 |

The 130 repeated-fault and repair episodes comprise the 120 primary fault cases and ten separate foreign-identity cases. The ten no-fault controls do not contribute to that denominator. All 120 primary fault cases passed: 40/40 at the build boundary, 40/40 before publication, and 40/40 after the local artifact write. Both stable and beta strata passed 70/70; each graph passed 28/28.

The after-write injector lets the supplied local publisher durably write the artifact and then return a nonzero exit code. It does not simulate `SIGKILL`, a network partition, or power loss. The ten foreign-identity cases test this adapter's immutable content-identity reconciliation, not arbitrary npm or OCI publishers.

## Source-window counterfactual

The source-window ablation is calculated from each case's original obligations and observed completion tags. It does not run a modified binary and is not a competitor comparison. Counts are sensitivity of a deficient analytical rule under deterministic designed cases, not a win rate or independent production samples.

| Case class | Cases | Mutant-losing cases | Lost obligations |
|---|---:|---:|---:|
| Primary fault matrix | 120 | 84 | 111 |
| No-fault controls | 10 | 0 | 0 |
| Foreign-identity cases | 10 | 10 | 10 |
| Total | 140 | 94 | 121 |

| Failure boundary | Cases | Mutant-losing cases | Lost obligations |
|---|---:|---:|---:|
| Build | 40 | 28 | 41 |
| Before publication | 40 | 28 | 35 |
| After artifact write | 40 | 28 | 35 |
| Foreign identity | 10 | 10 | 10 |
| No fault | 10 | 0 | 0 |

| Channel | Cases | Mutant-losing cases | Lost obligations |
|---|---:|---:|---:|
| Stable | 70 | 47 | 61 |
| Beta | 70 | 47 | 60 |

| Graph | Cases | Mutant-losing cases | Lost obligations |
|---|---:|---:|---:|
| Chain | 28 | 20 | 38 |
| Diamond | 28 | 20 | 25 |
| Fan-out | 28 | 20 | 20 |
| Two disconnected pairs | 28 | 14 | 14 |
| Chain with shortcuts | 28 | 20 | 24 |

## Finite projection

The finite analysis enumerated all 64 DAGs consistent with one fixed order of four vertices and each of four single intent sources: 256 source instances, 772 reachable completion states, and 2,270 failure-subset transitions. Of those, 1,054 transitions made progress. The stable residual projection had zero violations. The source-window mutant lost obligations in 260 states.

These state and transition counts are enumeration units, not independent samples. The model is a stable-channel, one-intent projection. It is not a mechanized proof of the full language, arbitrary graphs, or implementation refinement. `model-states.jsonl` records each reachable state and its failure-subset denominator; the offline checker independently reconstructs the transitions because the execution file does not store one row per transition.

## Evidence integrity

The full archive contains 16,464 regular fixture files (8,367,533 uncompressed bytes), including 140 working-repository `.git` directories and 140 bare origins. It was verified byte-for-byte before expanded trees were removed. Archive SHA-256: `0c94a5490f2e22eba90407c37588dd9860b6191f43b132ede6e7807fe3585fda`. A fresh archive extraction was rechecked in the pinned Docker environment and passed all 140 cases.

The historical pilot remains separate: 10/10 cases passed. Its archive contains 1,160 regular files and has SHA-256 `1ffa74155a7af0d1acacca309e4fd593f3805802e1026a55a78f493755a9477b`. `PILOT-FREEZE.json` is the pre-pilot freeze of the original four inputs; `FULL-FREEZE.json` separately freezes the full execution and verification helpers.

A negative check corrupted the case inventory only in a disposable copy while the retained campaign was mounted read-only. The offline checker exited nonzero and reported the case-order mismatch, missing corrupted case directory, and aggregate mismatch. A separate wrapper check refused an attempted reuse of the existing `full-01` name before launching Docker.

Primary evidence:

- `summary.json`: descriptive full-run aggregation and all requested strata.
- `runs/full-01/summary.json`: immutable executor aggregation.
- `runs/full-01/verifier.json`: offline consistency-check result from expanded raw evidence.
- `runs/full-01/archive-replay-verifier.json`: the same check from a fresh archive extraction.
- `runs/full-01/*/commands/*.json` and `runs/full-01/*/observation.json`: per-command and per-case retained evidence.
- `runs/full-01/model-states.jsonl`: finite-state enumeration.
- `runs/full-01/archive-verification.json` and `expanded-fixtures.tar.gz`: file-level archive manifest and complete fixture/Git data.
- `FULL-PROVENANCE.json`, `full-01-execution.jsonl`, and `full-01.log`: release lookup, host/image identity, exact Docker command, timestamps, and execution stream.
- `NEGATIVE-VERIFIER-CHECK.json` and `negative-verifier-check.log`: rejected corrupted-copy check.
- `overwrite-refusal.log`: preserved refusal to reuse an existing run name.
- `SHA256SUMS.json`: SHA-256 and byte length for every retained campaign file except the manifest itself.
