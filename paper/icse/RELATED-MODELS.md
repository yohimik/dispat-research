# Formal models of git/VCS in the literature - verified references

2026-08-28. Purpose: independent evidence that the paper's model objects
(commit DAG + reachability, package dependency graphs, LCA-based
branching) are the standard formal reading, not ad hoc. All entries
verified via web search this session; URLs at bottom.

| Work | Venue | What it formalizes | Which of our Definitions it supports |
|---|---|---|---|
| Bird, Rigby, Barr, Hamilton, Germán, Devanbu, *The Promises and Perils of Mining Git* | MSR 2009 | The commit DAG with reachability as the working model of git history in empirical SE; documents the pitfalls (rebases, foreign DAGs) | Def. history (DAG, reach, ⪯); our ancestry-not-time stance |
| Kaki, Priya, Sivaramakrishnan, Jagannathan, *Mergeable Replicated Data Types* | OOPSLA 2019 (PACMPL 3, art. 154) | Derives three-way merge "à la git" from the DAG's least common ancestor; git's branching model as formal substrate for replicated data | Def. history; branches/merges as first-class formal objects |
| Swierstra, Löh, *The Semantics of Version Control* | Onward! 2014, pp. 43–54 | Separation-logic-style semantics for VCS operations | The enterprise: repositories as objects of formal semantics |
| Angiuli, Morehouse, Licata, Harper, *Homotopical Patch Theory* | ICFP 2014 (JFP expanded) | Patch theories as higher inductive types; models as functors | Same enterprise, patch/content side |
| Mimram, Di Giusto, *A Categorical Theory of Patches* | ENTCS 298, 2013 | Merging as pushout in a category of files/patches | Same enterprise, merge semantics |
| Mancinelli, Boender, Di Cosmo, Vouillon, Durak, Leroy, Treinen, *Managing the Complexity of Large Free and Open Source Package-Based Software Distributions* | ASE 2006 | Formal model of package repositories and dependencies (installability as SAT) - the EDOS line | Def. workspace (packages + dependency graph as formal objects) |

## The positioning sentence this buys

The paper's model reads a repository as exactly the objects these works
use - the commit DAG with reachability (Bird et al.; Kaki et al.'s LCA)
on one side, formal package-dependency graphs (EDOS) on the other -
and *differs* from the patch-theoretic line (Swierstra–Löh, HPT,
Mimram–Di Giusto) in tracking no file contents at all: only history,
tags and messages, which is what makes a release plan a pure function
of the repository. Both halves of the model therefore have independent
formal lineages; their composition for release engineering is the
contribution.

## Sources

- https://dl.acm.org/doi/10.1109/MSR.2009.5069475
- https://dl.acm.org/doi/10.1145/3360580
- https://dl.acm.org/doi/10.1145/2661136.2661137
- https://dl.acm.org/doi/10.1145/2628136.2628158
- https://arxiv.org/abs/1311.3903
- https://www.researchgate.net/publication/29599445 (EDOS ASE 2006)

## Novelty check: sagas applied to software releases (2026-08-30)

Question: does any published work apply the saga pattern (or any formal
distributed-transaction treatment) to package releasing / release
engineering? Five searches from different angles.

Findings:
- "saga pattern" + release engineering / package publishing: nothing
  academic. All results are the classic saga domain, microservice data
  consistency, plus practitioner blogs.
- Transactional deployment / CI-CD + saga: generic pipeline-resilience
  prose and microservice papers; no release-engineering treatment.
- arXiv phrasing (release orchestration, publishing atomicity, registry
  failure recovery): only practitioner tooling guides (changesets,
  lerna, nx); one blog comment describes hand-rolled "restartable
  release flows" for semantic-release monorepos, which documents the
  pain but offers no model.
- RELENG venue: empirical and process studies; no formal transactional
  account of publishing.
- Closest academic neighbor found: Anvil (Sun, Ma, Gu, Ma, Chajed,
  Howell, Lattuada, Padon, Suresh, Szekeres, Xu; OSDI 2024, Best
  Paper) verifies liveness ("eventually stable reconciliation", a TLA
  formula) of Kubernetes controllers in Verus. Same spirit as our
  G6/idempotency claims: proved forward-recovery convergence for an
  operations loop. Different domain and different constraint: a
  controller reconciles mutable cluster state it can overwrite; a
  release writes immutable versions to registries it cannot reconcile,
  which is exactly why recovery must be replay-with-a-log rather than
  overwrite-toward-desired-state.

Conclusion: no prior work found applying sagas or a formal transaction
model to package releases; the paper's novelty claim stands as scoped
("composing the two halves for release engineering is what is new").
Anvil added to related work as the nearest neighbor, which strengthens
positioning rather than threatening it.

## Turborepo / release-please literature check (2026-08-30)

Searched for academic work on Turborepo or release-please (release
management, versioning, formal treatment). Nothing scholarly exists;
results are vendor documentation, practitioner blogs and GitHub
threads. Turborepo's own documentation delegates versioning and
publishing to the Changesets CLI, which is how the paper represents it
(Section 6 boundary-case paragraph; executed in Section 8.4 as
changesets 3.0.1 under turbo 2.10.12). No new citations added.
