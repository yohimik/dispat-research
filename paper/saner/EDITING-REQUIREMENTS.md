# Requirements for the author's next edit

Prepared 9 September 2026. The English working draft is ready for your edit, not submitted. Start with `main.tex` in this directory; `SOURCE.md` explains the files and build. The current PDF has ten content pages and two references-only pages.

## Keep the scientific story clear

1. Keep the order **system and benefits → formal model and guarantees → experiments**. Introduce the original npm → Docker → Docker failure before notation. Explain the distinction between local build output and an artifact that must already be published.
2. Make consumer-based admission and discharge the central result: a consumer retains its release obligation after its provider succeeds. Explain why a valid build DAG alone does not give this recovery property.
3. Describe a **common release protocol for conforming integrations**. Single-package repositories, monorepos, control-repository polyrepos, and specifications fit the abstraction. Do not claim demonstrated compatibility with every language, version scheme, registry, or workflow.
4. Keep saga-inspired recovery as an important foundation, while crediting Sagas, deployment models, and prior lifecycle orchestration. Do not claim invention of sagas, Git storage, topological ordering, or the first use of sagas in operations. State precisely what this protocol adds.
5. Explain generic CI as a practical benefit: within an already provisioned environment, adding a package need not change the workflow. Package configuration still changes; new tools, permissions, credentials, or runners may require CI changes. The present paper does not measure onboarding effort.

6. Treat **shared Windows/Linux release logic** as a practical contribution. Use game development as a concrete example: Windows editing with Linux dedicated-server CI, or Linux development with Windows packaging CI. Shared configuration owns the graph, lifecycle, and portable commands; referenced platform files choose the shell and override platform-specific steps. This supports reuse of configuration and commands, not automatic translation of Bash to PowerShell, cross-compilation, or identical artifacts.
7. Preserve platform evidence boundaries. In the evaluated 1.8.2 release, the conditional wrapper still requires `/bin/sh`; selecting PowerShell in a child configuration does not remove that requirement. Do not equate setting `OS=Windows_NT` on Linux with a Windows execution. Before claiming validated cross-platform equivalence, run the same fixture on real Windows and Linux, record native toolchains and outputs, and compare planned versions, selected stages, recovery, and test gates. This validation has not been added to the current campaign.

## Preserve the mathematics and its boundaries

- Define every symbol before use and keep dependency-arrow direction explicit. The figure uses provider-to-consumer stage arrows; the formal package graph uses consumer-to-provider edges.
- Preserve the difference between the train window and the fresh-work window. A prerelease tag discharges delivered intent while retaining the train target.
- Keep normalization and deterministic history ordering explicit. Git ancestry alone does not totally order commits. Keep source-set identity, shortest propagation depth, cancellation, scope filters, channels, and version guards in the admission argument.
- Keep the channel-entry patch case and exact-pin refusal behavior. Do not simplify the equations in a way that changes prerelease targets.
- Review every theorem and counterexample personally, especially source stability, inherited-channel drift, no widening, and version stability. Several stability lemmas follow directly from the retry invariant; the paper acknowledges this rather than presenting the invariant as automatically enforced by the implementation.
- The eight guarantees concern the stated model. They are not eight mechanically verified implementation properties. The implementation's own-reason exceptions, hooks, recording, and finalization require a separate refinement argument.
- Preserve `release(s) = release(release(s))` for a fully successful recorded release under fixed inputs and the retry invariant. Keep the adjacent explanation of successful-but-unrecorded publication and safe repetition or reconciliation. Ledger discharge does not make arbitrary external effects exactly-once.
- Convergence counts attempts that make progress. Permanent failures and an unlimited number of no-progress retries have no finite completion bound.
- “No cache/database” means no additional persistent **release-state** store. Git is the ledger; registries, build caches, application databases, and Terraform state still exist where integrations require them.

## Keep evidence tied to what was actually measured

