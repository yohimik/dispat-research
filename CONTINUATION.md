# Research continuation, 10 September 2026 — 1.10.0 update and cleanup

Ownership confirmed by the user: this task owns only `/Users/yohimik/Projects/dispat-research`. The Dispat product task (`01a06e7b-e8ba-7722-ad9c-c6da024126a8`) owns `/Users/yohimik/Projects/dispat`. Product-source inspection may support research, but product changes, CI operations, commits and releases belong to that agent. Send runtime defects and requested product changes to it.

The canonical English SANER manuscript now reports the completed released-dispat 1.10.0 campaign. The campaign survived the app restart and finished without a replacement run; all 14 stages passed from 17:02:20 to 17:11:00 UTC. No campaign is pending. The restart files record a historical checkpoint, not current running work.

Read `AGENTS.md`, `paper/saner/SOURCE.md`, `paper/saner/EDITING-REQUIREMENTS.md`, and `paper/saner/evidence/EXPERIMENTS-1.10.0-20260909.md`. The product coordinator's complete context is in `provenance/handoffs/2026-09-09/HANDOFF-2026-09-09.md`; product task `01a06e7b-e8ba-7722-ad9c-c6da024126a8` supplied and confirmed release provenance. This research task remains `01a08719-8f24-7201-a5fb-417d1ac98823`.

## Verified current evidence

Campaign: `experiments/saner-2027/campaign-1.10.0-20260909/runs/run-v1.10.0-linux-arm64-20260909`.

- 300 core histories: all accepted and matched; zero refusals, invalid cases or differences.
- 20 recovery episodes: all converged, progress every run, maximum four runs; 251 raw command records; distribution 9×2, 5×3, 6×4 runs.
- Each topology separately: 30 initial executions, 12 initial successes, 18 designed failures, 12 successful repairs and 24 unchanged no-op reruns. Three-node verifier: 522 checks; four-node: 798.
- Three CI repetitions, 81 repeated checks. Sixteen standalone diagnostics engineering cases passed separately.
- Exact binary SHA-256: `03d1ba5fbaef35b69582e9489f40b5438f81ae6926e02ea6d02716b5b73d92fd`; runner: `sha256:6f92932fbba5d33d61d777073f5fc155133063f4c3d4b2f950e3e5b9ed9a263e`.
- Archive SHA-256: `835208a0cd9066ec6bf7ec424a4d9cdee06ca4482a061f7a7d7cc02738611793`; 9,157 regular files byte-verified, then all four verifiers passed offline from a fresh extraction.

One episode (n=100,p=.3,seed100) needed an extra attempt versus 1.9.0; the retained trace comparison explains the additional release/tag/status triplet. Initial versions and first failure set match, but pending sets and subsequent seeded failure draws differ. No causal claim about diagnostics is supported. Do not normalize the 251 records to historical 248.

## Paper and delivery

Final PDF: `output/pdf/saner-2027-paper.pdf`, SHA-256 `b695e2d5b28adc1c65e4ac6d404226fae67cad1e00dfbdd956bae12105ebbf60`. Exactly ten content pages plus two references, 40 references; structural checks pass and all twelve rendered pages were visually inspected. Layout review is recorded in `paper/saner/evidence/PDF-1.10.0-20260909.json`. The source/model/guarantee files retain the existing scientific boundaries; the system includes bounded standalone-diagnostics support. The conclusion and Data Availability were shortened to maintain normal 10+2 layout.

The narrative remains system/benefits → model/guarantees → experiments, with npm assets → npm UI → Docker base → Docker app. Reuse of the frozen cases is explicit. The original 1.9.0 strict-overlap failure remains historical, and 1.8.2 full-profile, scaling and competitor measurements remain historical. No new Windows equivalence, throughput, or independent replication claim is made.

## Scope and remaining author decisions

The requested rerun and manuscript update are complete. The user will personally edit/review the paper before submission. Public/preprint anonymity history and exact author-provided AI model names still require confirmation. Full English technical report, Russian translation, patent/lawyer documents and publication actions remain outside this update. Nothing was submitted or made public. The user subsequently authorized committing and pushing the research update and repository cleanup to the private research repository. Check Git for publication status. IDE settings remain local and ignored; generated scratch previews were removed. The obsolete ICSE tree is archived under `paper/archives/`; completed handoffs are under `provenance/handoffs/2026-09-09/`. Final PDFs and verification records remain, and all three expanded campaign trees were removed only after byte-for-byte archive verification. See `RESTORATION.md` and `provenance/cleanup-2026-09-10.json` for restoration and the cleanup inventory.

Use the product task for future release identities or runtime defects. The later README-only CI dependency-download failure is separate from the successful 1.10.0 release; the product coordinator owns its retry. Do not change this campaign's frozen baseline for that unrelated CI result.
