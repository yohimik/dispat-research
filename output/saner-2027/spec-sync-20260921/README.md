# Existing-paper specification synchronization — 2026-09-21

This revision implements the user's clarification: update outdated mathematics and distributed-system material in the existing English conference paper. It preserves the paper's release-recovery focus. The abstract's brief LLVM forecast and the introduction are unchanged from the immediately preceding revision. The full technical report and experimental results are unchanged.

## Source and scope

`provenance.json` records CCME 3.1.0-rc.2, its repository revision and specification hash. `SPEC.md` is the reviewed snapshot. The adjacent product repository was inspected read-only.

- Existing formal model: distinguish propagation, publication-order and failure-blocking edges; retain full-graph ordering through unplanned intermediates; synchronize initial-version and exact-pin guards; make durable recording explicit in discharge and convergence. Relevant specification areas include §§8.6, 11.4, 13.7c and 19.2–19.3.
- Existing cost discussion: synchronize §13.11 marker ancestry indexing, word-operation and memory bounds, two-boundary fresh membership, per-unit admission/provenance, bounded caches and ordering/blocking costs. These are phase bounds, not a distributed speedup theorem.
- Existing fleet discussion: synchronize §27 repository-qualified consumer windows, baseline evidence, relevant input closure, source-owned durable records, conditional peer-link settlement and checkpoint recovery.
- Existing worker discussion: synchronize §28 orchestration, locks, immutable verified output transport, provider-output reuse, owner recording lanes and timeout fencing/reconciliation. Workers remain a specified, unevaluated extension.
- Existing discussion: preserve the conditional single-history proof scope and distinguish current shared-group contracts from proved or measured claims.

Prose was tightened to retain the required ten content pages and two reference pages. `changes.diff` records this revision relative to the saved `*-before.tex` files; earlier uncommitted changes are not attributed to this revision.

## Verification

`verification.json` records a successful 12-page build: ten content pages, two reference pages and 45 references, with embedded fonts and no detected overflow, unresolved citations or missing glyphs. All twelve rendered pages were visually inspected; pages 6 and 7 were inspected again after the final wording changes. `page-*.png` contains the inspected renders.

`math-sanity.json` records finite editorial checks of the marker ancestry index and equivalent fresh-window expressions, including incomparable boundaries. These checks are neither an implementation campaign nor a proof, and do not change any experimental count.

`scope-verification.json` verifies protected report/evaluation hashes, unchanged abstract/introduction, the unchanged specification snapshot and the delivered PDF hash. The delivered artifact is `../../pdf/saner-2027-paper.pdf`.
