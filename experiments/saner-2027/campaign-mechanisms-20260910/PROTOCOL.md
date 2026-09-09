# Controlled recovery mechanisms

This prospective protocol extends, rather than replaces, the frozen 9 September campaign. It is designed after examining that campaign and SANER exemplars; it is not an independently preregistered study. Freeze the scripts, this protocol and the runtime lock before the first measured execution. Retain pilot runs and failed attempts separately.

## Questions and design

RQ1: Does consumer-based admission retain the original remaining obligations after partial completion, and can a source-window alternative lose them? Compare each observed initial obligation set minus newly completed tags with the binary's retry plan. Separately evaluate a counterfactual that discards a unit when its originating package completes. This is a mechanism ablation in the analysis model, not a modified product binary or a competitor comparison.

RQ2: Are versions and completed records stable under repeated failure and repair? Construct five four-package topologies: chain, diamond, fan-out, two disconnected pairs, and a chain with shortcuts. Cross stable and beta baselines with each of four failure locations and three injection boundaries (before build completion, before publication, and after a local artifact is durably written but before the publisher returns success). This gives 120 fault episodes, plus ten no-fault topology/baseline controls. Run every case; use deterministic randomized order, seed 20260910. Each fault episode executes the same fault twice, then repairs it and executes a final no-op release. These are generated cases, not independent production samples or repeated random trials.

RQ3: Does the integration's identity check reject a conflicting artifact after an uncertain publication? Add ten cases, one per topology/baseline with the last package failing after writing. Substitute conflicting content before repair; require refusal without a new completion tag, restore the original content and retry. These test the supplied local publisher's reconciliation contract, not arbitrary npm/OCI publishers.

All packages have a stable 1.0.0 baseline; beta cases additionally have a 1.0.1-beta.0 baseline. A feature intent propagates patch intent transitively from a; disconnected cases include another feature intent from c. Channel inputs remain unchanged across retries. The local publication adapter uses immutable version/content identity, records writes separately from invocations, and may safely accept the same content. Build and publish concurrency are each one to isolate failure boundaries. Scheduling concurrency is already covered by the separate real-registry campaign.

## Finite model exploration

Enumerate all 64 DAGs respecting a fixed order of four named vertices, each of four single intent sources, all completion sets reachable by repeatedly recording an enabled package, and all subsets of remaining packages designated as failed in the abstract run. Check exact residual obligations, no widening, no double ledger delivery and strict decrease only when progress occurs. Apply the source-window mutant to the same states and retain counterexamples. This is an executable stable-channel, one-intent projection, not a mechanized proof of the complete language, arbitrary graphs or implementation refinement. Enumerated states and transitions are not independent statistical samples.

## Runtime and observations

Use the exact 1.10.0 runner and binary in the adjacent release lock, Linux ARM64, Docker with two CPUs, 4 GiB RAM and network disabled. Git origins and publisher destinations are local fixtures. Capture Docker image inspection, Python/Git/platform/binary identities, script hashes, every command stdout/stderr and return code, initial and retry plans, tags, stage events, local artifact identities and the complete fixture Git history. Do not mount the product checkout or contact external registries. Reproduction must create a new output directory and refuse overwrite.

## Analysis and stopping

Report denominators for episodes, configurations, faults, counterfactual failures, model states and transitions separately. No p-values or population reliability confidence intervals are appropriate for this deterministic designed matrix. Any unexpected plan, version, tag, duplicate write, acceptance of foreign content, or nonempty repaired plan is a failed observation. Continue the other cases, retain every failure, and distinguish a harness defect from a runtime defect before correcting either in a new run. Do not silently exclude cases or retune the matrix to improve outcomes.
