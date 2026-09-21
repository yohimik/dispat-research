# CCME mathematics, complexity and evidence review — 20 September 2026

The specification and conference abstract were revised. **The complete planner is not certified time- or memory-optimal.** Several individual bounds are tight under their input/output assumptions; the inspected implementation has concrete avoidable costs. Product implementation work remains separate from the specification edits authorized in this task.

## Provenance and scope

`provenance.json` identifies the initial, dirty product working-tree snapshot at HEAD `784a4971dfc3936be824469b6a7156383ebb7534`, specification label `3.1.0-rc.1`. `snapshot/` preserves the original specification and relevant implementation files. The pre-existing edits were preserved. The user's later request explicitly authorized editing the CCME specification in the product repository; no product source, release, tag or campaign result was changed by this review. The active paper is `paper/saner/`; the separate technical report was not rewritten.

## Findings and disposition

1. **P1 — Unbounded single-source propagation cache; shallow requests do unnecessary transitive work.** In the inspected `services/dispat/internal/plan/propagate.go`, `walk` routes a single source through `from`, which always calls `walkLiteral` with unbounded depth and retains the result in `single`. Only `exact` target entries are charged to `walkCacheBudget`. A chain with one depth-one request per package needs `P-1` returned targets; these cached unbounded walks retain `P(P-1)/2`. Budget every tier, key and empty entry; use depth-bounded misses or incremental BFS extension. **Specification guidance fixed; product code still needs a fix.**

2. **P2 — Marker transposition loses the advertised word-parallel work saving.** `ancestry.go:pass` propagates word masks, then enumerates each set bit to build marker columns. A chain with every commit marked contains `H(H+1)/2` set bits. The transpose therefore adds scalar quadratic work, and both layouts coexist during construction. The 512-marker batch cap limits scratch width, not total work. **Spec now distinguishes propagation, transpose, word padding, scratch and retained storage. Product code still needs representation work.** The factor is a word-RAM claim; with fixed 64-bit words it is not a different polynomial degree.

3. **P2 — Correction and cancellation accounting omitted multiplicative work.** Non-wildcard corrections still inspect package/target pairs for containment, liveness and application. Cancellation is queried for propagated candidates as well as direct incidences, including rejected candidates absent from final output. The implementation's `cancelledFor` scans its cancel list per query. **Spec adds `Jcorr`, `Jc`, cancel-mask construction and diagnostic-attribution qualifications.** A scalar implementation does not inherit a bitset bound merely because ancestry is indexed.

4. **P2 — Retained provenance is not total construction work.** Repeated `prov[d] |= sources` can perform duplicate insertions even when retained `Z` does not grow. **Spec distinguishes examined incidences `Zv` from retained/emitted `Z`, and recommends indexed in-place insertion.** A unique-output lower bound is not a proof that a particular deduplication procedure attains it.

5. **P2 — Direct-channel pseudocode accepted a no-op as the winner.** On baseline beta, newest `%beta` and older `%stable` in the fresh window, the previous pseudocode returned beta although the prose excludes no-op proposals. **Pseudocode and new vector 82k now skip the no-op, count the complete proposal set, and choose stable.** Inspected product code already checks no-op proposals; this is not reported as a confirmed product defect. Candidate summaries may save list storage if diagnostics are deferred and remain ordered.

6. **P2 — Two optimization vectors overclaimed their counterexamples.** Vector 82d previously claimed that channel-set hoisting could invent reachability without an edge. It now adds a stable consumer of the beta-only source, exposing the actual admission error. Vector 82g previously inferred baseline-only resolution from zero propagation depth, overlooking direct channels and unaffected direct bumps. **Both vectors corrected.**

7. **Cost qualifications.** The zero-marker path still pays graph/input overhead; boundary-only mask interning does not bound correction/cancel masks by `k+1`; unsorted-name comparison sorting is a conditional lower bound, not an instance-optimality proof for pre-ranked names. **Spec now states these qualifications, adds a memory ledger, and lazily memoizes inherited origin-channel computation without executing an otherwise unused diagnostic branch.**

## What can be defended

| Phase | Defensible result | Optimality boundary |
|---|---|---|
| Message scanning | Linear bytes, constant scanner state plus parsed output | Worst-case scan time is tight; copying/normalization buffers still count |
| Scope resolution / glob matching | Indexed literal/prefix lookup; linear pattern/candidate matching | Candidate scans, index construction and matcher scratch remain explicit |
| History/window indexing | Correct marker propagation on a DAG; reusable boundary classes | Dense indexes trade time for memory; a chain admits a much smaller position index |
| Corrections and cancels | Indexed ancestry plus incidence/query-sensitive work | No blanket linear bound in units or final contributions |
| One multi-source propagation walk | Linear reached vertices/edges, shortest distances, source exclusion | Reuse is input-dependent; all-source caching can be worse on shallow queries |
| Channels, direct bumps and holds | Linear scan of relevant incidences after ordering/resolution | Complete diagnostic output must be preserved; summaries can reduce retained lists |
| Versions and disjoint groups | Scan each member once using precomputed aggregates | Does not re-prove shared-group cross-run guarantees; fixed counters have weaker retry behavior |
| Canonical publish order | Heap time `O(E + P log P)`, `O(P)` auxiliary space | Tight worst-case comparison sorting for initially unsorted names |
| Blocking membership | One incremental multi-source traversal, `O(P+E)` | Listing every cause or path has additional output cost |
| Fleet closure | SCC condensation of dependency/group graph, then repository-set unions | Dense `P × Q` storage is an option, not an unavoidable lower bound |
| Fleet evidence and settlement | Shared tree reads/routes; one record per changed recording repository | Tree bytes, retained pins, revalidation, hooks and network effects are additional |

