# Anonymous review artifact draft

Start with [REVIEWER-GUIDE.md](REVIEWER-GUIDE.md). Run `python3 verify.py` to check hashes and recompute selected counts from saved records, without network access.

This accompanies *Recoverable Releases Across Package Registries: A Git-Backed Saga Protocol*.

- `results-1.8.2/`: primary campaign records (core/full differential profiles, six specification vectors, orphan recovery, repository replay, eight timing cells, and three fault experiments).
- `comparison-1.7.2/`: preserved earlier release-tool fault records; competitor cells were not rerun on 1.8.2.
- `harness/`: experiment scripts prepared for the 1.8.2 campaign, including the restricted reference oracle. This oracle is not a full implementation of the paper's current model.
- `MANIFEST.json`: per-file hashes of the review copies and original inputs. Sanitization changes author-specific paths and repository identifiers, not measured values. Embedded original hash manifests describe originals and need not match sanitized files.

This includes an executable offline checker, but is an incomplete replication artifact draft for review, not a complete archival replication release. Binaries, Git repositories, images, compressed dossiers, environment inventories and files larger than 2 MB are omitted. Author-identifying image/repository paths are placeholders. The full originals remain preserved locally; do not treat the review-copy hash list as a replacement for the campaign's original 753-artifact manifest. No new experiment was run to create this bundle. The primary campaign README documents refusal handling and coverage limitations. Complete archival provenance and executable setup are still required before an accepted-paper artifact evaluation.
