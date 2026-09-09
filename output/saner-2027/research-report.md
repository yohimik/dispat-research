# Preparing the release-protocol paper for SANER 2027

## Current 1.10.0 evidence update, 9 September 2026

The canonical English manuscript now uses a completed, separate dispat 1.10.0 Linux ARM64 campaign. All 14 stages passed: 300 accepted matching core histories; 20 converged recovery episodes (at most four runs, 251 command records); 30 initial executions per three- and four-node topology; and three CI repetitions. Each topology retained 18 intended negative outcomes, 12 successful repairs and 24 unchanged no-op runs. Checks remain separate from sample counts. A separate 16-case diagnostics engineering addendum passed.

The campaign survived the app restart without a replacement run. The complete retained work archive contains 9,157 byte-verified regular files; its SHA-256 is `835208a0cd9066ec6bf7ec424a4d9cdee06ca4482a061f7a7d7cc02738611793`. All four retained-data verifiers passed offline from a fresh extraction. This is an integrity/reproduction check, not independent scientific replication.

The recovery difference from 1.9.0 comes from one extra release attempt in the n=100, p=.3, seed=100 trace, adding release/tag/status records. Initial versions and the first failure set match, but pending sets and subsequent failure draws differ. No causal effect of diagnostics is established. Both topologies again showed the intended local-output scheduling; the four-node base builds completed before UI publication began, an admissible schedule rather than a requirement for strict overlap.

See [1.10.0 evidence](../../paper/saner/evidence/EXPERIMENTS-1.10.0-20260909.md) and [editing requirements](../../paper/saner/EDITING-REQUIREMENTS.md). The paper retains ten content pages plus two reference pages and keeps the model/implementation gap explicit. Old 1.8.2 full-profile diagnostics, scale cells and comparisons remain historical. Prior 1.9.0 evidence and its failed oracle attempt are preserved. Native Windows equivalence and production throughput were not measured. Author review, public/preprint-history assessment and exact AI-model-name confirmation remain required before any submission.

## Historical 1.9.0 evidence update, 9 September 2026

The active manuscript now incorporates the completed Dispat 1.9.0 Linux ARM64 campaign: 300 matching core histories, 20 converged recovery episodes, separate 30-execution three- and four-node topologies, and three CI-fixture repetitions. The four-node case uses two npm packages followed by two Docker images. A retained first attempt failed an overly strict overlap oracle; the correction was frozen before the new full execution. Do not pool attempts or relabel the saved 1.8.2 full-profile, scaling, and competitor records as current measurements.

See [the experiment evidence](../../paper/saner/evidence/EXPERIMENTS-1.9.0-20260909.md) and [editing requirements](../../paper/saner/EDITING-REQUIREMENTS.md) for exact identities, counts, limitations, and reproduction. Self-hosting and dated implementation milestones strengthen the practical case study; they are not a controlled estimate of AI productivity. The research positioning below remains relevant, but earlier campaign descriptions are historical where they differ from this update.


Research and manuscript recommendations · 9 September 2026

**Status: preparation only. No SANER submission has been made.** The earlier ICSA submission was withdrawn. The English manuscript has now been revised, built, and checked at ten content pages plus two reference pages. The mixed-chain experiment has also been executed. This report retains the research rationale and updates its recommendations to the actual handoff; see READINESS.md for evidence and unresolved author decisions.

## Recommendation

Lead with the problem that originally motivated the system: **an npm package feeds a Docker image, which feeds another Docker image**. A package-level dependency graph alone does not explain when each build may start. Some consumers need a provider's local build output; others need its published artifact. Publication must therefore sometimes happen between builds. A later failure then raises a second question: how can the next invocation complete the remaining release without losing the downstream work or inventing another version?

That sequence gives the paper a natural argument:

1. Explain the system through this concrete chain, its stage ordering, and its operational benefits.
2. Formalize release admission and recorded progress, state the assumptions, and prove the guarantees.
3. Evaluate the implementation against those claims, separating scheduling, recovery, semantic agreement, and cost.

The mathematical contribution should remain central. The system explanation gives readers a reason to care about the definitions; it does not replace them with a feature catalogue.

