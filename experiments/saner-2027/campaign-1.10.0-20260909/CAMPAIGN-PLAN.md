# Dispat 1.10.0 campaign, frozen 9 September 2026

This is a new execution of the corrected 1.9.0 protocol. All protocol files, the driver, Dockerfile, and Alpine package lock are copied byte-for-byte. The new release lock selects the official 1.10.0 Linux ARM64 binary; measurements are separate from every prior run. The feature adds standalone diagnostics; parser 2.0.0 and the scientific hypotheses are unchanged.

Execute all 14 stages, including the four-node extension: parser/golden gates, 300 core histories (seeds 90001–90300), 20 recovery episodes (20/100 packages, failure probabilities .1/.3, seeds 100–104), five configurations × six repetitions separately for each mixed topology, and three CI repetitions. Retain all intentional failures, invalid executions, refusals and divergent rows. Predicate counts are repeated checks, not independent samples. Preserve failed attempts without overwriting or selectively retrying observations.

Use two CPUs and 4 GiB per main container, offline core/recovery/CI and private registry networks for mixed chains. The Docker socket uses this host's Docker Desktop daemon. No other campaign may run concurrently. The protocol's artificial delays test availability, not throughput. This is not native Windows evidence.

From this directory, preview `python3 execute.py --release-lock release-lock.json --run-id run-v1.10.0-linux-arm64-20260909 --with-4node-extension`; then add `--execute`. A COMPLETE marker requires all stages. Archive a finished attempt with `python3 tools/archive-campaign.py experiments/saner-2027/campaign-1.10.0-20260909/runs/RUN_ID` from the repository root. Verify archives in a separate extraction and rerun the retained-data verifiers offline.

Prior source: `../campaign-next-release-prepared`, corrected campaign `run-v1.9.0-linux-arm64-20260909-corrected`. Its first failed strict-overlap oracle and corrected rerun remain immutable. Base build completing before UI publication starts remains an admissible schedule. No new oracle changes are made here.
