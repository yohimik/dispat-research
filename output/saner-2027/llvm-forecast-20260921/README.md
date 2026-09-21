# Abstract-only LLVM forecast update — 21 September 2026

Final scope: only the abstract in paper/saner/main.tex, plus its rebuilt paper PDF.
All interim report and body-source edits were reverted at the author’s request.
The technical report source and delivered PDF are unchanged from the turn start.
Existing uncommitted work predating this turn was preserved.

Reviewed CCME 3.1.0-rc.2 and the adjacent LLVM fork read-only. Exact heads,
working-file hashes and source copies are in source-manifest.json and sources/.
The fork has no real LLVM build result. The abstract's 6–10-machine neutral
forecast is conditional on graph expansion, sharding and five-minute hops.

The public upstream run 34549173201 supplies the rounded 154-minute Linux
build-job baseline (154.10 minutes, of which 95.52 build and 56.35 tests).
Run: https://github.com/llvm/llvm-project/actions/runs/34549173201
API: https://api.github.com/repos/llvm/llvm-project/actions/runs/34549173201/jobs?per_page=100
Raw API responses and the pinned workflow are retained here. This corrects the
supplied approximate 153 minutes; the 103-minute forecast still rounds to a
33% reduction. Forecasts are not added to experimental sample counts.

The retained timing-summary.json records an illustrative sensitivity budget,
not an executed build or a validated LLVM task model. Seven upstream runs
include different platform matrices and are not repetitions of a single fixture.

Final structural checks pass: 10 content pages + 2 references-only pages,
45 references, no overflow or unresolved citations. Pages 1–3 changed from
the before PDF and were visually reviewed; the paper body sources are unchanged.
The copyable abstract is abstract.txt. Nothing was submitted or published.
