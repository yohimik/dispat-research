# Dispat release-protocol research

Private working repository for the papers, reproducible experiments, and review evidence. The active conference manuscript targets SANER 2027. It has not been submitted to SANER.

## Start here

- [English conference paper source](paper/saner/SOURCE.md), canonical for current editing.
- [Current conference PDF](output/pdf/saner-2027-paper.pdf).
- [Editing requirements](paper/saner/EDITING-REQUIREMENTS.md).
- [Research and venue report](output/saner-2027/research-report.md).
- [Experiment archive](experiments/README.md), containing historical campaigns with their original versions and limitations.
- [September 9 experiment extension](experiments/saner-2027/PLAN.md). Results from this extension are separate from the measurements already reported in the PDF; consult its campaign status before citing them.
- [Full English technical report](paper/main.tex), separate from the active conference revision.

Read the source notes before editing older conference drafts under `paper/icse/` or `output/conference-submission-2026-09-09/`. Submission and withdrawal receipts there are historical evidence, not a current submission.

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

Experiment scripts, inputs, raw observations, failed setup attempts, image/package pins, and verification scripts are retained. Docker is the preferred environment for new experiments; historical macOS measurements remain explicitly historical. Docker on a Linux VM does not validate native Windows execution.

[Restoration instructions](RESTORATION.md) explain replay fixtures, nested Git metadata, and the Docker runner. Some older scripts and records contain their original absolute paths. Preserve those records; adapt paths only in a new runner or run directory.

## Scope and privacy

This is an English-only copy of the research material from the Dispat workspace and its sibling experiment directory. The originals were retained, including the Russian material excluded at the user’s request. `provenance/migration.json` inventories copied files and exclusions. Patent and lawyer files, credentials, dependency caches, and downloaded third-party articles are not part of this repository. Bibliographic metadata and source links are retained. External replay repositories have exact revision/tag locks and a restoration script.

Keep this repository private. It contains identifiable research history and is not an anonymous conference artifact. An anonymized submission artifact must be prepared separately. Do not submit, publish, or change repository visibility automatically.

## Licensing

The existing [paper license](paper/LICENSE) is retained. Vendored sources retain their own license files and notices. Private storage does not change their licenses or grant additional redistribution rights. This repository does not impose a new blanket license on material with different existing terms.
