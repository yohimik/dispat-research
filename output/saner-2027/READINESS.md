# SANER 2027 paper verification and author handoff

Verified 9 September 2026. **Ready for the author's English edit. Not submitted, and not a certification of submission eligibility or acceptance.**

## Delivered manuscript

Active source: `../../paper/saner/main.tex`. Editing requirements: `../../paper/saner/EDITING-REQUIREMENTS.md`. Delivered PDF: `../pdf/saner-2027-paper.pdf`.

The paper follows system → mathematics → experiments. It foregrounds the original npm → Docker → Docker problem, consumer-based retention of release obligations, and a common integration contract. Single-package, monorepo, control-repository polyrepo, and specification use are explained. Generic graph-driven CI is described as a bounded architectural benefit, not an unmeasured productivity result.

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

The existing curated campaign verifier passed again, validating 1,108 file hashes and reaggregating selected reported results:

| Evidence | Verified result |
| --- | --- |
| Core differential profile | 1,500 matching and accepted instances |
| Broader profile | 997 accepted, 503 refused; 550 matching comparisons; 1,914 differing package rows |
| Specification vectors | Six |
| Recovery episodes | 24; maximum four runs |
| Planning-scale cells | Eight |
| Released-binary fault scenarios | Three |

This is verification of saved observations, not a fresh rerun of the whole campaign. The broader-profile refusals and oracle disagreements remain visible in the paper. Historical competitor configurations are not recast as freshly rerun experiments. Detailed verifier output: `validation/saved-campaign.txt`.

The **fresh** mixed-chain experiment used official Dispat 1.8.2 on macOS ARM64, Python 3.12.14, native npm build/publication, private registries, and isolated BuildKit builds:

- Five configurations repeated twice; all 106 verifier assertions pass.
- Local-output base builds overlap npm publication in both mixed runs.
- Application builds follow base publication with the barrier enabled; removing it causes the intended registry-not-found failure twice.
- Four repaired failures finish at the retained planned versions.
- Eight completed configurations subsequently perform no build or publication on an unchanged rerun.
- Its containers, builder, and network were removed. No external package/image service received a publication; local downloaded image cache can remain.

The retained run is `mixed-chain/run-20260909-022316/`; source, logs, timestamps, tags, results, checksums, and exclusions are documented in `mixed-chain/README.md`. Earlier registry-connectivity and Python 3.9 clock-origin attempts are excluded. The fixed delays establish observable ordering, not comparative throughput. The experiment does not cover the ambiguous external-success/record-loss interval.

## Remaining author decisions

1. Review and own the mathematical premises, proofs, and counterexamples. The strongest claim is the conditional admission/discharge protocol, not first-ever saga orchestration or universality across all ecosystems.
2. Keep specification integration and unchanged-workflow CI bounded as architectural claims, or add controlled fixtures before asserting measured generality or reduced effort.
3. Prepare an anonymous, executable artifact if supplying one. The current local curated review copy omits some binaries, histories, and large dossiers; supplemental raw files contain identifying paths. No anonymous artifact has been published or attached.
4. Resolve public-sharing history against the [SANER call and preprint policy](https://conf.researchr.org/track/saner-2027/saner-2027-papers), as detailed in the editing requirements. Eligibility cannot be inferred from the absence of another active submission.
5. After author edits, rebuild, rerun checks, and inspect the PDF again. Synchronize Russian/patent documents only after the English revision settles, in the requested order.

No submission, commit, push, release, public artifact upload, or patent edit was performed for this handoff. Unrelated workspace changes were preserved.

## Windows/Linux clarification added for author editing

The system section now gives explicit Windows-to-Linux and Linux-to-Windows CI examples for game development. Shared graph/lifecycle/portable commands are distinguished from platform-specific shell scripts and toolchains. The 1.8.2 POSIX-shell requirement remains stated, and no native two-OS equivalence test is claimed. The editing checklist specifies that experiment if the author wishes to strengthen the portability claim. The rebuilt manuscript still passes 10+2 pagination and citation checks; changed pages 3–10 were rendered and inspected again.

## Final page-fit and disclosure correction

Shortened the abstract and removed repeated introductory explanation to make room for the Windows/Linux example without changing fonts, margins, proof premises, or results. The research report now reflects completed work and an updated ten-page writing budget instead of the superseded proposal. The AI disclosure follows the author's corrected account: primarily Claude Fable 5, with additional Claude Opus 5, Claude Fable 5.1, Gemini, and Codex. Exact model identifiers remain an author provenance check.
