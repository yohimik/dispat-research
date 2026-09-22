# Dispat release-protocol research

Private working repository for the papers, reproducible experiments, and review evidence. The active conference manuscript targets SANER 2027. It has not been submitted to SANER.

## Start here

- [English conference paper source](paper/saner/SOURCE.md), canonical for current editing.
- [Current conference PDF](output/pdf/saner-2027-paper.pdf).
- [Editing requirements](paper/saner/EDITING-REQUIREMENTS.md).
- [Research and venue report](output/saner-2027/research-report.md).
- [SANER literature and paper review](output/saner-2027/conference-review-20260910/REVIEW.md), emphasizing recent CI/release-related papers and verified award examples.
- [Supplementary recovery-mechanism results](experiments/saner-2027/campaign-mechanisms-20260910/RESULTS.md): 140 Docker cases, a finite model projection, and an explicit source-window counterfactual; [protocol](experiments/saner-2027/campaign-mechanisms-20260910/PROTOCOL.md) and [reproduction](experiments/saner-2027/campaign-mechanisms-20260910/README.md).
- [Distributed-execution evidence, 22 September 2026](experiments/distributed-20260922/evidence/README.md): raw logs, receipts and fork snapshots of the Linux kernel parity pairs and the LLVM dependent-build pair on Compute Engine, with a hash manifest; one repetition per side, no general speedup claimed. The reproduction kit is being prepared beside it in `experiments/distributed-20260922/`.
- [Reproducibility audit, 22 September 2026](experiments/REPRODUCIBILITY.md): per-family status (exact, recipe, historical), rerun commands, fresh reruns into `experiments/results/repro-20260922/`, and the gaps that still block exact reproduction on a fresh machine.
- [Experiment archive](experiments/README.md), containing historical campaigns with their original versions and limitations.
- [Released 1.10.0 experiment evidence](paper/saner/evidence/EXPERIMENTS-1.10.0-20260909.md), with the completed 14-stage Docker campaign, separate diagnostics checks, and verified archives.
- [Historical 1.9.0 evidence](paper/saner/evidence/EXPERIMENTS-1.9.0-20260909.md), including the preserved failed oracle attempt and corrected campaign.
- [Campaign protocol and reproduction](experiments/saner-2027/campaign-1.10.0-20260909/CAMPAIGN-PLAN.md) and [complete evidence archives](experiments/saner-2027/campaign-1.10.0-20260909/ARCHIVES.md).
- [Technical report, condensed edition](output/pdf/technical-report.pdf) (main findings, model, proofs, departures, results; source [paper/report.tex](paper/report.tex)) and its [extended edition](output/pdf/technical-report-extended.pdf) (source [paper/main.tex](paper/main.tex)), built from the same section files; separate from the active conference revision. Build with `cd paper && make check && make check-report`.

The obsolete `paper/icse/` working tree is preserved in a [verified archive](paper/archives/README.md). Historical submission and withdrawal receipts remain under `output/conference-submission-2026-09-09/`. These are historical evidence, not a current submission.

## Build the English conference PDF

Requires Tectonic, Python 3, and Poppler. Run from this repository:

```sh
cd paper/saner
mkdir -p build
tectonic -X compile main.tex --outdir build --keep-logs
python3 check.py
pdftoppm -scale-to 1600 -png build/main.pdf build/page
```

Inspect all rendered pages after edits. The target is exactly ten content pages plus two reference pages. Copy a verified new build to `output/pdf/saner-2027-paper.pdf`; do not change an old run's evidence to match newer prose.

## Reproducibility

Experiment scripts, inputs, raw observations, failed setup attempts, image/package pins, and verification scripts are retained. Docker is required for new experiments; historical macOS measurements remain explicitly historical. Docker on a Linux VM does not validate native Windows execution.

[Restoration instructions](RESTORATION.md) explain replay fixtures, nested Git metadata, and the Docker runner. Some older scripts and records contain their original absolute paths. Preserve those records; adapt paths only in a new runner or run directory.

Generated build files, page previews and verified extracted copies of campaign archives were removed during the [10 September cleanup](provenance/cleanup-2026-09-10.json). Final PDFs, verification records, raw observations and failed attempts remain. IDE settings are local and ignored.

## Scope and privacy

This is an English-only copy of the research material from the Dispat workspace and its sibling experiment directory. The originals were retained, including the Russian material excluded at the user’s request. `provenance/migration.json` inventories copied files and exclusions. Patent and lawyer files, credentials, dependency caches, and downloaded third-party articles are not part of this repository. Bibliographic metadata and source links are retained. External replay repositories have exact revision/tag locks and a restoration script.

Keep this repository private. It contains identifiable research history and is not an anonymous conference artifact. An anonymized submission artifact must be prepared separately. Do not submit, publish, or change repository visibility automatically.

## Licensing

The existing [paper license](paper/LICENSE) is retained. Vendored sources retain their own license files and notices. Private storage does not change their licenses or grant additional redistribution rights. This repository does not impose a new blanket license on material with different existing terms.
