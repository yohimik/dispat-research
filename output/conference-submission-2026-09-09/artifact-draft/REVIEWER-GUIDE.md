# Reviewer guide

This artifact supports the evaluation of *Recoverable Releases Across Package Registries: A Git-Backed Saga Protocol*. It contains recorded observations and the harness used to produce them. It is a review draft, not the complete executable replication package.

## Start here

Download and extract the repository, then run from its root:

```sh
python3 verify.py
```

Python 3.8 or later is sufficient. The command uses only the standard library. It reads local files, checks the review-copy manifest, recomputes selected counts from individual records, and exits nonzero if a check fails. It does not use the network, install packages, invoke Dispat, or rerun experiments. A passing result validates consistency of the supplied observations; it is not independent reproduction or a proof of the protocol.

## Evidence map

| Paper evidence | Files | Interpretation |
| --- | --- | --- |
| E1 restricted core agreement | `results-1.8.2/e1/core-*/e1-core-*.json` | Two disjoint seed batches, 1,500 instances, all matching the restricted historical oracle. |
| E1 full profile | `results-1.8.2/e1/full-*/e1-full-*.json` | 1,500 cases; 997 accepted and 503 E195 refusals. The 550 matching diagnostic comparisons include four refused cases. The 1,914 differing rows are classified heuristically, not established defects. |
| Selected specification vectors | `results-1.8.2/e1/ccme2-vectors.json`, `ccme2-vectors-evidence/` | Six targeted vectors (133-138), each with fixture and parsed/output evidence. This is not full specification conformance coverage. |
| E2 orphan recovery | `results-1.8.2/e2/dispat-rep*/` | Two isolated repetitions, including logs, plans and verdicts. |
| E3 repository replay | `results-1.8.2/e3/cc.json`, `gcn.json` | Historical release observations for conventional-changelog and google-cloud-node. These are comparisons, not assertions that the historical projects used this protocol. |
| E4 recovery | `results-1.8.2/e4/rep*/e4c-recovery.json` | 24 episodes, each converged within four runs under the tested failure schedules. |
| E4 scale | `results-1.8.2/e4/timing.csv` and neighboring records | Eight cells, 100-10,000 packages. Host-sensitive timings, not a controlled speedup claim. |
| E5 current Dispat fault experiments | `results-1.8.2/e5/*/verdict.json` and neighboring logs | Orphan, clean competing push and conflicting competing push. Each verdict names the checks and their outcomes. |
| Earlier competitor comparison | `comparison-1.7.2/` | Historical pinned-tool results; competitor cells were not rerun in the 1.8.2 campaign. |
| Experiment logic | `harness/e1/` through `harness/e5/` | Frozen campaign scripts for inspection. See their imports and commands before attempting reproduction. |

The proofs and their assumptions are in the submitted paper. This bundle does not contain machine-checked proofs. The reference oracle in `harness/e1/oracle.py` implements a restricted historical model, not every feature of the current specification.

## Integrity, redaction and limits

`MANIFEST.json` records the SHA-256 of each included review file. Original campaign files also carry `source_sha256`, computed before redaction. Review-only helper files have no original campaign hash. The manifest deliberately excludes itself. Author paths, email domains and repository/image owner identifiers were replaced with non-resolving placeholders. Measurements, seeds, event outcomes and tool versions were retained.

Embedded checksums in the original records refer to unredacted originals and may not match these copies. References to omitted directories, image names and local paths in historical logs are provenance, not runnable download instructions. Original Git object IDs and release digests remain for traceability and may enable deliberate reidentification. No claim of anonymity against such investigation is made.

Binaries, full Git histories, container images, environment inventories, compressed dossiers and individual files larger than 2 MB are omitted. Some E195 dossier files exceed this review cutoff; the E1 aggregate records retain every seed and classification. Thus this draft supports inspection and offline aggregation but not full end-to-end reproduction. The original 753-artifact execution manifest is separate from this curated review-copy manifest. No new experimental run was performed during packaging. Complete archival replication material remains required for later artifact evaluation.
