# SANER 2027 English working manuscript

This directory is the active English conference revision. The withdrawn ICSA submission and earlier ACM-format source remain archival; the full technical report is `../main.tex`. Edit this directory for SANER, not those older versions.

The verified 10 September 2026 build has exactly **10 content pages + 2 references-only pages**, in IEEE conference format. English is canonical. Nothing has been submitted; translations and patent documents have not been synchronized to this venue revision.

## Files in reading order

- `main.tex`: format, title, abstract, and input order.
- `introduction.tex`: problem, original mixed chain, contribution positioning.
- `system.tex`: workflow, integration contract, stage graph, and CI benefit.
- `model.tex`: normalized inputs, admission, versions, and run transition.
- `guarantees.tex`: conditional guarantees, proofs, and recorded-state idempotence.
- `evaluation.tex`, `mixed-results.tex`: fresh 1.10.0 campaign and separately identified saved evidence.
- `discussion.tex`: limitations, related work, conclusion, data availability, AI disclosure.
- `references.tex`: bibliography in citation order.

The unused historical comparison fragment is archived at `../archives/saner-comparison-2026-09-10.tex` and is not included in the build. Do not treat its claims as part of the active paper. The obsolete `paper/icse/` tree is preserved in the verified archive described in `../archives/README.md`.

## Build and inspect

Requires Tectonic, Python 3, and Poppler (`pdfinfo`, `pdftotext`, `pdffonts`, `pdftoppm`). From this directory:

```sh
mkdir -p build
tectonic -X compile main.tex --outdir build --keep-logs
python3 check.py
pdftoppm -scale-to 1600 -png build/main.pdf build/page
```

Inspect every rendered page. `check.py` checks pagination, citations, known identifying strings, font embedding, and build warnings; it does not prove claims or certify submission eligibility. It writes `build/verification.json` with source/PDF hashes. Ordinary underfull typesetting warnings may remain; the final rendered pages have been visually reviewed.

The 24-point title and 10-point body are TeX points (approximately 23.91 and 9.96 PDF points). Font encoding is selected before IEEEtran initialization to avoid XeTeX font substitution. The IEEE bibliography break balances the two references-only pages. The checker derives the expected final number from the bibliography and verifies that every numbered entry appears on those pages.

Read **EDITING-REQUIREMENTS.md** before revising the claims. The prospective
mechanism campaign is documented in
`../../experiments/saner-2027/campaign-mechanisms-20260910/RESULTS.md`; the
earlier 1.10.0 real-registry and broad campaign remains identified in
`evidence/EXPERIMENTS-1.10.0-20260909.md`. Saved 1.8.2 results remain separate.
All implementation campaigns use the implemented 2.0 semantics; future
specification features are not evaluated results.

Local evidence and review reports are in `../../output/saner-2027/`. The delivered PDF is `../../output/pdf/saner-2027-paper.pdf`; rebuild it after edits before distributing a newer copy.
