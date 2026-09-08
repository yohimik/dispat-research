# Experiment plan for the CCME/dispat paper

Working notes, 2026-08-28. Maps the reviewer feedback (P1–P7) and our own
ideas (U1–U3) onto concrete experiment designs E1–E4 and a mechanisation
track M. Feasibility and risks stated per item; priorities at the end.

| Feedback | Addressed by |
|---|---|
| P1/P2 model ↔ arbitrary repo made explicit | paper §4.4 (done, v8) + E1 |
| P3 automated proofs (e.g. Lean) | M |
| P4 specific instance → expected plan → compare with dispat | E1 (and the existing 240 vectors are already this shape) |
| P5 hundreds/thousands of packages: time, graph size, recovery steps, cost growth | E4 |
| P6 experiments proving practice | E2 + E3 |
| P7 serious 10k+-commit repos (z3, cbmc, llvm) | E3b + E4a |
| U1 compare lerna/nx/release-please against their calculated model | E2 (model calculated in paper §6, v8) |
| U2 replay convention-following repos against their actual releases | E3a |
| U3 drop webhooks, keep delivery potential | paper edit (done, v8) |

---

## E1. Differential validation: model oracle vs dispat

**Role.** Not an evaluation experiment but the validation of §4.4's
refinement claim - and exactly P4's shape, executed by a generator instead
of by hand. It cannot be replaced by a real repo: the question requires
instances whose *expected* plan is independently computable, which means
constructed or generated instances by definition. Presented in the paper
under conformance, not as a headline result.

**Claim tested.** The refinement claim of paper §4.4: dispat computes the
model's Π(σ) and ν_σ.

**Design.**
1. Write an *independent* oracle implementing §4 of the paper - and nothing
   else - in ~500 lines of Python. Clean-room rule: the author of the oracle
   reads only the paper, not SPEC.md and not the Go code. This doubles as a
   test of the paper's self-containment (P1): if the oracle cannot be written
   from the paper alone, the paper is not self-contained.
2. Instance generator: random workspaces (P ∈ {5..50}, layered DAGs with
   configurable fan-out), random histories (linear + merges), random unit
   streams over the full directive grammar (weights favouring realistic
   commits), random tag states σ (including prerelease baselines, holds,
   pending cancels).
3. For each seeded instance: oracle plan vs `dispat status --json` plan.
   Byte-compare package set, versions, channels, and the reason codes.
4. Metamorphic runs: simulate `run(σ, F)` for adversarial F (random subsets,
   worst-case blocking chains) by writing the tags the model says a run
   writes, then re-plan. Assert G2–G6 as runtime properties across the
   sequence (plan shrinks; versions stable; empties within n runs).

**Output for the paper.** "N randomised instances, zero divergences" (or the
divergences found - either is a result). Extends the existing conformance
argument from 240 hand-written to ~10^4–10^5 generated instances.

**Feasibility.** High. 1–2 weeks. No external services; fake registry not
needed (plan-level only). Risk: JSON plan output completeness - verify
`status` exposes channels + reasons (it does: Releases[].Channel/Reason).

## E2. Competitor comparison on shared fixtures (U1)

**Claim tested.** Paper §6's frozen-directive reading of lerna / nx release /
release-please, and the at-most-once vs exactly-once distinction - as
executable fact, not documentation reading.

**Why sandboxed, and why not toy.** Fault injection needs a registry we
are allowed to break, so the registries are local (verdaccio, local Docker
registry) by necessity - controlled fault injection is the standard
dependability methodology and is read as such. The *workspace* does not
need to be synthetic, though: the primary substrate is a mirrored real
workspace - a checkout of googleapis/google-cloud-node (~100 real packages,
real graph, real history) with its publish targets retargeted at the local
registry. Real graph and commits; sandboxed only where physics demands.
The paper's six-package fixture family remains as smoke tests only. Note
z3/cbmc/llvm cannot serve here at all: they use none of the compared tools
and have no multi-package conventional-commit process, so there is no
comparison to run on them - they carry E3b/E4a instead.

