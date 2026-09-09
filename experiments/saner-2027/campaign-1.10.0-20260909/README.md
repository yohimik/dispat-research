# Completed dispat 1.10.0 research campaign

`runs/run-v1.10.0-linux-arm64-20260909` completed all 14 stages on 9 September 2026, 17:02:20–17:11:00 UTC. The process survived the app restart; no replacement attempt was needed. The pre-execution plan and FREEZE.json remain unchanged.

- `summary.json`: reaggregated counts with separate units.
- `release-lock.json`, `identity-measurements.json`: immutable released binary, image and toolchain identity.
- `protocol/`, `protocol-sha256.json`: frozen corrected protocol copied unchanged from 1.9.0.
- `runs/run-v1.10.0-linux-arm64-20260909/provenance.json`: all stage commands/timestamps/outcomes.
- `runs/run-v1.10.0-linux-arm64-20260909/work.tar.gz`: complete retained work, including fixture Git metadata; 9,157 regular files verified against the work tree.
- Archive SHA-256: `835208a0cd9066ec6bf7ec424a4d9cdee06ca4482a061f7a7d7cc02738611793`.
- `runs/run-v1.10.0-linux-arm64-20260909/archive-verification/`: four offline verifiers passed from a fresh extraction.
- `runs/run-v1.10.0-linux-arm64-20260909/recovery-comparison.json`: trace explanation for 251 commands versus historical 248.
- `diagnostics/`: separately frozen 16-case engineering addendum, all passed, outside scientific sample counts.
- `SHA256SUMS.json`: checksums of retained campaign files outside ignored expanded work trees.

The evidence report is `../../../paper/saner/evidence/EXPERIMENTS-1.10.0-20260909.md`. Prior 1.9.0 attempts and older measurements remain separate. Publication failures/missing barriers are designed controls, not omitted observations. Artificial delays do not measure throughput; this campaign does not validate native Windows equivalence.

Reaggregate from the repository root with `python3 tools/summarize-saner-campaign.py experiments/saner-2027/campaign-1.10.0-20260909/runs/run-v1.10.0-linux-arm64-20260909`. Restore archives into a separate directory; do not overwrite raw work. The archive and verifier tools refuse overwriting existing evidence. See ARCHIVES.md and the evidence report for the archive review workflow.
