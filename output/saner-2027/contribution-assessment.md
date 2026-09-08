# Contribution assessment for SANER 2027

Research date: 9 September 2026. This is a targeted literature and tool-documentation review, not a systematic review or a proof that no earlier equivalent exists. It updates the narrower search recorded in `paper/icse/RELATED-MODELS.md` on 30 August. Sources are primary papers, author copies, project reports, and official tool documentation. Search-engine dates were not treated as publication dates.

## Recommended central claim

**An ecosystem-independent release protocol that combines stage-aware execution with a Git-backed completion ledger, preserving outstanding versioned obligations after partial failure.**

This is a stronger research claim than “using sagas for releases,” “works with every language,” or “CI never needs changing” in isolation. Those describe the motivation, applicability, and maintenance benefit. The scientific question is which invariants make the combined protocol safe and recoverable, under what assumptions, and whether the implementation exhibits those properties.

The manuscript should explain the whole system first. Its mathematical section then explains why consumer-relative admission, separate train and fresh-work windows, and completion records produce the stated properties. Experiments must test that explanation rather than merely list supported languages or successful commands.

## 1. Sagas and recoverable releases

Garcia-Molina and Salem introduced sagas in 1987. Their work decomposes a long transaction into independently committed transactions, with compensating transactions to amend partial execution. It is the conceptual antecedent, not a novelty attributable to Dispat. [Original Princeton report](https://www.cs.princeton.edu/techreports/1987/070.pdf), [SIGMOD paper DOI](https://doi.org/10.1145/38713.38742).

There is also explicit saga use in deployment-related orchestration. NEPHELE deliverable D4.1 describes a coordinator that implements lifecycle methods as saga rounds across topology, network-service lifecycle, and configuration modules. Its title page gives version 1.0 and submission date **27 December 2023**; relevant material is on printed pages 38–41. This is a public project report, not evidence of a peer-reviewed universal package-release protocol. It does defeat a broad assertion that sagas have never been applied to deployment operations. [Primary report](https://nephele-project.eu/sites/nephele/files/public/content-files/deliverables/nephele_d4.1.pdf).

Dispat's evaluated forward-recovery behavior should be described as **saga-inspired**. It preserves published results and completes outstanding obligations, rather than assuming every publication can be undone. Classical saga terminology must not silently promise compensation that the evaluated implementation does not provide. A missing completion record after successful external publication remains an ambiguous outcome and needs safe retry or reconciliation.

The potentially distinctive contribution is the release-specific protocol: how an intent retains its effect on an unfinished consumer after its provider has recorded completion, while maintaining version stability and admissible stage ordering. A search that finds no exact match supports further investigation, not “nobody has done this.”

## 2. One lifecycle across languages and non-code artifacts

Language-independent release automation already exists. Semantic-release explicitly supports package managers and languages through plugins. Release Please supports many language strategies and a generic `simple` strategy; its README explicitly excludes publication to package managers. Thus “any language” cannot establish novelty alone. [Semantic-release](https://semantic-release.org/intro/), [Release Please](https://github.com/googleapis/release-please).

A particularly important academic antecedent is Liu and Smith, **A Formal Framework for Component Deployment**, OOPSLA 2006, pp. 325–344. It defines platform-independent build, install, ship, and update transitions and proves version-compatibility properties. It explicitly models multiple industrial deployment mechanisms. This belongs in related work because it is much closer to the proposed common lifecycle claim than a conventional-commit parser comparison. Its abstraction concerns component deployment and compatibility; that does not establish equivalence to consumer-relative recovery of interrupted registry publications. [Author PDF](https://pl.cs.jhu.edu/projects/new-arch/papers/a-formal-framework-for-component-deployment.pdf).

Aeolus also formalizes component states, dependencies, and configuration reachability. Its general model permits constraints beyond Dispat's acyclic release graph. The useful distinction is the problem being solved, not suggesting that previous deployment models were informal. [Di Cosmo, Mauro, Zacchiroli, and Zavattaro, Information and Computation 239, 2014](https://doi.org/10.1016/j.ic.2014.11.002).

For Dispat, define a package as a **versioned release unit**. An integration supplies its identity, version policy, dependency and availability requirements, stage commands, and trustworthy completion interpretation. A specification can validate or render during build and publish versioned files during publication. It need not contain executable program code.

Prefer “a common protocol for conforming integrations, including software and specifications” to “a standard that works for every programming language.” “Standard” could imply external standardization or adoption that has not been demonstrated. The current model also has explicit limits, including SemVer-compatible versions, acyclic package graphs, and retry assumptions.

An additional formal observation could make this breadth precise: if two integrations yield the same normalized planning inputs, their ecosystem labels do not change the plan. However, this is a property of the abstraction, not proof that every real adapter conforms. A theorem that adapters preserve model guarantees would require a refinement argument and explicit handling of failed, delayed, and ambiguous external effects. Do not manufacture a major theorem by merely observing that the equations contain no language names.

## 3. Stable CI with package-local configuration

The third benefit is real and measurable: **add a package by defining its tasks and dependencies, without duplicating its identity and ordering in the CI workflow**. The same generic runner can invoke tests and releases from the package graph. This is especially useful when the graph includes code, containers, infrastructure, documentation, and specifications.

Affected-task execution and generic graph-driven CI already exist. Nx documents deriving affected projects from Git changes and the project graph. Spinnaker supports parallel pipeline stages and execution histories. Therefore the comparison must include these established capabilities rather than contrasting Dispat only with a manually hard-coded pipeline. [Nx affected tasks](https://nx.dev/docs/features/ci-features/affected), [Spinnaker pipelines](https://spinnaker.io/docs/concepts/pipelines/).

The bounded claim is that package onboarding within an existing execution environment does not require workflow edits. New operating systems, tools, credentials, permissions, trust boundaries, or deployment destinations can still require infrastructure changes. Tests and releases may share a package graph while intentionally using different selection windows. A common graph does not prove test completeness, enforce a missing-script policy, or by itself prevent a privileged user from bypassing CI.

Repository inspection supports the intended architecture: `.github/workflows/tests.yml` invokes `dispat run tests --since ... --consumers`; the release workflow invokes `dispat run tests --since all`. This inspection is not a controlled onboarding experiment and should not be reported as one.

## Evidence that would make these claims persuasive

1. **Original mixed chain:** npm local artifacts → Docker base → Docker consumer. Demonstrate permitted build/upload overlap and required publish-before-build barriers. Inject publication and consumer-build failures; inspect retry versions and retained obligations.
2. **A non-code package:** version and publish a specification together with a consumer. Assert that no language-specific planner path is needed. Keep semantic compatibility of the specification outside the automatic bump guarantee.
3. **CI extension experiment:** hash an unchanged workflow, add packages of several artifact types through configuration, and verify discovery, selected tests, fail-closed publication, and successful releases. Record configuration edits as well as workflow edits; moving work into another file does not make it zero work.
4. **Mechanism ablations:** compare removal of the publication barrier, provider-relative rather than consumer-relative recovery admission, and a manually enumerated CI package list. Attribute each failure to the omitted mechanism. A generic workflow can encode the correct protocol; do not claim it is intrinsically incapable.
5. **Correctness boundary:** distinguish model proofs, adapter assumptions, saved campaign results, fresh executions, and setup failures. The current loopback-registry failures are excluded setup attempts, not protocol results.

## Manuscript changes made in this review

- Introduction now foregrounds the common protocol and includes specifications as release units.
- System section now states the integration contract and a stable-CI-entry-point subsection.
- Related work now acknowledges the Liu–Smith model, Aeolus, and NEPHELE's explicit saga orchestration.
- References added for those three sources; the review pseudonym replaces the identifying specification title in the bibliography.

The requested system → mathematics → experiments order is preserved. The final draft has ten content pages and two reference pages. The fresh mixed-chain campaign passes 106 assertions across ten case repetitions, including four repaired failures and eight unchanged reruns without repeated stages. See READINESS.md for verification and remaining author decisions. This is a handoff for human editing, not a submission or an acceptance prediction. Nothing has been submitted, committed, or published by this review.

## Additional practical benefit: Windows/Linux orchestration reuse

The system section now explicitly motivates Windows development with Linux CI, and the reverse, through game-development server builds and native packaging. Shared configuration carries graph/lifecycle/portable commands; referenced platform files select shells and platform-specific scripts. This is useful for mixed-host teams, but it is not shell-language translation, cross-compilation, an established first-of-its-kind claim, or a measured portability result. A native two-OS experiment is required before claiming equal behavior: retain versions, command traces, test gates, and failure/retry outcomes on both systems. The existing 1.8.2 `/bin/sh` requirement for the conditional wrapper remains explicit.
