# Campaign status, 9 September 2026

The following fresh executions completed against official Dispat 1.8.2. These are separate from the older saved campaign and are not yet incorporated into the active paper PDF.

| Execution | Result | Evidence |
| --- | --- | --- |
| Locked Linux Docker parser and golden gates | Passed | `parser-gate.log`, `golden-gate.log` |
| Restricted core holdout, seeds 90001–90300 | 300 accepted and matching, no invalid/rejected cases | `core/`, `core-holdout.log` |
| Recovery, 20 episodes | All converged; maximum 5 runs; all made progress each run | `recovery/results.json`, 254 raw command records, `recovery/verification.json` |
| npm → Docker → Docker, six repetitions of five configurations | 30 cases, 405 verifier assertions; 12 successful repairs; 24 final no-op checks | `mixed-docker/run-20260908-224925/`, `mixed-docker/verification.json` |
| Fixed CI entrypoint, adding specification and executable consumer | Three repetitions, 81 assertions | `integration/results/verification.json` |

The mixed experiment includes deliberately failed publications and a missing-barrier control. Those expected nonzero outcomes are part of the result, not excluded failures. Each mixed run independently queries its local npm and Docker registries. The verifier checks ordering using event timestamps rather than concurrent append order. Artificial delays expose stage overlap; they are not production throughput measurements.

`mixed/mac-verification.json` records a separate 30-case macOS control run. `core-prior-runtime/` and `recovery-original-harness/` preserve preceding executions. Do not pool these with the canonical Linux evidence as independent populations.

## Environment and setup attempts

`docker/Dockerfile` pins both base images and `docker/apk.lock` pins all installed Alpine packages. `docker/runner-image.json` identifies the measured runner. `binary-provenance.log` records CLI hash and tool versions. The Docker daemon was Docker Desktop on the macOS host; this is a Linux container experiment, not a native Windows validation or bare-metal performance study.

The initial locked-runner attempt lacked a Git author identity. Subsequent recovery setup attempts failed while writing trace records. Their logs are retained as `parser-gate-missing-identity.log` and `recovery-trace-setup-failure*.log`, with the diagnostic script and attempt directories. They did not yield accepted recovery measurements. The final driver explicitly supplies a synthetic author/committer and `init.defaultBranch=main`; the completed recovery run retains each Git/CLI command's output. No seed or failed release episode was removed from the final declared 20-episode sample.

The recovery scheduler chooses deny-list candidates in sorted order before seeded random selection. This corrects dependence on Python set iteration; the earlier harness snapshot remains archived. The progress bound is checked only when every recorded run makes progress. Permanent-failure convergence is not claimed.

## Verification

Run from this directory:

```sh
python3 verify-recovery.py
python3 mixed-docker/verify.py mixed-docker/run-20260908-224925
```

These commands recheck retained observations; they do not rerun releases. Full Docker reproduction instructions are in the research repository's `RESTORATION.md`. New runs must use new output directories. The mixed runner cleans its temporary registries, builder and network; pre-existing host containers are left alone.
