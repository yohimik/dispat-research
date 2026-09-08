# Dispat 1.8.2 campaign: complete

Completed 7 September 2026. All E1–E5 stages and eight completion markers passed. Official released ARM64 image and binary verified; immutable CLI commit a7011cbcb9e88e52e7336f6fc8f1b207a8e7a311.

Results: /Users/yohimik/Projects/dispat-experiments/results/v182-20260907. Validated interpretation: README.md in that directory. Machine summary: output/experiments-v182-summary.json. All 753 execution artifacts verified. All 216 historical 1.8.1 artifacts preserved. First stopped attempt retained, not overwritten.

E1 core 1500/1500; full 997 accepted (546 matching) and 503 validated E195 refusals, 550 diagnostic-clean overall, 1914 classified row differences. No unknown or invalid executions. Six selected CCME2 vectors pass. E2 two repetitions pass. E3 historical replay36/42 and7/64. E4 24/24 recoveries and eight timing cells pass. E5 three fresh Dispat cells pass8/12/14 checks; nine competitor cells remain historical.

Canonical EN updated then RU then patent technical description. All four PDFs rebuilt and changed measurement pages visually reviewed; conference EN9/RU10 pages; reports EN39/RU45 pages. Final reference and overflow checks clean. Existing conference fallback for unavailable italic monospace font remains, with rendered text legible.

Lawyer note section16 appended; all prior221006bytes preserved. Patent claims and following legal sections byte-identical to baseline. Final artifact hashes: output/experiments-v182-final-hashes.json. Nothing committed or pushed. No code, parser, configuration, or release mutations.

Methodological limits: old oracle is CCME1; rejected diagnostics are not executable/conformance plans; E1 tmpfs/pre-fsck/exitchecker hardening prevents attributing seed580success to runtimechange. Planner source unchanged. Performance observations host-sensitive. CCME3.0.1 spec references retained; runtime/parserCCME2, no VCS/rollback implementation claim.
