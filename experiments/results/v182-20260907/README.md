# Dispat 1.8.2 experiment campaign

Completed 7 September 2026 (Asia/Dubai), using official Linux ARM64 release bytes from the immutable image digest in campaign.identity. The extracted binary matches GitHub release asset SHA-256 78b0b37b4b74ed393f366ff4d36a98aa69a48fa781cc6a704ad17a0160107a68. Immutable CLI release commit: a7011cbcb9e88e52e7336f6fc8f1b207a8e7a311.

All eight completion markers match campaign.identity. Finalize/SHA256SUMS validates 753 recorded artifacts.

- E1 core: 1,500/1,500 exact, no invalid executions.
- E1 full: 1,500 cases, 550 matching diagnostic comparisons and 1,914 classified row differences against the historical CCME 1 oracle. 503 cases are explicit E195 version-regression refusals, not executable release plans. Of 997 accepted cases, 546 match. All 503 rejection dossiers preserve and validate raw errors and proposed/baseline versions. There are no invalid executions or unknown row differences in the fresh campaign.
- CCME 2 vectors 133–138: 6/6 pass. These targeted checks are separate from the historical-oracle comparison.
- E2: two isolated orphan recovery repetitions pass; failed package untagged, same-version recovery, empty final plan.
- E3: five releases each from google-cloud-node and conventional-changelog; 36/42 and 7/64 exact package-version observations. Metrics reproduce 1.8.1.
- E4: 24/24 recovery episodes converge in at most 4 runs, no G3/G5 checker violations. Eight timing cells cover 100–10,000 packages; medians 0.017–19.354 s, RSS 15–118 MiB, capped at 2 CPUs and 4 GiB. Host-sensitive measurements, not a controlled speedup claim.
- E5: all three fresh Dispat fault cells pass: orphan 8 checks, clean competing push 12, conflicting competing push 14. The nine competitor cells were not rerun and remain historical.

The first attempt is preserved in ../v182-20260907-attempt1 with its frozen harness. Its strict exit checker initially classified expected E195 refusals as invalid; the corrected campaign reran every seed from scratch, distinguishing validated semantic rejection from execution failure. No samples were discarded. E1 uses tmpfs+Git integrity checks; E4 retains the original container filesystem and cells. Do not attribute seed 580's fresh success to a planner change: its earlier 1.8.1 fixture failure remains unresolved historical evidence, and the fixture environment changed. Planner source is unchanged between CLI 1.8.1 and 1.8.2.

The v181 campaign remains byte-identical across all 216 original hashed artifacts. New runner hardening lives only in prepare-v182/harness. Do not mutate that snapshot or this campaign's recorded artifacts; any future run needs a new result directory. This README is post-run interpretation, not part of the 753-artifact execution manifest.
