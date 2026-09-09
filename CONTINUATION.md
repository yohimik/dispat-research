# Research continuation, 10 September 2026 — SANER adaptation complete

This task owns only `/Users/yohimik/Projects/dispat-research`. The product task `01a06e7b-e8ba-7722-ad9c-c6da024126a8` owns `/Users/yohimik/Projects/dispat`; inspect it read-only when needed and route product defects or changes to that task. The research task is `01a08719-8f24-7201-a5fb-417d1ac98823`.

## Completed work

The user requested recent SANER literature, award examples, conference-suitable experiments, a whole-paper revision preserving the science, ten content pages plus two reference pages, and a review report. The topic is Software Release Engineering, Continuous Integration and Delivery. The user required Docker and Sol for execution; both Sol execution subtasks have finished. No experiment is pending.

Canonical paper: `paper/saner/`. Delivered PDF: `output/pdf/saner-2027-paper.pdf`, SHA-256 `2c3e8ecb868e785400a9c8f22972bc49e30b05e60238dde8ed511dd7f64dd978`. Exactly 10+2 pages, 43 references, normal IEEE 10pt body and 24pt title. All twelve pages were visually inspected. Evidence: `paper/saner/evidence/BUILD-20260910.json` and `PDF-20260910.json`. The model and guarantee sections remain byte-identical to their pre-revision sources.

Current review: `output/saner-2027/conference-review-20260910/REVIEW.md`. It prioritizes SANER 2026 CI contexts, GitHub Actions workflow clones, and CI/CD failure management; award examples inform exposition rather than substitute for technical related work. Primary-source access limits and source hashes are retained in `RESEARCH-PROVENANCE.json`; final integrity checks are in `FINAL-VERIFICATION.json`.

## New Docker mechanism campaign

`experiments/saner-2027/campaign-mechanisms-20260910/`: prospective full matrix 140/140 PASS, with 120 fault cases, ten no-fault controls and ten foreign-content controls. Source-window counterfactual loses 111 obligations in 84/120 fault cases; foreign cases add ten losses separately. Repeated adverse conditions preserve plans/tags in 130/130 cases; all 140 finish with a no-op. This is a deterministic designed matrix, not independent production samples or a modified-binary comparison. The after-write fault is an adapter returning failure after a local write, not a process crash or power loss.

Finite stable-channel projection: 64 ordered four-node DAGs, 256 source instances, 772 states, 2,270 transitions, 1,054 progress transitions, zero projection violations; mutant loses work in 260 states. This is not full implementation refinement or a mechanized proof.

Released CLI remains 1.10.0; the later product 1.10.1 release was documentation-only. Binary SHA-256 `03d1ba5fbaef35b69582e9489f40b5438f81ae6926e02ea6d02716b5b73d92fd`; Docker runner `sha256:6f92932fbba5d33d61d777073f5fc155133063f4c3d4b2f950e3e5b9ed9a263e`. Network disabled, Linux ARM64, two CPUs and 4 GiB RAM. Full archive SHA-256 `0c94a5490f2e22eba90407c37588dd9860b6191f43b132ede6e7807fe3585fda`; 16,464 fixture files preserved, expanded copies removed only after verification. Offline checks and archive-extraction replay pass; a corrupted-copy negative check fails as expected. All 4,896 retained files match the campaign manifest. Pilot 10/10 remains separate. The exact runner exists locally but has no repository image export; README describes the pinned recipe and fresh-machine rebuild limitation.

## Preserved baseline and historical evidence

Original 1.10.0 campaign: `experiments/saner-2027/campaign-1.10.0-20260909/`; all 103 manifest files unchanged. All 14 stages passed: 300 accepted matching core histories, 20 recovery episodes within four runs (251 command records), two separate 30-execution registry topologies, three CI repetitions, and a separate 16-case diagnostics addendum. Per topology: 12 initial successes, 18 designed failures, 12 repairs, 24 no-op reruns. Archive SHA-256 `835208a0cd9066ec6bf7ec424a4d9cdee06ca4482a061f7a7d7cc02738611793`, 9,157 files. See `paper/saner/evidence/EXPERIMENTS-1.10.0-20260909.md`.

The failed 1.9.0 strict-overlap oracle attempt remains preserved. Its correction preceded the corrected run and 1.10.0 reuse. Old 1.8.2 full-profile diagnostics, planning costs and comparisons remain historical; do not pool versions or remove negative evidence. Old dated PDF records remain immutable.

## Scope, remaining decisions, and repository delivery

Native Windows equivalence, real-team effectiveness and full implementation refinement remain unverified and are stated as limits. Before submission the author must assess public/preprint history, verify the exact AI model labels in the disclosure, review the proofs, and decide anonymous artifact distribution. Nothing was submitted, published publicly, or released. The full English technical report is separate; Russian translation and patent/lawyer material are out of scope.

The user authorized committing and pushing this research work to the private `yohimik/dispat-research` repository. Check Git HEAD and origin/main for the completed delivery commit. Prior cleanup is documented in `provenance/cleanup-2026-09-10.json`; obsolete ICSE sources are archived, handoffs are under `provenance/handoffs/2026-09-09/`, and raw failures remain. `RESTORATION.md` covers regeneration. Do not restart completed campaigns or overwrite their evidence.
