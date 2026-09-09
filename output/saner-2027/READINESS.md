# SANER 2027 paper verification and author handoff

Verified 9 September 2026. **Ready for the author's English edit. Not submitted, and not a certification of submission eligibility or acceptance.**

## Delivered manuscript

Active source: `../../paper/saner/main.tex`. Editing requirements: `../../paper/saner/EDITING-REQUIREMENTS.md`. Delivered PDF: `../pdf/saner-2027-paper.pdf`.

The paper follows system → mathematics → experiments. It extends the original npm → Docker → Docker problem with two npm packages followed by two Docker images, consumer-based retention of release obligations, and a common integration contract. Single-package, monorepo, control-repository polyrepo, and specification use are explained. Generic graph-driven CI is described as a bounded architectural benefit, not an unmeasured productivity result.

The model and proof review corrected or clarified deterministic history ordering, source suppression, channel eligibility, the train aggregate, channel-entry patch behavior, version-guard outcomes, and the distinction between recorded completion and external effects. The retry invariant is explicit; several stability lemmas are consequences of its premises. Proofs are handwritten and tool-assisted, not mechanized or an implementation-refinement proof. G8 now explicitly concerns bump-axis suppression alone, not cancellation of an entire contribution.

## Format and visual checks

- Exactly 12 PDF pages: ten content pages, references beginning on page 11 and continuing on page 12.
- Standard IEEE conference class, US Letter, 24-point title and 10-point body. PDF text sizes are approximately 23.91 and 9.96 PDF points, the TeX-point conversion.
- All fonts embedded; no font-substitution warnings. Selecting T1 encoding before IEEEtran initialization resolved the previous XeTeX startup warnings.
- All twelve pages rendered and inspected. Fixed the stage-graph labels that touched node boundaries. No remaining visible text overlap or clipped table/equation was found.
- No overfull boxes, missing glyphs, undefined references, duplicate labels, or duplicate bibliography keys. Some underfull line warnings remain in justified technical text and long bibliography URLs; rendered output was inspected.
- Forty cited references, ordered by first citation, with no uncited bibliography entries. Nineteen DOI metadata records checked against Crossref; other technical references use primary publications, official documentation, or identified project reports. Aeolus's missing author was restored. NEPHELE is identified as a project deliverable, not presented as peer-reviewed novelty evidence.
- No author metadata or known identifying project/author strings in extracted PDF text. This string check does not guarantee that no reader can infer identity.

Machine results and source/PDF hashes: `validation/manuscript.json`. DOI metadata: `research/doi-metadata.json`. Research positioning: `research-report.md` and `contribution-assessment.md`.

## Evidence checks

The completed primary campaign uses the official Dispat 1.9.0 Linux ARM64 binary and an immutable Docker runner. All fourteen provenance stages passed. Its source, binary, image, protocol, and archive identities are retained in [the evidence report](../../paper/saner/evidence/EXPERIMENTS-1.9.0-20260909.md).

| Evidence | Verified result |
| --- | --- |
| Core holdout | 300 accepted matching histories; no differences, refusals, or invalid executions |
| Recovery | 20 converged episodes; at most four runs; 248 raw command records |
| Three-node mixed topology | 30 executions; 12 initial successes, 18 deliberate failures, 12 repairs, 24 final no-ops |
| Four-node mixed topology | Separately the same counts; both npm packages and both OCI artifacts inspected |
| CI fixture | Three repetitions; 81 predicates, including failed-test and missing-test release gates |

The three-node verifier applies 522 repeated predicates and the four-node verifier 798. They are not independent experimental samples. Local builds did not wait for unnecessary publication; Docker consumers with registry requirements did wait. The six four-node mixed cases built the base before UI publication began, a valid schedule that need not have positive interval overlap.

The first 1.9.0 attempt remains FAILED because its four-node oracle incorrectly required that overlap. The predicate correction was frozen before a new complete execution using the same cases and seeds. Both attempts are archived; their observations are not pooled. The coordinator extracted the corrected archive separately and reran the four data verifiers with networking disabled. All passed; 9,190 archived files also matched the retained work tree byte-for-byte.

Saved 1.8.2 evidence remains separately labeled: the earlier 1,500-case core and full profiles, six specification vectors, twenty-four recovery episodes, fault cells, historical comparisons, and eight planning-scale cells. Those observations were reaggregated and hash-checked, not newly executed on 1.9.0. The old macOS mixed-chain experiment remains historical evidence, not the primary current result.

Dispat 1.9.0's own CI/release passed all gates, including installation on macOS, Linux, and Windows. The self-hosting case study supports practical use; code size and release milestones do not establish causal AI productivity or replace protocol experiments.

## Remaining author decisions

1. Review and own the mathematical premises, proofs, and counterexamples. The strongest claim is the conditional admission/discharge protocol, not first-ever saga orchestration or universality across all ecosystems.
2. Keep specification integration and unchanged-workflow CI bounded by the three controlled fixture repetitions. They do not establish industrial generality or reduced human effort.
3. Prepare an anonymous, executable artifact if supplying one. The current local curated review copy omits some binaries, histories, and large dossiers; supplemental raw files contain identifying paths. No anonymous artifact has been published or attached.
4. Resolve public-sharing history against the [SANER call and preprint policy](https://conf.researchr.org/track/saner-2027/saner-2027-papers), as detailed in the editing requirements. Eligibility cannot be inferred from the absence of another active submission.
5. After author edits, rebuild, rerun checks, and inspect the PDF again. Synchronize Russian/patent documents only after the English revision settles, in the requested order.

No submission, commit, push, release, public artifact upload, or patent edit was performed for this handoff. Unrelated workspace changes were preserved.

## Windows/Linux clarification added for author editing

The system section now gives explicit Windows-to-Linux and Linux-to-Windows CI examples for game development. Shared graph/lifecycle/portable commands are distinguished from platform-specific shell scripts and toolchains. The 1.8.2 POSIX-shell requirement remains stated, and no native two-OS equivalence test is claimed. The editing checklist specifies that experiment if the author wishes to strengthen the portability claim. The rebuilt manuscript still passes 10+2 pagination and citation checks; changed pages 3–10 were rendered and inspected again.

## Final page-fit and disclosure correction

Shortened the abstract and removed repeated introductory explanation to make room for the Windows/Linux example without changing fonts, margins, proof premises, or results. The research report now reflects completed work and an updated ten-page writing budget instead of the superseded proposal. The AI disclosure follows the author's corrected account: primarily Claude Fable 5, with additional Claude Opus 5, Claude Fable 5.1, Gemini, and Codex. Exact model identifiers remain an author provenance check.