Use **exactly ten pages of content, followed by two pages containing references only** as the authoring target. The conference permits a maximum, not a required length. The current build meets that page count. The budget below guides further edits; avoid filling page 10 so tightly that a small clarification crowds the conclusion or disclosures.

## Venue fit and constraints

SANER explicitly includes release engineering, continuous integration and delivery. It accepts theoretical, empirical, and tool-oriented research. Its criteria cover novelty, significance, soundness, verifiability, and presentation. IEEE conference format is required: `IEEEtran`, `10pt,conference`, with no `compsoc` option; at most ten content pages plus two reference pages. Abstract registration is due **21 September 2026**, and the paper **25 September 2026**, both AoE. [Official research-track call](https://conf.researchr.org/track/saner-2027/saner-2027-papers).

Preparation must also cover double-anonymous text and artifacts, a Data Availability section after the conclusion, and disclosure of substantive AI assistance. Before submission, establish whether an identifiable version was posted or promoted during the anonymity period, which began 25 August. Public-preprint history remains unresolved; withdrawal from ICSA resolves simultaneous review, not that separate question. Nothing needs submitting to complete the present research and revision work. [Submission and preprint rules](https://conf.researchr.org/track/saner-2027/saner-2027-papers#preprint-guidelines).

## What “influential papers” means in this report

I selected seven full papers: two SANER Most Influential Paper award recipients, two SANER distinguished papers, a directly relevant SANER release-engineering paper, and two adjacent papers useful for formal system exposition. Award status is verified separately from the paper text. This is a focused editorial review, not an exhaustive systematic literature review or a ranking by citation counts. SANER 2027 has not yet selected its research papers; the exemplars come from earlier editions and adjacent venues.

The downloads include publisher or institutional cover sheets in two cases. Those cover sheets must not be confused with conference page allowances. Source PDFs and extracted text are retained in `research/` for checking the observations.

### 1. RevFinder: an established SANER influence

Thongtanunam and colleagues, **Who Should Review My Code? A File Location-Based Code-Reviewer Recommendation Approach for Modern Code Review**, SANER 2015. It received SANER 2025's Most Influential Paper award. [Award record](https://sel.ist.osaka-u.ac.jp/topics/award_SANER2025_raula/index.html.en).

**Observed organization:** introduction; background and related work; exploratory evidence about the problem; recommendation approach; empirical evaluation; results; discussion; conclusion. Within the approach, an intuitive worked example precedes the ranking algorithm and its calculations. It does not use a separate theorem section. [Author manuscript](https://naist.repo.nii.ac.jp/record/5130/files/10061_12737.pdf).

**Transfer to our paper:** show the chain and one wrong schedule before introducing admission predicates. Let a small execution explain why the algorithm is needed. Its preliminary empirical study is not evidence for the prevalence of our release problem; our original experience must be labeled motivation, not a population study.

### 2. Self-admitted technical debt: evidence can overturn intuition

Wehaibi, Shihab, and Guerrouj, **Examining the Impact of Self-admitted Technical Debt on Software Quality**, SANER 2016. It received SANER 2026's Most Influential Paper award. [Official award list](https://conf.researchr.org/attending/saner-2026/awards).

**Observed organization:** introduction; related work; methodology; case-study results; threats; conclusion. The contribution is empirical rather than a new system or theorem. Research questions distinguish defects from change difficulty, and the conclusions preserve results that do not fit the simplest expectation. [Author manuscript](https://das.encs.concordia.ca/pdf/Wehaibi_SANER2016.pdf).

**Transfer:** avoid turning every Dispat result into a success count. Preserve the weak historical replay agreement and the limited domain of the reference oracle. These limitations help define what the measurements actually establish.

### 3. Model consistency: the closest SANER exposition pattern

Marchezan and colleagues, **Exploring Dependencies Among Inconsistencies to Enhance the Consistency Maintenance of Models**, SANER 2024. Distinguished-paper status is recorded in an author's institutional publication history. [Award record](https://www.saadshafiq.com/uploads/resume.pdf).

**Observed organization:** introduction; background and motivation; approach; evaluation; discussion; related work; conclusion. A robotic-arm example introduces the problem before the metamodel and algorithms. The evaluation connects research questions to assumptions, methods, and metrics. [Paper](https://wesleyklewerton.github.io/publications/SANER24.pdf).

**Transfer:** reuse one release example across the system diagram, formal admission rule, and fault trace. Each experimental question should name the claim it tests. Do not import the UML mechanisms or numerical results; they address a different problem.

### 4. STELLAR: a recent awarded SANER paper

Sorokin and colleagues, **STELLAR: A Search-Based Testing Framework for Large Language Model Applications**, SANER 2026, received a distinguished-paper award. [Official award list](https://conf.researchr.org/attending/saner-2026/awards).

**Observed organization:** introduction; background and motivation; approach; evaluation; threats; qualitative evaluation; related work; conclusion; data availability. Definitions and examples precede the algorithm. Its evaluation separately asks whether its oracle is reliable, whether testing is effective, and whether discovered failures are diverse. [Author manuscript](https://tsigalko18.github.io/assets/pdf/2026-Sorokin-SANER.pdf).

**Transfer:** explicitly assess the reference oracle's coverage before using agreement as evidence. Separate fault diversity from the number of runs. Do not add an AI research claim merely because SANER welcomes AI topics or agents helped develop Dispat.

### 5. Release engineering: direct subject positioning

Adams and McIntosh, **Modern Release Engineering in a Nutshell: Why Researchers Should Care**, SANER 2016, is an invited release-engineering contribution. [Authors' publication record](https://rebels.cs.uwaterloo.ca/confpaper/2016/03/15/modern-release-engineering-in-a-nutshell.html).

**Observed organization:** introduction; a working definition of the release pipeline; research roadmap; a checklist for software-engineering researchers; conclusion. This is a synthesis and agenda, not a theorem-and-experiment system paper. [Paper](https://rebels.cs.uwaterloo.ca/papers/saner2016_adams.pdf).

**Transfer:** position our contribution at the interaction of building, publishing, and recovering versioned dependencies. Do not claim to solve the whole release pipeline. This paper belongs in the manuscript's related work, not just in this editorial report.

### 6. Anvil: distinguish a model proof from an implementation proof

Sun and colleagues, **Anvil: Verifying Liveness of Cluster Management Controllers**, OSDI 2024, received a Best Paper award. It is an adjacent systems exemplar, not a SANER paper. [Official publication and award](https://www.usenix.org/conference/osdi24/presentation/sun-xudong).

**Observed organization:** introduction; practical controller behavior; correctness specification; framework; theorem proof strategy; case studies; evaluation; related work; discussion. It exposes the environment and fault assumptions needed for liveness. [Paper](https://www.wisdom.weizmann.ac.il/~padon/anvil-osdi2024.pdf).

**Transfer:** explain the operational failure before the formal property, then identify exactly what is proved and what is trusted. Our handwritten model proofs and executable tests must not be described as equivalent to Anvil's verified implementations. Mechanizing the Dispat model remains future work.

### 7. Build Systems à la Carte: separate the decisions

Mokhov, Mitchell, and Peyton Jones, **Build Systems à la Carte**, ICFP 2018, provides an executable framework for comparing build systems. It is selected for conceptual relevance, not a verified citation ranking or SANER award. [Publication record](https://www.microsoft.com/en-us/research/publication/build-systems-la-carte/).

**Observed organization:** introduction; concrete background; abstract model; decomposed design; concrete implementations; engineering aspects; related work; conclusion. Scheduling and rebuilding are separated. It is not organized around a conventional benchmark section. [Final conference manuscript](https://www.microsoft.com/en-us/research/wp-content/uploads/2018/03/build-systems.pdf).

**Transfer:** distinguish which packages need a release, which stages may start, and which successful obligations have been recorded. A topological scheduler alone is not the scientific novelty. This paper already belongs in our bibliography; its role should be explained more precisely.

### Synthesis

The selected papers do **not** all follow “system, mathematics, experiments” literally. Some are empirical, and some place related work near the beginning. The common useful practice is to establish a concrete problem, explain the method with enough detail to inspect it, and match evidence to claims. Your requested order is well suited to this particular paper because its contribution combines an executable protocol with mathematical guarantees.

## The new opening: npm → Docker → Docker

Use an explicitly illustrative naming scheme:

- **assets**, an npm package whose build produces files in the workspace;
- **base**, a Docker image that copies those files into an image;
- **app**, a Docker image built from the newly published `base` version.

The first dependency uses a local build artifact. The second uses a registry artifact in an isolated downstream builder. These are declared consumption modes, not universal properties of npm or Docker: an npm consumer that downloads from its registry also needs publication, and a Docker builder sharing a locally available base image may not need a registry push.

```text
Package dependencies:   assets (npm) ──→ base (Docker) ──→ app (Docker)

Required stage order:
  build assets ──→ build base ──────────→ publish base ──→ build app ──→ publish app
       │                                    ↑
       └────────→ publish assets ────────────┘

Allowed overlap: publish assets and build base.
Required barrier: publish base must succeed before build app starts.
```

This example explains both why a global “build everything, then publish everything” pipeline is insufficient for the isolated-builder case and why serializing every package through both stages imposes an unnecessary wait at the npm edge. The paper should not claim that generic workflow engines cannot encode these dependencies. Its contribution is the composition with version selection and recoverable release records.

**Configuration accuracy:** `isBuildWaitingPublish: true` belongs to the **provider** package or its space. In this example, set it on `base`, not on `app` merely because `app` waits. Leave it false on `assets` when its consumer uses the local output. The executor also orders consumer publication after provider publication. These semantics were checked against the current executor, the versioned 1.8 Docker example, and the two integration tests that distinguish waiting from permitted overlap. Those files were inspected; no new test run is claimed here.

Relevant repository evidence:

- [Executor scheduling contract](/Users/yohimik/Projects/dispat/services/dispat/internal/release/executor.go:110)
- [Publish barrier and overlap tests](/Users/yohimik/Projects/dispat/tests/integration/order_test.go:98)
- [Versioned Docker example](/Users/yohimik/Projects/dispat/packages/docs/versioned_docs/version-1.8/examples/docker.md:1)

Then fail `app` after `assets` and `base` have published and been recorded. The retry must preserve `app`'s outstanding release at its planned version. This connects the original scheduling problem to consumer-based admission. Keep a separate, clearly marked branch of the example for a lost publish response before recording; that branch requires external-outcome reconciliation.

### Proposed replacement opening

> Consider a release containing an npm package, a Docker image that packages its output, and a second Docker image built from the first. Their dependencies cross the boundary between building and publishing. The first image can use files already built in the workspace. The second image, when built in an isolated environment, cannot use its new base version until that version is available in the registry. Building all packages before publishing any of them is therefore not a valid schedule for this release.
>
> The release also needs to survive interruption. If the npm package and base image have been published but the final image fails, repeating the command should finish the remaining work. It should neither forget the final image because its providers have already released nor assign it a different version solely because the first attempt made progress. Stage ordering and recovery are consequently parts of the same problem: publishing one package changes what another package can build and what a later run still owes.
>
> We present a release protocol that derives versioned work from repository history and executes it through a graph of build and publish stages. Commit messages describe release intent, while Git tags record completed release obligations. A consumer retains a propagated obligation until its own record discharges that obligation. This design permits local-build dependencies and published-artifact dependencies within one release graph, and supports recovery by recomputing the outstanding plan.
>
> Our mathematical model establishes deterministic planning and conditional recovery guarantees. The conditions are explicit: the reviewed intent and relevant admission inputs remain stable during a retry sequence, and successful external publication is either recorded or reconciled before repetition. The implementation is evaluated separately through reference-model comparisons, ordering checks, and injected failures. These experiments test the implementation; they do not constitute a proof that its code refines the entire model.

This is proposed manuscript text, not a historical account of measured deployments. Use one sentence later to state that the same protocol supports a single-package repository, a monorepo, or a polyrepo represented through a control repository.

## What to move into, out of, and within the manuscript

The **archived** withdrawn IEEE draft was nine pages total. Its model begins on page 2, implementation on page 6, evaluation on page 7, and references on page 9. It has 28 bibliography keys, with no missing, duplicated, or uncited keys. Those are archival counts. The active SANER revision has 40 cited references; DOI metadata and primary-source checks are recorded in the verification report.

| Existing material | Recommended treatment | Reason |
|---|---|---|
| npm → Docker → Docker origin | Add to introduction and use throughout | Makes the initial problem understandable before notation |
| Implementation after the proofs | Move its architectural explanation before the model | Readers need the inputs, stage boundaries, records, and retry behavior first |
| Eight-header CCME table and full syntax walkthrough | Move most to the technical report/artifact; retain one commit and its normalized intent | Surface syntax is not the central scientific result |
| CCME version chronology and unimplemented extensions | Exclude from conference narrative | A roadmap does not substantiate current guarantees |
| Consumer admission, two windows, retry invariant | Keep self-contained in the paper | They carry the nontrivial reasoning |
| Eight guarantees | Group by planning, recovery, and scope/channel behavior without deleting their qualifications | Reduce reading burden while keeping proof obligations visible |
| Universal tagging argument | Keep next to convergence | Explains why even packages with no upload need discharge records |
| Six counterexamples in evaluation | Move explanatory cases next to the definitions they motivate; retain a compact validation matrix in evaluation | Logical necessity and executed regression coverage are different evidence |
| Release-tool comparison | Put measured comparisons in evaluation; conceptual differences in related work | Avoid mixing feature descriptions and experimental findings |
| Windows/Linux configs, `if`, `for`, agent gate recipes | Keep a concise system paragraph with Windows development/Linux CI and the reverse; move full configuration recipes to the artifact | Show reuse for game-development and mixed-host teams without claiming shell translation or tested OS equivalence |
| Single-package and polyrepo support | Retain before formalization with explicit scope limits | Avoid presenting the result as monorepo-only or claiming unmeasured polyrepo scale |
| Dense campaign paragraph | Replace with RQ-based subsections and compact tables | Makes counts, denominators, refusals, and limitations inspectable |
| Eight timing cells | Show a small measured table or plot | More informative than a best/worst summary; no unsupported linear-scaling claim |
| Parser vectors, all seeds, environment digests, complete logs | Artifact with links from each result | Reproducibility detail should be accessible without consuming the argument |

“Move” means preserve the material in the full report or review artifact where appropriate. It does not mean silently drop inconvenient evidence or remove definitions required to understand a proof.

## Exact ten-page content budget

Sections should flow naturally; these are cumulative layout budgets, not instructions to insert forced page breaks between sections. Use normal IEEE typography and readable figures. The ten pages include title, abstract, figures, tables, conclusion, data availability, and AI disclosure.

| Section | Pages | Cumulative | Required content |
|---|---:|---:|---|
| Title, abstract, keywords | 0.65 | 0.65 | Concise problem, method, evidence, scope |
| I. Introduction | 0.75 | 1.40 | Mixed-chain failure, gap, three contributions |
| II. System and release protocol | 1.20 | 2.60 | Stage diagram, records/retry, repository layouts, Windows/Linux reuse, generic CI |
| III. Formal model | 2.70 | 5.30 | State, two windows, admission, channels, version selection, run transition |
| IV. Guarantees and proof arguments | 1.50 | 6.80 | Retry invariant, lemmas, eight conditional properties, counterexample |
| V. Evaluation | 1.90 | 8.70 | Saved campaign, full-profile limitations, timing, fresh mixed-chain controls |
| VI. Discussion and threats | 0.35 | 9.05 | Oracle, implementation, host, and external-effect limits |
| VII. Related work | 0.50 | 9.55 | Relevant build/release, deployment, saga, and verification antecedents |
| VIII. Conclusion, Data Availability, AI disclosure | 0.45 | **10.00** | Takeaway and accurate disclosure; preserve visual breathing room |
| References only | **2.00** | **12.00** | Relevant verified references; no extra results or appendices |

These are approximate page-equivalent writing allocations, not measured section lengths or forced page breaks. All figures and tables count. The formal core has more space than the original proposal because its assumptions and channel/version rules must remain self-contained. The Windows/Linux example is included in the system allocation, not added beyond the ten-page budget.

When adding practical examples, cut repeated framing and overly detailed abstract prose first. The current revision shortens the abstract and removes a repeated integration-contract paragraph from the introduction. Do not shrink fonts, compress margins, delete proof premises, or move essential reasoning to an unavailable appendix. Preserve some unused space at the end of page 10 for subsequent author edits.

The seven editorial exemplars are writing models; they do not all belong in the bibliography. Do not pad references to manufacture page 12. The current rendered gate passes ten content pages followed by two pages of legitimate references; rebuild after every substantive author edit.


## Make the mathematical contribution easier to assess

Start the model with a notation table tied to the example: package graph, build/publish stage, fixed commit, tag ledger, unit of intent, pending consumer, next version. Then separate two layers.

**Scheduling layer.** In the illustrative stage graph, each package has build and publish events. A local-artifact edge requires provider build completion before consumer build; a published-artifact edge requires provider publication before consumer build. Consumer publication follows its own build and the relevant provider publications. With successful stages and a finite acyclic package graph, these edges explain the required partial order. The revised manuscript includes the stage-order proposition and its proof. Its scheduling premise requires successful prerequisite stages; it is not proof that arbitrary commands fulfill their promised artifact contract. Topological sorting itself is established machinery.

**Recovery layer.** Preserve the existing formal distinctions: aggregating prerelease intent is not discharging delivered work; a source's release is not a consumer's receipt; deterministic planning is not exactly-once external execution. State the retry invariant before the cross-run theorems and explain how it can fail. “Unchanged configuration” alone does not imply that inherited channels remain unchanged as tags advance.

Keep the requested idempotence formula, but define its operator. For fixed reviewed inputs, let `release` denote a completed successful state transformation over the modeled release ledger. Then express `release(s) = release(release(s))` under those premises. Do not use the same formula to describe every interrupted attempt or arbitrary shell-side effects. A failed attempt can leave outstanding work; that is precisely why another run is useful.

A concise disclaimer can accompany the formula: “The property concerns recorded release state. If a publisher succeeds but its completion record is lost, its outcome must be reconciled, or the publisher must safely accept repetition.” The current formal model does not establish unconditional exactly-once effects across external registries.

Prioritize the proof chain: unchanged consumer window → preserved admission → stable version → discharge → shrinking outstanding plan. State the liveness premise that useful retries eventually make progress. The existing bound on propagation work is not a bound on Git scanning, manifest rewriting, shell execution, or end-to-end release latency.

## Evaluation organized around the claims

| Question | Evidence to present | What it does not establish |
|---|---|---|
| RQ1: Does execution respect both consumption modes? | A mixed-chain timeline; provider-publish barrier and local-build overlap; failed-provider case | Universal ecosystem behavior or fastest possible scheduling |
| RQ2: Does an interrupted release retain and discharge the intended work? | Version equality before/after failure, remaining package set, tag records, empty final rerun; bounded concurrent-push cases | All possible failure interleavings or external exactly-once writes |
| RQ3: How closely does the released planner implement the modeled semantics? | Separate core oracle agreement, selected vectors, and full-profile diagnostic differences | Full implementation refinement or full-profile conformance |
| RQ4: What is the observed planning cost? | All eight scale cells with topology, history/unit size, resource limits, repetition and dispersion | Cross-tool performance dominance or asymptotic complexity from a few timings |

### Results already available, without reinterpretation

- The Dispat 1.8.2 core campaign agrees on **1,500/1,500** generated cases within the restricted oracle's domain.
- The full profile has **1,500** cases: **997 accepted**, **503 E195 refusals**, and **1,914 differing package rows**. These are not 1,500 passing conformance tests. Preserve the distinction between accepted, diagnostic-clean, refused, and differing rows.
- Six selected specification vectors pass; they do not cover the entire semantics.
- The existing recovery campaign reports **24/24 episodes** converging within four runs under its tested fault model.
- Historical replay agrees on **36/42** and **7/64** versions for the two subjects. Explain policy reconstruction and tool-convention limitations rather than claim real-project version equivalence.
- Timing observations range from **0.017 seconds** for a 100-package layered graph to a **19.354-second median** for a 10,000-package chain, on the recorded contended host. Maximum observed RSS spans **15–118 MiB**. Show the actual cells rather than calling this “linear” or universally fast.
- Competitor fault measurements are pinned historical runs. They must remain visibly distinct from the new Dispat 1.8.2 campaign; different tools' check counts are not a common score.

These saved-campaign figures have now been reaggregated with the curated verifier, including 1,108 file hashes. That is an integrity check, not a fresh rerun of the entire campaign. The separately executed mixed-chain experiment is summarized below.

### Completed mixed-chain experiment and remaining portability evidence

The original mixed chain is now an executed operational experiment. For future reruns: Use an isolated downstream Docker builder or otherwise prevent accidental reuse of a local base image. Record stage events with monotonic timestamps and establish happens-before relationships; avoid relying only on an animated diagram or wall-clock screenshots.

Run the correct configuration, then an intentionally wrong control without the base-image publish barrier. Add a fully serialized control to distinguish correctness from permitted overlap. The local-output consumer should be allowed to build during the npm publish; the second Docker build must not start before the base image is available. Inject a refused base push and a downstream failure after base publication. Validate selected versions, published identities, completion records, and the final empty plan.

Label these controls as controlled configurations of the protocol, not defective competitor products. Existing two-package ordering tests support the mechanism, but inspecting their source is not a measured three-package npm/Docker/Docker experiment. The retained 9 September campaign ran five configurations twice and passes 106 assertions. It includes four repaired failures and eight unchanged reruns with no repeated stages. Source, raw logs, timestamps, tags, excluded attempts, and verification are in mixed-chain/. Two repetitions and injected delays support observed ordering, not comparative throughput.

A separate Windows/Linux fixture remains prospective. It should use a real Windows host and a real Linux host, shared referenced configuration, platform shell overrides, and native build tools. Compare selected stages, planned versions, gate outcomes, and retries. Environment-variable emulation on Linux is insufficient. The paper currently presents this as a practical integration capability; it does not claim a portability experiment or game-studio adoption.

## Risks to fix before calling the manuscript ready

1. **Novelty scope.** A DAG, a lock, and Git storage are not independently new inventions. Argue for the particular composition of stage availability, consumer-owned release obligations, and replay under stated invariants. Avoid “no other tool can do this” without a defensible scoped comparison.
2. **Strong retry assumptions.** Some stability lemmas follow directly from the invariant. Explain why applications can maintain it and give counterexamples when they cannot. Do not market conditional invariants as unrestricted guarantees.
3. **Proof/code gap.** The current source explicitly leaves refinement open. Keep that qualification beside the claims, not only in threats.
4. **Corrected stale prose.** Related work now distinguishes operational comparisons from formal instantiations. The unsupported self-hosting-study reference has been removed. Keep those corrections when revising.
5. **Evidence boundaries.** Distinguish illustrative examples, inspected integration-test code, newly executed experiments, and historical campaigns in every figure and table.
6. **Reference quality.** The active bibliography has 40 connected, distinct entries, with 19 DOI metadata records and primary-source checks retained. Recheck any entry or associated claim changed during author editing; connectivity alone never establishes factual support.
7. **Anonymity and artifact.** Preserve identifying originals privately; prepare a separate review copy and verify the artifact's content, not only its URL. Resolve public-preprint history before submission.

## Deliverables and next revision order

Completed: primary-source research on seven editorial exemplars; revised English system → mathematics → experiments manuscript; 10+2 pagination and visual checks; bibliography corrections; saved-campaign integrity verification; and a fresh private-registry mixed-chain experiment. The system also explains Windows/Linux orchestration reuse with a game-development example, within its measured-evidence limits. Downloaded third-party papers remain private research copies.

Next is the author's English edit. Use paper/saner/EDITING-REQUIREMENTS.md and the active main.tex; preserve the withdrawn manuscript as an archive. Rebuild and inspect after edits. Prioritize proof review, anonymous artifact preparation, and public-preprint eligibility. Optional new empirical claims about OS portability, specification packages, or CI onboarding need their own fixtures. Synchronize translations and patent materials only after the English scientific revision settles.

No submission, commit, push, release, or patent edit was performed for this handoff.

## Author-reported AI assistance

The disclosure has been corrected: most AI-assisted work used Claude Fable 5, with additional Claude Opus 5, Claude Fable 5.1, Gemini, and OpenAI Codex assistance. These model labels follow the author's account; exact identifiers, including the Gemini variant, should be confirmed from records before submission. Assistance across the work includes writing, proof arguments, harness code, experiment execution, and result summaries. Do not imply that Codex was the primary tool or that every named model performed every activity. Retain human responsibility and distinguish executed measurements from model-generated explanations.
