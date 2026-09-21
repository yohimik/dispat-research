# Distributed execution abstract update - 21 September 2026

Scope: abstract and CCME specification design. The author requests no code
changes and defers report expansion until after the abstract and implementation.
The research agent owns this repository; canonical product specification edits
are routed to the existing product task, **Finalize Dispat production release**,
under the repository ownership rule. That handoff explicitly authorizes only
specification documentation, not implementation, tests, commits or release.

## Manuscript change

Only the abstract in `main.tex` changes in this turn. It leads with distributed
task/release execution and transfer of dependency outputs, not repository-link
topology. It covers the default orchestrator role, workers barred from initiating
releases, the CI-entry node's repository locks and task allocation, concurrency,
temporary Git branches and remote JS output reuse. It distinguishes the proposed
execution profile from evaluated single-history recovery. The 120/84/70% result
is retained; no new experimental outcome or speedup is asserted.

The paper body, title, proofs, result tables, references and full technical
report remain unchanged from the start of this turn. Earlier uncommitted edits
are preserved. A proposed body paragraph was removed during layout iteration;
`system.tex` matches its saved pre-edit snapshot byte for byte. The abstract is
194 whitespace-delimited words; the plain text is saved for copying at
`../../output/saner-2027/distributed-execution-20260921/abstract.txt`.

## Specification design

The review input and proposed normative text are in
`../../provenance/CCME-DISTRIBUTED-EXECUTION-20260921.md`. The principal requirement
is actual reuse of remote provider outputs for local JS dependencies: branch
synchronization must carry ignored/generated output bytes or verified immutable
bundle references with retrievable bytes. Source-only dispatch, repeated provider
closure compilation and mandatory placement of the entire connected graph on
one worker do not meet it. A parallel large-JS fixture must demonstrate a
wall-time benefit before an implementation performance claim is made; serial
critical paths and transfer overhead remain real constraints.

Other requirements preserve pure semantic planning, source-owned release tags,
whole-run concurrency limits, per-owner publication serialization, explicit
transport-commit exclusion from release ancestry, and safe handling of timed-out
publishers. The draft's conformance vectors are proposed cases, not executed
tests. Broader report revision and measured distributed results await a pinned
implementation and a new campaign.

## Verification and retained evidence

`tectonic -X compile main.tex --outdir build --keep-logs` and `python3 check.py`
pass: exactly ten content pages and two references-only pages, 45 cited
references, embedded fonts, resolved references, no overflow and no known
identifying names or author metadata. Ordinary underfull warnings remain.
Only pages 1 and 2 differ in extracted text from the pre-edit delivered PDF;
both were rendered at 1600 pixels and visually inspected. No clipping, overlap
or unreadable content was observed. Pages 3-12 retain their extracted text.

The delivered PDF is `../../output/pdf/saner-2027-paper.pdf`, SHA-256
`8ae2e684513a4f1052c62617c70b155a51a68257825fdb2ec775c6090f4deece`.
The saved before-PDF, source snapshots, reviewed specification snapshot, changed
page list, rendered pages and final verification manifest are in
`../../output/saner-2027/distributed-execution-20260921/`. Failed layout iterations
were build attempts, not experiments; no raw experimental observation changed.
Structural and visual checks do not certify scientific claims or submission
eligibility. Nothing was submitted, published or released.

## Canonical specification integration completed

The product owner integrated §28 and its cross-references into
`/Users/yohimik/Projects/dispat/specs/ccme-spec/SPEC.md`, with companion boundary
and history updates in that directory's `README.md` and `DESIGN-HISTORY.md`.
The final specification has nine profile subsections and 26 consecutively
numbered, unexecuted conformance cases. It retains version `3.1.0-rc.1`; no
version was released. The product owner reports a passing specification verifier
and scoped whitespace/link/structure checks, with no implementation, test or CI
changes for this handoff.

Independent read-only review checked the new profile, integration points and
abstract alignment. Owner-pronoun ambiguity and duplicate vector numbering
were corrected by the product owner before final capture. Final spec SHA-256:
`63210d4eadaf27c5cb610ae822aeeb13c692b5423a48ff95a914ee6e2c4a0875`.
The captured specification and exact companion hashes are retained in
`../../output/saner-2027/distributed-execution-20260921/SPEC-after.md` and
`spec-integration.json` in the same directory. These are design/static-review
records, not runtime or performance evidence.

## Agent-guide and DORA follow-up

At the author's request, the abstract and the existing DORA paragraph now
describe the accompanying agent guide: coding agents inspect deterministic
plans, retain tests, invoke CI releases, and reconcile partial outcomes through
the implemented engine. The mathematical guarantees remain conditional
properties of the release model; no proof of the complete implementation or
measured agent effectiveness is claimed. The distributed execution profile
remains unimplemented and unmeasured. This follow-up changes only `main.tex`
and the existing related-work paragraph in `discussion.tex`; adjacent wording
was compressed to preserve pagination. The full technical report, results,
proofs and bibliography are unchanged. This is not a request to publish the
agent-guide package.

The guide was inspected read-only and snapshotted. The DORA association was
rechecked against its [researcher summary](https://dora.dev/insights/balancing-ai-tensions/):
higher AI adoption is associated with higher delivery throughput and instability.
It motivates the design; it is not evidence validating this engine or its agents.

The abstract is now 180 whitespace-delimited words. The rebuilt PDF passes
the 10+2-page and 45-reference checks. Changed pages 1, 2, 3 and 10 were rendered
and visually inspected with no clipping or overlap. The delivered PDF SHA-256
is `944e858c28faf0cc847c49a30e89563028853728e3d81cf8034cdd0cf5a2677d`.
Before snapshots, guide provenance, copyable abstract, page renders and final
verification are in `../../output/saner-2027/agent-guide-20260921/`.

The live [Research Track call](https://conf.researchr.org/track/saner-2027/saner-2027-papers)
and [official dates page](https://conf.researchr.org/dates/saner-2027) were
rechecked on 21 September: mandatory abstract 21 September 2026 AoE, full
paper 25 September AoE; no extension is listed. With the end-of-day AoE cutoff,
these convert to 22 September 15:59 and 26 September 15:59 respectively in
Dubai (UTC+4). No submission was performed.