The existing eight recovery guarantees retain their retry invariant and single-history/forward-release boundaries. A finite number of progress-making runs is not a bound on arbitrarily many failed retries. Rollback's historical artifact inventories, adapter operations and external execution are not covered by ordinary-release planner bounds. No external exactly-once claim was added.

## New mathematical checks

Run `python3 check_math.py` from this directory. `math-checks.json` retains results: all 1,024 DAGs on five vertices under a fixed order, 32,768 marker configurations, and 158,720 source-set/depth configurations. The checks compare marker propagation against explicit ancestor traversal and composed single-source distances against multi-source BFS. They also retain the no-op channel counterexample, zero-marker accounting case and exact chain operation counts. At 512 packages the shallow queries return 511 targets, while unconditional full-walk caching retains 130,816 entries.

These are generated configurations and analytic operation counts, not independent samples, measured allocation totals, product benchmarks or a proof for arbitrary inputs. They are not pooled with the paper's frozen campaigns.

## Experiment review: how much evidence, compared with what?

`experiment-review.json` and `experiment-snapshot/` preserve the inspected product records and harness hashes. The local product `coverage/experiments/` contains **12 cells**, all labeled Dispat **1.7.1**, from three scenarios crossed with four tool configurations. Its current harness defines **16 cells**, adding build/publish propagation cells for Dispat and Lerna; no retained records for those four were present in the inspected coverage directory. The 12 verdicts predate the current binary-hash fields and do not identify the current candidate. They must not be relabeled as contemporary results.

The orphan records show that **all four tools eventually publish the refused consumer**. The difference is the intermediate record state and recovery procedure: Lerna/Nx had a tag for an unpublished version; Changesets and Dispat did not in these configurations. Lerna's first retry needed cleanup before its successful recovery. A failed named predicate is not a universal failure of that product, and unequal check counts cannot form an aggregate tool-quality score. Midrelease outcomes also depend on the prescribed rebase/push procedure.

The new propagation harness is useful but not a matched superiority experiment. Dispat receives explicit caret propagation intent, Lerna an ordinary fix; their selected release sets differ. Lerna's protocol manually publishes the provider and attempts the consumer, while Dispat's scheduler can finish other independent packages. Consequently “one package recovered versus five” would conflate scheduling and selection with retry semantics. Retain each tool's original obligations, completed set and residual set; compare recovery to its own residual before claiming a difference. The harness also overwrites cell directories, so research runs must use unique immutable output roots and archive raw attempts.

| Evidence | Coverage strength | What the count does not establish |
|---|---|---|
| 120 primary mechanism episodes | Complete designed matrix: 5 graphs × 2 channels × 4 fault targets × 3 boundaries | Industrial reliability, crash recovery, arbitrary graphs or fleet behavior |
| 20 additional controls | 10 no-fault and 10 foreign-content cases | 20 more random fault trials |
| 84/120 losing analytical alternatives | Same episodes and completion states; 70% lose unfinished work under source-based discharge | Competitor win rate or production failure prevalence |
| 772 finite model states | Exhaustive reachable states in the stated four-node/single-origin projection | Independent statistical observations or full-language refinement |
| 300 generated Git histories | Fresh restricted reference-model agreement | Full semantics; historical broader-oracle discrepancies remain |
| 12 retained product comparison cells | Concrete registry/Git behavior in named configurations | A broad field study or current candidate validation |
| 8 historical scale cells | Illustrative time/peak-memory growth up to 10,000 packages | Optimality, controlled asymptotic isolation or cross-tool speed superiority |

The 120 episodes are substantial **coverage of a small designed mechanism matrix**, not a large deployment study. More repetitions of the same deterministic cases would mostly increase the headline. The abstract now leads with recovery of all 120 fault episodes and explicitly names the analytical comparison: lost work in 84/120 (70%). It keeps implementation and production boundaries visible and removes the undifferentiated list of episode/state/check totals.

## Highest-value next runtime experiments

1. **Fleet recovery:** source-owned histories, consumer boundary reconstruction, control versus linked-peer topology, partial settlement and retry. This addresses the manuscript's main unvalidated extension; pin a candidate binary separately from the released campaigns.
2. **Actual process termination:** kill the controller after externally durable publication and before completion recording; retain stale locks and dirty worktrees; report required operator reconciliation rather than quietly clearing them. This adds a failure model the existing nonzero publisher response does not test.
3. **Time/memory isolation:** cold depth-one chain queries, dense propagation output, many history boundaries, and wide repository closures. Compare semantic equality, peak memory and work counts under an explicit cache budget. Pin before/after binaries and hold output/provenance settings constant.

The choice should address a claim gap, not inflate counts. No new runtime result may be inferred from the new mathematics checks, the presence of scripts, or the missing four propagation cells.