- Core differential profile: 1,500 matching, accepted instances in the shared reference-model domain.
- Broader profile: 997 accepted plans; 503 E195 refusals; 550 matching comparisons comprise 546 accepted matches and four matching diagnostic dossiers. Preserve the 1,914 differing package rows and the explanation of oracle limits.
- Saved campaign: 24 recovery episodes, at most four runs; six targeted vectors; eight planning-scale cells. These records were reaggregated and hash-checked for this revision, not rerun in full today.
- Fresh mixed-chain campaign: five configurations × two repetitions, 106 verifier assertions, four repaired failures, eight unchanged reruns without repeated build or publication. Assertions are not independent experimental samples.
- Keep the injected three-second and two-second delays identified as controls. Two repetitions establish observed ordering, not a statistical performance advantage. Missing-barrier failures are deliberate; setup failures and invalid Python 3.9 cross-process timing are excluded.
- Do not pool histories, package rows, vectors, runs, and assertions into a single success percentage. Preserve host/tool versions, binary hashes, raw outcomes, and limitations.
- Historical competitor configurations were not all rerun with this revision. Never generalize their observed behavior to every configuration or claim competitors cannot encode the correct graph.
- If you want to promote specification portability or unchanged-CI onboarding into empirical contributions, first add controlled executable fixtures. Measure the unchanged workflow, changed package configuration, required test selection, failed-test publication gate, and resulting release. Otherwise retain the present bounded architectural claims.

## References and presentation

Use primary sources for technical claims. The current bibliography has 40 distinct, cited entries in first-citation order; 19 DOI metadata records were checked. Retain relevant antecedents rather than padding references with famous but unrelated papers. When changing a citation, verify authors, title, year, venue, DOI or official URL, and that the source actually supports the sentence.

Prefer concrete explanations over product promotion. Keep one running example through the system, model trace, and experiment. Retain useful limitations in one clear place rather than deleting them or repeating a disclaimer after every sentence. Do not add CCME version-history material unless needed to identify evaluated semantics: this campaign uses Dispat 1.8.2 and the implemented CCME 2.0 fragment, not unimplemented 3.x features.

## Format and submission checks

The [SANER 2027 Research Track call](https://conf.researchr.org/track/saner-2027/saner-2027-papers) requires IEEE conference format, 10-point body text, a 24-point title, and at most ten content pages plus two references-only pages. Your target is exactly 10+2. Do not shrink fonts or margins to fit; edit content and rebuild.

Preserve double anonymity, including metadata, identifying project names, links, and supplemental files. Keep Data Availability after Conclusion and accurately disclose substantive AI assistance. The abstract is due 21 September and the paper 25 September 2026, AoE; recheck the call before submission.

**Unresolved before submission:** establish the dates of any public versions, updates, or promotion of the same scientific content. The anonymity period began 25 August and continues through the decision or withdrawal. If prior sharing conflicts with the policy, consult the chairs. Artifact sharing is encouraged, not mandatory; the local bundle is not yet an anonymous upload package. Nothing is to be submitted now.

### AI provenance to confirm

The author reports that most AI assistance came from Claude Fable 5, with additional use of Claude Opus 5, Claude Fable 5.1, Gemini, and OpenAI Codex. The paper now reflects that account rather than attributing the work mainly to Codex. The Claude labels are preserved as supplied by the author; confirm exact product/model identifiers from session records before submission, and identify the Gemini model if available. The list does not imply that every tool performed every listed activity. Keep the stated scope of assistance accurate and retain human responsibility for the results.

## Final handoff checks after your edit

1. Read the whole argument without consulting the specification. A reviewer must be able to understand the model and proof premises from this paper.
2. Compile and run `python3 check.py`. Render and inspect every page again: changed text can move tables, references, or equations.
3. Recheck numerical claims against retained evidence; rerun affected experiments if semantics or the tested binary changes.
4. Have a human reviewer challenge the proofs, novelty boundary, and interpretation. Automated checks are not independent scientific replication.
5. Finish the English revision before translating it. Synchronize the Russian paper from English, then synchronize the patent with the Russian paper separately. Those later updates are outside this handoff.
