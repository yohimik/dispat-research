# SANER paper adaptation — 20 September 2026

Local editorial record, not part of the anonymous manuscript or an upload package. Scope: English conference paper and its rendered PDF. No product changes, experiments, publication, or submission.

## Call and deadlines

Read the complete [Research Track call and preprint guidelines](https://conf.researchr.org/track/saner-2027/saner-2027-papers) on 20 September 2026.

| Milestone | AoE date | Dubai cutoff, assuming 23:59 AoE |
|---|---|---|
| Mandatory abstract | 21 September 2026 | 22 September, 15:59 |
| Full paper | 25 September 2026 | 26 September, 15:59 |
| Notification | 1 December 2026 | — |
| Registration and camera-ready | 8 January 2027 | — |

The call requires original, non-concurrently submitted English research; IEEE conference PDF format with a 24-point title, 10-point text, and a 10+2 reference-only page limit. It requires double anonymity, third-person self-citation, non-identifying names and links, and no identifying acknowledgments. Data Availability follows Conclusion; artifact sharing is optional. Review considers novelty, significance, soundness, verifiability, and presentation. AI-related research must address evolution/maintenance. Accepted papers require full registration and presentation; authors cannot change after acceptance, and title changes need chair approval. The anonymity period starts one month before submission: public versions must not be updated or promoted during it, or linked from the submission. IEEE post-publication preprint rules also apply.

The paper fits the explicitly listed release-engineering/CI/CD topic; AI themes do not require recasting this work as AI research. The call's AI-guidance link returned 404. Read the [IEEE policy](https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/) directly: substantive AI content belongs in an acknowledgments disclosure identifying systems, sections, and scope. The [ACM authorship policy](https://www.acm.org/publications/policies/new-acm-policy-on-authorship) was discoverable in official search results but direct retrieval returned 403; complete current ACM-policy compliance is not certified here.

Submission still requires the author's confirmation of public-version dates and promotion since 25 August, exclusive-submission status, author list, and AI provenance. Existing author-supplied Claude model labels remain in `EDITING-REQUIREMENTS.md`; the manuscript uses system-family names. The call currently contains inconsistent EasyChair conference IDs, so use its live Research Track entry and verify the destination before any later submission.

## Direct CCME review and fleet focus

The governing review input after the author's clarification is the actual working file `../dispat/specs/ccme-spec/SPEC.md`, including uncommitted changes, not merely release notes. The inspected snapshot is retained locally at `tmp/ccme-review-20260920/SPEC.md` with SHA-256 `6381cae09e8ddcda32947347daed9827d89cf53f6bea7abd5c0ef0ad1360930f`. At capture, product HEAD was `784a4971dfc3936be824469b6a7156383ebb7534`, and the specification had 170 added and 69 removed working-tree lines. Its stamped version alone does not identify those changes.

The manuscript's focus is fleet releases and polyrepos, particularly §27 and §27.11:

- Three modes: single history, specified histories under entry configuration, and discovered peer histories. A star topology does not establish central policy ownership.
- Packages publish and record in their source repositories; central orchestration is not a publishing wrapper or a mandatory publication location.
- Commit identities and ancestry remain repository-local. A consumer's boundary in a provider history needs an exact checkpoint association, recorded link route, or explicit tuple. No timestamps or synthetic global DAG invent an ordering between independent histories.
- Peer-link settlement occurs before publication. Its exact native heads must be admitted by revalidation, rather than rejected as unexpected changes.
- Source records precede control checkpoints. A failed checkpoint preserves source success and requires explicit repair; it must not trigger source republication or pretend that a fleet release is atomic.

These details now form a dedicated system subsection and inform the abstract and conclusion. The single-history proofs and saved measurements remain bounded to their actual scope. Shared-version groups are only a brief proof exclusion: a shared counter can advance on retry and reselect successful members. The channel-only graduation clarification is reflected in the model exposition and train table. Detailed group policies and new performance optimizations are not the paper's focus.

## Candidate cross-check

Read the product repository without changing or running it. Latest local release tag inspected: `v1.11.0-rc.3`, also `services/dispat/v1.11.0-rc.3`, resolving to `eafb7599779a9cfff32424d6b65030c73eb2266a`.

Relevant tagged sources: `services/dispat/CHANGELOG.md`, `packages/docs/docs/control-repository.md`, `packages/docs/docs/choreographed-repositories.md`, `services/dispat/internal/plan/plan.go`, and `services/dispat/internal/app/release.go`.

The candidate corroborates the implemented fleet direction; the newer local specification supplies the clarified semantic account above. Maintenance changes to HTTP cancellation, build gates, dependency reconciliation, and announcements do not create new paper evidence.

Local HEAD at inspection was `784a4971dfc3936be824469b6a7156383ebb7534`, with later shared-version counter/channel work and uncommitted product changes. Those are not relabeled as the tagged candidate. No current product test counts or performance claims were imported.

## Campaign labels and exact provenance

Product release numbers are removed from manuscript prose; numerical SemVer examples and external standards identifiers remain where needed. Labels do not merge datasets or move evidence to the candidate.

| Manuscript label | Existing pinned evidence |
|---|---|
| Mechanism campaign | `experiments/saner-2027/campaign-mechanisms-20260910/RESULTS.md`, released CLI 1.10.0; 140 episodes and finite projection |
| Companion campaign | `experiments/saner-2027/campaign-1.10.0-20260909/runs/run-v1.10.0-linux-arm64-20260909`; 300 core histories, 20 recovery episodes, 60 registry executions, three CI repetitions |
| Earlier protocol-validation attempt/rerun | Separate original and corrected 1.9.0 runs in `campaign-next-release-prepared`, detailed in `evidence/EXPERIMENTS-1.9.0-20260909.md` |
| Historical campaign | Saved 1.8.2 evidence, including full-profile diagnostics, vectors, recovery, comparisons, replay, and scale; original records remain unchanged |

The mechanism and companion campaigns use binary SHA-256 `03d1ba5fbaef35b69582e9489f40b5438f81ae6926e02ea6d02716b5b73d92fd`. Their protocols, environments, and counting units remain separate. Exact image and protocol hashes remain in the original records. Historical comparisons retain Lerna 10.0.1, Nx 23.1.2, and Changesets 3.0.1 pins. The pseudonymous language reference distinguishes the evaluated 2.0.0 snapshot from the locally reviewed development snapshot above; it does not transfer evaluation claims between them.

## Verification

Build and structural validation: `tectonic -X compile main.tex --outdir build --keep-logs` and `python3 check.py`. The checker reports 12 pages: ten content and two references-only pages, 45 cited references, embedded fonts, no identifying author metadata, no known identifying names, no overflow, and resolved citations. All twelve final pages were rendered at 1600 pixels and visually inspected, including the fleet text, stage diagram, equations, tables, final content page, and both reference pages. No clipping, overlap, or illegible layout was observed. Ordinary underfull typesetting warnings remain. This does not certify anonymity eligibility or scientific validity.

Delivered PDF: `../../output/pdf/saner-2027-paper.pdf`, SHA-256 `1e0764a0f8c6054d6595cd3fb082991421dd9bced3c29b03a90f4cf54c7ff3e7`. Exact source hashes remain in `build/verification.json`; no measurements were rerun or rewritten.

## DORA reference follow-up

Added the 2025 State of AI-assisted Software Development report as contextual motivation in Related Work. Its finding is higher AI adoption associated with both higher delivery throughput and higher delivery instability, not merely more software. The association is confirmed in DORA’s own [researcher summary](https://dora.dev/insights/balancing-ai-tensions/); bibliographic authors, title, and year were checked against [Google Research](https://research.google/pubs/dora-2025-state-of-ai-assisted-software-development-report/). This is distinct from the earlier Impact of Generative AI report based on prior research, which reported lower throughput. The paper does not treat the association as causal evidence, attribute it to fleet-release failures, or present it as validation of this protocol. Rebuilt with 45 references and unchanged 10+2 pagination; only pages 10 and 12 changed in extracted text, and both were rendered and visually rechecked.


## Outreach coverage follow-up

Added an exploratory-context paragraph to Discussion from eight retained September outreach inventories in the read-only product repository. Their 240 memberships deduplicate to **211 distinct repositories**, a conservative lower bound with unequal review depth, not a defect count. The 21-ecosystem pass and separate 1,512-repository discovery pool retain their distinct denominators. Coverage includes RelayCast at 9 GitHub stars and Paperclip at 80,381 in pinned snapshots; stars describe visibility, not code size.

Three examples distinguish a RelayCast simulated post-upload recording failure, two observed Astro histories whose green retries skipped unfinished marketplace destinations, and an Apache Arrow stubbed-client reproduction selecting a stale workflow invocation. Later quality-review exclusions override older outreach claims, including the discarded Netty example. No current defect, adoption, or field validation of this protocol is inferred. Exact source hashes, the full deduplicated inventory, evidence limits, and authoritative dispositions are retained in `evidence/OUTREACH-20260920.json` and explained in `evidence/OUTREACH-20260920.md`.

Repeated introductory and discussion prose was shortened to preserve ten content pages without reducing fonts or altering results. The rebuilt document has 45 references and passes `check.py`; changed pages 1–10 were rendered and visually inspected, with no clipping, overlap, or illegible layout. Source repositories and experimental observations remain unchanged.
