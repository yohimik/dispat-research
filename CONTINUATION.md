# Research continuation, 9 September 2026

The research workspace has moved to this private repository. Originals in the Dispat working tree and the sibling `dispat-experiments` directory were retained as a safety copy. Make future research edits here to avoid divergent copies.

Dispat 1.9.0 was released successfully with docs, four Docker images, models and the agent guide. CCME specification 3.0.2 was also released; the parser remains unchanged at 2.0.0. The user declined a follow-up change to diagnostics when Git exits before its commit-message hook. Do not resume that change.

The canonical English SANER paper now incorporates the completed, immutable Dispat 1.9.0 Docker campaign: 300 core cases, 20 recovery cases, 30 executions for each of two mixed-package topologies, and three CI integration repetitions. The corrected campaign passed all 14 stages. Preserve the first failed oracle attempt and its raw evidence; its overly restrictive overlap assertion was corrected before a complete fresh rerun. Historical 1.8.2 measurements remain explicitly separate.

The final PDF has ten content pages and two reference pages, with 40 references. All twelve rendered pages were inspected. Its SHA-256 is `62176e33ac6df95d528fd8af457e1ff80d739dac28e24783a38bde34122631c3`; `output/pdf/saner-2027-paper.pdf` is the delivery copy. The system and evaluation include a bounded self-hosting case study, without treating author-reported AI use or later code counts as causal productivity evidence.

Preserve the requested narrative: system and benefits, then mathematics, then experiments. Explain the original npm → Docker → Docker chain: a consumer may build from local npm output before npm publication, whereas a downstream image that pulls its base must wait for that image's registry publication. CI/configuration reuse and cross-platform scripts are bounded integration capabilities; the Linux fixture does not prove native Windows behavior.

The user has excluded Russian work. Keep this repository English-only. Patent work remains outside this repository. Do not submit to SANER yet. The user will personally revise the manuscript before submission.

See `paper/saner/EDITING-REQUIREMENTS.md` for the user's next editing pass and scientific, formatting, authorship-disclosure and submission checks. `paper/saner/evidence/` records the release, experiments and self-hosting case. `experiments/saner-2027/campaign-next-release-prepared/ARCHIVES.md` explains how to restore the verified complete raw work archives, including fixture Git repositories. Local expanded work trees remain available but are intentionally ignored by Git to avoid nested repository links. No experiment rerun or manuscript edit remains pending for this update.