**Design.**
1. Substrate A (primary): mirrored google-cloud-node as above. Substrate B
   (smoke): npm workspace, packages {core; cli,ui,api → core; theme,docs →
   ui} (the paper's running graph). Scenarios: single fix; feat + breaking;
   fix in a leaf; mixed-package commit; prerelease.
2. For each tool - `lerna version --conventional-commits` (independent and
   fixed), `nx release version --dry-run` (independent and fixed),
   `release-please release-pr` with node-workspace, `dispat status` - record
   the computed plan. Compare each against (a) its own model as calculated in
   paper §6 (validates our reading), (b) dispat with the equivalent explicit
   directives (`fix(x)^^`), expecting agreement on the version arithmetic.
3. **The orphan experiment** (the headline): local npm registry (verdaccio),
   publish with a fault injector that fails exactly one package's upload
   (npm lifecycle hook or a proxy that 502s one name). Then:
   - lerna: observe tags already written for the failed package; run
     documented recovery (`lerna publish from-package`); record that it
     recovers npm - then repeat with a two-target fixture (npm + local
     Docker registry) and record that no documented recovery exists for the
     image.
   - release-please: merge release PR, fail the CI publish job; observe tag
     exists, artefact absent; record the manual re-run path.
   - dispat: same failure; observe no tag written, re-run resumes, versions
     identical (G2/G3 live), converges (G6).
4. Record everything as machine-readable traces; the paper gets one table
   and one figure (runs-to-convergence per tool).

**Feasibility.** Medium. 2–3 weeks. Risks: nx release and release-please
need care to run hermetically (release-please wants a GitHub repo - use a
local Gitea or the `release-please` CLI's manifest mode against a file
remote; fall back to documented-behaviour-only for the parts that cannot run
hermetically, and say so).

## E3. Historical replay on real repositories

### E3a. Convention-following repos: expected data exists (U2)

**Claim tested.** dispat's computation agrees with what disciplined projects
actually released - on their own history, not on fixtures.

**Candidates** (release data = tags + release PRs, commit convention
enforced):
- googleapis/google-cloud-node - release-please manifest mode, ~100+
  packages, years of history. The manifest and PR trail give exact expected
  versions per release.
- googleapis/google-api-nodejs-client and sibling repos - same tooling.
- babel/babel - lerna, conventional-ish commits, long history.
- nrwl/nx - releases itself with nx release, conventional commits.
- angular/angular - strict conventional commits (they wrote the convention),
  custom releaser; expected data in tags.
- jest (historical lerna era) - smaller, good pilot.

**Protocol.** For each of the last k releases: checkout the commit *before*
the release commit; generate dispat config (spaces from the workspace
layout, edges via `dispat compute`, lenient parsing, type map matched to the
repo's convention); run `dispat status`; compare the planned (package,
version) set against the actually-released set (from tags / release PR).
Where feasible, also run the repo's own tool in dry-run at the same commit
(three-way comparison).

**Metrics.** Exact-agreement rate per release and per package; divergence
taxonomy: (i) non-conventional commit in window, (ii) manual override /
Release-As-equivalent, (iii) dependent-bump semantics differ (their ^^-patch
vs our explicit), (iv) our bug. Class (iii) divergences are *predicted* by
paper §6 - finding them at the predicted places is a positive result.

**Feasibility.** Medium-high. Config archaeology is the cost; googleapis
repos are the easiest (machine-readable manifest = expected data). 2–4
weeks for 3 repos × 10 releases.

### E3b. The reviewer-suggested repos: z3, cbmc, llvm

z3 (~40k commits), cbmc (~30k), llvm-project (~500k) do **not** follow
conventional commits and are single-product or subproject-monolithic, so
version-agreement replay does not apply. Use them for what they are:
- **Adoption experiment** (paper's §19.7-style): point dispat at the repo
  with a minimal config, lenient mode; measure the first plan on a mature
  history - parse rate, diagnostics volume, time. Shows behaviour on hostile
  (convention-free) input at scale.
- **Performance corpus** for E4a: real DAG shapes (llvm's merge topology),
  real tag volumes (llvm has ~1k+ release tags), real message sizes.
- llvm subprojects (clang, lld, mlir, ...) can be declared as packages with
  path-derived scopes to get a realistic 20-package × 500k-commit workspace
  for cost measurement - versions synthetic, costs real.

## E4. Scale and cost growth (P5)

**Claims tested.** The complexity paragraph of the paper; G6's bound as an
empirical curve; "works at hundreds/thousands of packages".

**Design.**
- **E4a real-history axis** (commits C, tags T): dispat plan time and peak
  RSS on z3 / cbmc / llvm checkouts as above; C scaled by `--since` depth:
  10^3, 10^4, 10^5 commits.
- **E4b synthetic-graph axis** (packages P, edges E): generator from E1
  scaled to P ∈ {100, 1 000, 10 000}; shapes: layered, chain (worst depth),
  star (worst fan-out), scale-free. Measure plan time / memory vs P, E, U;
  fit against the stated bounds (expect ~linear in P+E for planning; report
  the constant).
- **E4c recovery growth**: for n = |Π(σ₁)| ∈ {10, 100, 1 000} and failure
  probability p ∈ {0.01, 0.1, 0.3} per publish: simulated runs to empty
  plan (validates ≤ n; expected value under random F), number of catch-up
  releases, blocked-set sizes. One figure: runs-to-convergence vs n and p.
- **E4d lock and order overhead**: publish-order computation time at 10k
  packages; lock round-trip against a local remote.

**Feasibility.** High for E4b/c/d (pure computation, seeded, CI-runnable);
E4a needs disk + patience for llvm. 2 weeks. Hardware: one machine, report
spec; all scripts and seeds in the repo for reproduction.

## M. Mechanised proofs (P3)

**Target.** Lean 4 + mathlib. The model was written to be finite and
set-theoretic; nothing needs coinduction or real analysis.

**Staging.**
1. Definitions of paper §4 as Lean structures over `Finset`/`List`
   (instance, window, src, adm, Π, ν, run). ~1–2 weeks.
2. Lemmas W/S/C and G1–G8 as theorems. The paper proofs are already
   lemma-factored; expect the hard 20% in Lemma C and G6's variant. ~3–6
   weeks.
3. The six obligations as *counterexample theorems* (∃ instance violating
   the unamended claim) - falsification mechanised too, which is unusual
   and reviewable.
4. Bridge to E1: generate instances in Lean, export JSON, feed the same
   instances to the Python oracle and to dispat; three-way agreement. This
   is the strongest available substitute for verifying the Go code itself.

**Alternative/complement.** TLA+ model of the run/publish interleavings
(concurrent runs + lock + adversarial failures), checked with TLC/Apalache
for small instances - cheap, catches protocol races the Lean pass
(sequential runs) does not model.

**Honesty note for the paper.** Mechanisation verifies the model, not the
Go binary; the differential bridge (M.4/E1) is the link, and stays sampling-
based. Say exactly that.

## Priorities

1. **E1** (fast, directly answers P4, feeds M.4) - do first.
2. **E2** (the headline orphan experiment; answers P6/U1).
3. **E3a** on googleapis + one lerna repo (answers P6/U2 with real data).
4. **E4b/c** synthetic scale (answers P5 cheaply), then **E4a/E3b** on
   z3/cbmc, llvm last.
5. **M.1–2** in parallel (independent of the experiments).

Minimal credible revision for resubmission: E1 + E2 + E3a(2 repos) + E4b/c,
with M started and stated as in progress.

## 2026-08-30 extension (P5/P6 follow-through)

E2 extended to the full competitor set at the latest published
versions: lerna 10.0.1, nx 23.1.2 (nx release, requires @nx/js),
turbo 2.10.12 + changesets 3.0.1 (Turborepo's documented release
path; the in-repo harness names this flavour `changesets`, since
turbo delegates every release step to it). Each phase on a fresh registry, run twice, identical
transcripts. Findings written into Sections 6 and 8.4: lerna and nx
tag before publish (orphan observed in both), nx recovers by registry
query without lerna's dirty-tree block, changesets tags after publish
but recovers by registry query and consumes its changeset files (not
replayable). release-please stays documentation-level in the orphan
setting (GitHub-API-bound, publishing delegated to CI); its executed
evidence remains the Section 8.5 replay. Every dispat-side experiment was
rerun on the 1.7.0 image on 2026-09-02 and on the 1.7.1 image on
2026-09-04 (see below).

## 2026-09-02 extension: E5, the concurrent push (mid-release)

The fault no unit test reaches besides the refused upload: a
colleague's commit lands on `origin/main` while the release runs.
Same six-package fixture and registry as E2; a git shim first on
`PATH` records every git call the tool makes and fires the
colleague's push once, immediately before the tool's first push of
the branch (dispat's lock push excluded), so the interleaving is a
point in each tool's sequence, not a timer. Scenarios: clean (no
overlap) and conflict (edit beside the version line of
`core/package.json`). After the run: the operator's recovery (`pull
--rebase`, `push --follow-tags`), each tool's next plan, and for
dispat a rerun from the same clone. One observer joins clone, origin
and registry into per-package states (consistent, unpushed, dangling,
orphan, unrecorded, baseline).

Results (paper Section 9.5, table row "push race" in Section 6):
lerna 1/5 and 2/5, nx 2/6 twice, changesets 3/5 twice, dispat 1.7.0
12/12 and 14/14 (merge onto the release commit, W242/W243, next plan
is the colleague's change alone, rerun releases it). dispat 1.6.0 on
the same cells: 5/12 and 6/14, E224 at the rejected push with the
four versions published and their tags local only; status plans
nothing, rerun refused. Orphan control 7/7 on both versions.

The harness is in the repository at `tests/experiments` (no paper
reference in repo content). Since 1.7.2 it runs inside every release,
as the docs package's beforeBuild hook against the image the run has
just published, and the site page https://dispat.dev/internals/experiments/
is built from what it recorded; the Experiments workflow is the
by-hand run for any released version. Raw records of the 1.6.0 vs
1.7.0 comparison are kept outside the repo in
`~/Projects/dispat-experiments/results/v170/`.

## 2026-09-02 rerun: E1 against the 1.7.0 image

The differential campaign was rerun with the binary copied out of the
official `yohimik/dispat-alpine:1.7.0` image
(`~/Projects/dispat-experiments`, `BIN_STAGE=relimg`,
`DISPAT_VERSION=1.7.0`), so the paper's Section 9.3 is about the
current release. Golden gate PASS. Core profile: 1000/1000 (seeds
1..1000) and 500/500 (seeds 5001..5500) exact. Full profile: 1000
instances, 412 clean, PG1 409 / PG2 240 / PG2x 58 / PG3 390; 500
instances, 222 clean, PG1 182 / PG2 135 / PG2x 23 / PG3 200; nothing
unclassified. Per-seed rows are identical to the 1.6.0 and 1.4.0
campaigns on all 3,000 instances (only the `dispat` version field
differs), which is expected: the 1.6.0 to 1.7.0 planner diff is
`AliasFilter` plus the W242/W243 codes, and the fix is to the run's
protocol. Records: `~/Projects/dispat-experiments/results/v170/e1-core/`
and `e1-full/`.

## 2026-09-04: the harness review, and E5 on the 1.7.1 image

A review of `tests/experiments` found 22 defects, all fixed before the
1.7.2 release: the entrypoint's pipeline subshell masked exits (a
registry that never started was a run that passed for every compared
tool), a gating assert passed vacuously on empty variables, assert
output was discarded, an empty check list passed, the readiness poll
watched verdaccio while the first request went to the proxy, the
observer fetched into the clone under test between steps (it now
builds a scratch bare observer repository per observation), the shim's
fired marker was not atomic and its log was not line-oriented (one JSON
object per call now), the proxy denied by substring over the whole
path and dropped chunked uploads, fixture commits carried no fixed
dates, and the npm tools had no lockfile. The twelve cells rerun on
the 1.7.1 image, twice, after the fixes: identical to the 1.7.0
records cell for cell (dispat 7/7, 12/12, 14/14; lerna 3/5, 1/5, 2/5;
nx 4/5, 2/6, 2/6; changesets 5/5, 3/5, 3/5). The only observable
difference is timing: a refused publish now takes about seventy
seconds, npm's three retries against a clean 502, where the poisoned
connection used to end it after two.

## 2026-09-04: the 1.7.2 release, E1 and E5 on its image

1.7.2 (run 33814306152 tests, 33814918103 release) is the first release
to run the twelve cells inside itself and to publish the records on
the site page. Release run and by-hand run (33816831619) agree cell for
cell and step for step; the counts are the 1.7.0 counts. E1 rerun on
the 1.7.2 image (`~/Projects/dispat-experiments/results/v172/`): golden
PASS, core 1000/1000 and 500/500, full 412 and 222 clean with the same
class counts, per-seed identical to 1.7.0 on all 3,000 instances. Paper
subject moved to 1.7.2 (counts as recounted for the paper: 319 tags,
849 commits, fourteenth stable CLI release, 2,869 test functions in 221
files, coverage 95.4% of 19,246 statements, unit 88.4%, CLI module
86.3%; the tools module is profiled for the first time at 81.3%, which
is what moved the totals). E3a on the 1.7.2 image: gcn 36/42 and cc rows byte-identical to the
v1.6.0 campaign. E4 on the 1.7.2 image, two repetitions on a loaded
host: 0.4 to 1.1 s at 100, 5 to 10 s at 1,000, 209 to 215 s at
10,000 packages (same shape; the paper's range stays the v1.4.0
five-repetition one); recovery 24/24 converged within 5 runs, first
plans up to 45, 4 checker flags of the usual log-matching kind.
Comparison note: `results/v172/compare-v170-v172.md`.

