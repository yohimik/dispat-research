# Requirements for the author's next edit

Prepared 9 September 2026. The English working draft is ready for your edit, not submitted. Start with `main.tex` in this directory; `SOURCE.md` explains the files and build. The current PDF has ten content pages and two references-only pages.

20 September steering: focus the adaptation on fleet releases and polyrepos from the current `../dispat/specs/ccme-spec/SPEC.md`. Describe source-owned records, specified/discovered histories, consumer boundaries, settlement, and partial-fleet recovery. Keep the existing single-history proof and measurement boundaries explicit. Use campaign labels in manuscript prose while retaining exact versions in provenance. `ADAPTATION-2026-09-20.md` records the inspected working-tree snapshot and replaces earlier restrictions on discussing newer specification features; it does not authorize new empirical claims.

## Keep the scientific story clear

1. Keep the order **system and benefits → formal model and guarantees → experiments**. Introduce the npm assets → npm UI → Docker base → Docker app running example before notation, explaining how it extends the original npm → Docker → Docker failure. State the dependency boundary precisely: an npm workspace dependent consumes its provider's local build output, while a Docker dependent built in an isolated registry-based builder requires its provider image to be published. Do not generalize that requirement to Docker builders that share a local image store. A Go consumer resolving a module version obtains published source rather than upstream compiled output; local `go.work` and `replace` configurations are exceptions, and the Go example is not evaluated evidence.
2. Make consumer-based admission and discharge the central result: a consumer retains its release obligation after its provider succeeds. Explain why a valid build DAG alone does not give this recovery property.
3. Describe a **common release protocol for conforming integrations**. Single-package repositories, monorepos, control-repository polyrepos, and specifications fit the abstraction. Do not claim demonstrated compatibility with every language, version scheme, registry, or workflow.
4. Keep saga-inspired recovery as an important foundation, while crediting Sagas, deployment models, and prior lifecycle orchestration. Do not claim invention of sagas, Git storage, topological ordering, or the first use of sagas in operations. State precisely what this protocol adds.
5. Explain generic CI as a practical benefit: within an already provisioned environment, adding a package need not change the workflow. Package configuration still changes; new tools, permissions, credentials, or runners may require CI changes. The present paper does not measure onboarding effort.
6. Preserve the release-note communication benefit. Release-worthy descriptions marked during development can be collected into version-specific notes at release, even for private projects without conventional changelogs; a human may adapt them as social announcement drafts or hand them to managers for reports. Do not claim automatic social posting or a measured productivity effect. Keep these human-facing narratives distinct from completion tags, which discharge versioned release obligations.

7. Treat **shared Windows/Linux release logic** as a practical contribution. Use game development as a concrete example: Windows editing with Linux dedicated-server CI, or Linux development with Windows packaging CI. Shared configuration owns the graph, lifecycle, and portable commands; referenced platform files choose the shell and override platform-specific steps. This supports reuse of configuration and commands, not automatic translation of Bash to PowerShell, cross-compilation, or identical artifacts.
8. Preserve platform evidence boundaries. In the evaluated 1.10.0 release, the conditional wrapper still requires `/bin/sh`; selecting PowerShell in a child configuration does not remove that requirement. Do not equate setting `OS=Windows_NT` on Linux with a Windows execution. Before claiming validated cross-platform equivalence, run the same fixture on real Windows and Linux, record native toolchains and outputs, and compare planned versions, selected stages, recovery, and test gates. This validation has not been added to the current campaign.

Treat self-hosting as a practical case study, not causal evidence that AI improved productivity. Keep the first stable release milestone separate from the later source-size snapshot, and label AI assistance and reuse as the author’s account unless independently verified.

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

The completed primary campaign is `run-v1.10.0-linux-arm64-20260909`, pinned to the official 1.10.0 Linux ARM64 image and binary hash. See `evidence/EXPERIMENTS-1.10.0-20260909.md` for exact files and counts.

- Core differential holdout: 300 accepted, matching histories (seeds 90001–90300), no refusals, invalid executions, or differences.
- Recovery: 20 episodes, all converged, maximum four runs, 251 raw command records. The observed maximum is not a universal liveness bound.
- Three-node topology: five configurations × six repetitions, 30 initial executions. Twelve initial successes, eighteen deliberate failures, twelve successful repairs, and twenty-four unchanged no-op releases. The verifier applies 522 repeated predicates.
- Four-node topology: separately, the same 30/12/18/12/24 counts, with 798 repeated predicates. Both npm packages and both Docker artifacts were inspected. Base builds completed before UI publication began in all six mixed fixtures; do not describe this as required overlap.
- CI integration: three repetitions and 81 repeated predicates. Failed tests and missing required tests block release. These are controlled fixture observations, not measured industrial onboarding effort.
- Do not pool those units, the two topologies, or prior attempts into one success percentage. Predicate counts are not independent experimental samples.
- Preserve the initial 1.9.0 failed attempt and its corrected complete rerun. Its four-node verifier incorrectly demanded strict interval overlap. The corrected protocol was frozen before the new execution and reused unchanged for 1.10.0. Do not pool attempts or versions.
- The 1.10.0 recovery distribution is nine episodes in two runs, five in three, six in four. Its extra release/tag/status triplet explains 251 records versus 248 in 1.9.0; traces do not establish a cause attributable to diagnostics.
- Sixteen separately frozen diagnostics engineering cases passed; these are outside the 14-stage campaign and scientific sample counts. Diagnostics checks literal syntax and parser policy, not scope existence, authorization, or plan correctness.
- Saved 1.8.2 evidence remains separate: 1,500 core matches; full profile 997 accepted, 503 E195 refusals, 550 matching comparisons (546 accepted and four diagnostic dossiers), 1,914 differing package rows; 24 recovery episodes; six vectors; eight scale cells. These figures were not freshly executed on 1.10.0 and must never be relabeled as such.
- Historical competitor/replay observations remain pinned and separate. Do not generalize them to every tool configuration or claim competing tools cannot express a correct dependency graph.
- Artificial delays expose stage availability. They are not production throughput measurements; Docker Desktop results on Linux ARM64 are not native Windows evidence.
- Raw work trees, including nested Git metadata, are preserved in hash-verified archives. Never discard failed observations or alter raw outcomes to fit a claim.

## References and presentation

Use primary sources for technical claims. The current bibliography has 45 distinct, cited entries in first-citation order; 22 DOI metadata records were checked. Retain relevant antecedents rather than padding references with famous but unrelated papers. When changing a citation, verify authors, title, year, venue, DOI or official URL, and that the source actually supports the sentence.

Prefer concrete explanations over product promotion. Keep one running example through the system, model trace, and experiment. Retain useful limitations in one clear place rather than deleting them or repeating a disclaimer after every sentence. Do not add CCME version-history material unless needed to identify evaluated semantics: the fresh campaign uses dispat 1.10.0 and the implemented CCME 2.0 fragment, not unimplemented 3.x features.

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
5. Keep this research repository focused on the canonical English conference paper. Russian translation and patent synchronization are outside the current scope.

## Outreach evidence added 20 September 2026

Retain the 211-repository lower bound as a deduplicated coverage count across eight selected inventories, with unequal depth. Keep 1,512 discovery repositories separate. Preserve the distinction between observed Astro histories and simulated RelayCast/Arrow fixtures, the later quality-review exclusions, and stars as a visibility measure rather than code size. Exact provenance lives in `evidence/OUTREACH-20260920.json`; do not turn this selected review into a defect rate or field validation of the protocol.
