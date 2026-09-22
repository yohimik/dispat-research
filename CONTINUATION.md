# Research continuation, 22 September 2026 — distributed-execution evidence collected

This task owns only `/Users/yohimik/Projects/dispat-research`. Product changes, runtime defects and the pending `1.11.0-rc.4` release dispatch belong to the Dispat product agent; the product repository (`main` = `252216ba`, CCME `3.1.0-rc.2`) is inspected read-only and cited by commit.

## State on 22 September

The conference abstract in `paper/saner/main.tex` is **read-only** at the author's instruction; the delivered PDF is `output/pdf/saner-2027-paper.pdf` (SHA-256 `e47a6585…`, 10+2 pages, 48 references, verified in `output/saner-2027/abstract-final-review-20260922/`). It says Linux and LLVM results will be presented in the technical report, not in the paper. The mandatory abstract registration and any submission remain the author's decision; nothing was submitted.

The product side implemented CCME §28 (worker nodes over a Git mailbox) and measured it twice on Compute Engine on 22 September: Linux kernel parity pairs (hexagon 122.62 s alone versus 92.22/95.89 s with one slower worker; m68k_nommu 138.01 s versus 115.48/115.61 s) and an LLVM matrix pair (41 min 12.02 s on one node versus 27 min 48.94 s with two workers and an orchestrator; a one-heavy-package negative case at 26:47 versus 20:16). One repetition per side, asymmetric hardware, and the specification's own stance, "no speedup of the profile or of the engine is claimed beyond what these pairs measured", travel with every number. Seven LLVM attempts and all four kernel round-1 candidates are preserved as failures, including the dispat CRLF transport defect fixed at `9f649f88`.

The permitted raw material was **copied** (never moved or edited) into `experiments/distributed-20260922/evidence/` with `MANIFEST.json` (631 files, 49 MB, every SHA-256, the LLVM attempt-to-log mapping, binary hashes, and the list of what was left in place). Sources: the worker-nodes session's scratchpad and `/tmp/dispat-cov-*`, the validation session's scratchpad, `git archive` of the two forks (`linux-build-test` `c699bf3d`, `llvm-project` `952c2de4`), and the Codex agent's hash-verified round-1 archive. Secrets and private keys were neither read nor copied. See that directory's README for the caveats and exclusions.

## Technical report and reproduction kit, handed over and verified

The sibling session "Dispat-research report reproducibility" revised the full technical report under `paper/` for CCME `3.1.0-rc.2` at product commit `252216ba` (new `sections/04a-execution.tex` and `11-evaluation.tex`; model, guarantees, obligations and conformance sections updated for the delivery rule §13.4a, owed windows, E201, build readiness §19.2a and §28 placement; title and abstract rewritten by that session) and wrote the Docker + Terraform reproduction kit in `experiments/distributed-20260922/` beside `evidence/`. It handed both over with "report sections done". This task then rebuilt the report, ran `make check` (no undefined references, zero overfull boxes, 99 pages), traced the evaluation section's kernel and LLVM figures to the evidence files (`evidence/CROSS-CHECK.json`, 41 comparable values agreeing), fixed the two overfull bibliography URLs, corrected the LLVM caveat paragraph (the specification entry's 23 September date is an error, not a calendar effect; the `6c1a5fcd`/`d8fb8408` pair is the orchestrator's re-applied patch), cited the copied first-run logs, moved the section-local macros into `macros.tex`, and stopped the two tall LLVM tables from floating past the bibliography. The delivered PDF is `output/pdf/technical-report.pdf`; hashes and inspected pages are in `paper/REPORT-BUILD-2026-09-22.json`. These are structural and visual checks, not a review of the proofs or of the transcription of the specification.

The sibling session's audit agent then delivered `experiments/REPRODUCIBILITY.md` (ten campaign families with exact/recipe/historical status, rerun commands and verification), five relocatable helpers under `experiments/tools/`, and `experiments/results/repro-20260922/` (689 files, cheap reruns and verifier reports; nothing pre-existing modified; Git metadata from fresh reruns tarred). Every executed check passed and matched the retained evidence. Six gaps remain the author's decisions: the locked runner images exist only in this host's Docker store (a `docker save` with recorded hashes would make them portable); `docker/apk.lock` no longer resolves on a cold build (xz-libs 5.8.3-r0 replaced by 5.8.4-r0); the August binaries have no recorded hashes; some bases and packages are unpinned; the v181/v182 campaign scripts are bound to this host; several verifiers write beside their inputs. Docker images created by the audit remain on the host (`dispat-exp:repro-20260922-*`, `dispat-saner:rebuild-20260922`). The rerun of the three specification validation scripts is recorded in `evidence/spec-validation/RUN-20260922.md`: two reproduce their author's figures, the copied `proceed.py` does not, and the report cites none of them.

## Rules that continue to apply

Preserve raw observations and failed attempts; corrections need a new run with provenance. Do not pool the kernel rounds, the LLVM fixtures, or measurements from different binaries. Do not present either pair as a general speedup. Russian translation, patents and lawyer material remain out of scope. Nothing is submitted, published or released without explicit authorization.

---

# Research continuation, 10 September 2026 — SANER adaptation complete

This task owns only `/Users/yohimik/Projects/dispat-research`. The product task `01a06e7b-e8ba-7722-ad9c-c6da024126a8` owns `/Users/yohimik/Projects/dispat`; inspect it read-only when needed and route product defects or changes to that task. The research task is `01a08719-8f24-7201-a5fb-417d1ac98823`.

## Completed work

The user requested recent SANER literature, award examples, conference-suitable experiments, a whole-paper revision preserving the science, ten content pages plus two reference pages, and a review report. The topic is Software Release Engineering, Continuous Integration and Delivery. The user required Docker and Sol for execution; both Sol execution subtasks have finished. No experiment is pending.

Canonical paper: `paper/saner/`. Delivered PDF: `output/pdf/saner-2027-paper.pdf`, SHA-256 `e1101c91a00e732e982639e2f4834244c05c42c8c43188adb577fa6bc74349ff`. Exactly 10+2 pages, 44 references, normal IEEE 10pt body and 24pt title. All twelve pages were visually inspected. Evidence: `paper/saner/evidence/BUILD-20260910-NOTES.json` and `PDF-20260910-NOTES.json`. The model and guarantee sections remain byte-identical to their pre-revision sources.

Current review: `output/saner-2027/conference-review-20260910/REVIEW.md`. It prioritizes SANER 2026 CI contexts, GitHub Actions workflow clones, and CI/CD failure management; award examples inform exposition rather than substitute for technical related work. Primary-source access limits and source hashes are retained in `RESEARCH-PROVENANCE.json`; final integrity checks are in `FINAL-VERIFICATION.json`.

## Follow-up author clarification

The author added the practical benefit of release-worthy changes captured during development, collected into notes at release, then adapted as social announcement drafts or handed to managers for reports. The paper distinguishes these narratives from recovery completion tags. The npm example now explicitly identifies a provider-consumer dependency. Isolated registry-based Docker builders need the published base image; version-resolved Go modules need published tagged source, while local `go.work`/`replace` configurations remain exceptions. These are presentation/applicability clarifications, not new measured outcomes. See `output/saner-2027/conference-review-20260910/AUTHOR-CLARIFICATIONS.md` and its source-provenance JSON. No experiment rerun was needed; no campaign evidence changed.

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
