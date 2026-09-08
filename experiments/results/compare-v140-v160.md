# dispat v1.4.0 vs v1.6.0: full campaign comparison

2026-08-31. Both campaigns run the released binary extracted from the
official `yohimik/dispat-alpine` image (v1.4.0 commit 5e3a2337,
v1.6.0 commit f9c2acf2). SPEC.md is byte-identical across both
releases and the old exp-342062d3 pin, so the model, oracle and
vectors are shared. The v1.6.0 diff touches the plan engine
(propagate.go, plan.go, directives.go, vars.go), which made E1 the
decisive test. Instances are process-deterministic since the gen.py
fix, so per-seed rows are directly comparable.

## Verdict

v1.6.0 is plan-equivalent to v1.4.0 on everything measured. The only
observable difference is reporting metadata: plan rows now carry the
complete propagation source set (`dueTo` lists every source; reasons
say "propagated from p07, p12" where 1.4.0 said "catch-up from p07").
Versions, bumps, channels and released sets are identical everywhere.

## Per experiment

| Experiment | v1.4.0 | v1.6.0 | delta |
|---|---|---|---|
| Golden gate | PASS | PASS | none |
| E1 core 1..1000 | 1000/1000 exact | 1000/1000 exact | none |
| E1 core 5001..5500 | 500/500 exact | 500/500 exact | none |
| E1 full 1..1000 | 412 clean; PG1 409 / PG2 240 / PG2x 58 / PG3 390 | same counts | per-seed rows identical |
| E1 full 5001..5500 | 222 clean; PG1 182 / PG2 135 / PG2x 23 / PG3 200 | same counts | per-seed rows identical |
| E2 dispat orphan | no tag on failure, same-version resume, empty 3rd plan; 2 reps identical | same, 2 reps identical | none |
| E3a gcn (k=5) | 36/42 exact | byte-identical JSON | none |
| E3a cc (k=5) | rows as recorded | byte-identical JSON | none |
| E4b headline (5 containers, median-of-medians) | 0.61 / 6.49 / 143.1 s; chain 6.51 | 0.60 / 6.43 / 142.4 s; chain 6.40 | within noise |
| E4c recovery | 24/24 converged, max 5 runs, invariants 18/24 | 24/24 converged, max 4 runs, invariants 19/24 | within episode randomness |

## The one row that needed attribution

Seed 588, package p13 (full profile): classified PG2x under 1.4.0,
initially UNKNOWN under 1.6.0. Replaying the identical instance on
both released binaries shows identical plans (p13 -> 3.6.2 patch on
both); only the dueTo/reason metadata differs. The classifier's
cascade rule keyed on the 1.4.0 phrasing; it now keys on the source
set (a source in the prerelease domain marks the row PG2x), after
which both campaigns classify 100% with identical per-seed rows.
Recorded as harness gotcha 15: plan *metadata* is release-version-
dependent even when plan *semantics* are frozen; classifiers must key
on structure, not phrasing.

## Notes

- v1.5.0 was released between the campaigns and intentionally not
  measured (user asked for 1.6.0).
- Competitor tool versions unchanged since the v1.4.0 campaign
  (lerna 10.0.1, nx 23.1.2, turbo 2.10.12, changesets 3.0.1), so the
  executed competitor phases carry over.
- v1.6.0 also ships the `dispat-tiny-*` TinyGo-fork assets (8 release
  assets, like v1.4.0).
- E4 absolute timings depend on Docker Desktop core placement
  (bimodal across containers; one 0.22 s fast-placement outlier at
  P=100 in the v1.6.0 sweep); the paired sweeps overlap fully.
