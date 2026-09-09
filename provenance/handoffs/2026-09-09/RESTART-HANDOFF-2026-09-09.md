> **Resolved after restart:** The original process survived and completed all 14 stages. The 1.10.0 evidence and final 10+2 PDF are verified. Read CONTINUATION.md for current state; the record below preserves the earlier checkpoint.

# Restart handoff, 9 September 2026 — active 1.10.0 research campaign

The user asked “get ready for update restart” during the experiment run. Work is saved; the experiment has been left running. No process was killed, no duplicate was launched, and no final 1.10.0 paper was delivered. Process survival across the app restart is unverified: inspect it before proceeding.

## Task and instructions

- Workspace: `/Users/yohimik/Projects/dispat-research`.
- Research task: `01a08719-8f24-7201-a5fb-417d1ac98823`.
- Product task: `01a06e7b-e8ba-7722-ad9c-c6da024126a8`, “Review and harden Dispat”. User explicitly authorized ping/coordination; it has supplied its complete `HANDOFF-2026-09-09.md` in this repository.
- Original objective remains: rerun experiments on latest released dispat and update canonical English SANER paper plus research report. Read AGENTS.md, HANDOFF-2026-09-09.md, paper/saner/EDITING-REQUIREMENTS.md and this file.
- English conference paper only; separate technical report is unchanged. No Russian/patent/lawyer work, submission, publishing, privacy change, or product release. Preserve historical measurements and failed attempts.
- User did not request new agents. No subagents spawned. Product coordinator is not running a competing campaign.

## Active execution — check this FIRST after restart

Campaign: `experiments/saner-2027/campaign-1.10.0-20260909`.
Run: `runs/run-v1.10.0-linux-arm64-20260909` beneath it.
Driver started `2026-09-09T17:02:20.892329+00:00`.
Host PID at snapshot: **14409** (check full command against PID reuse).
Old exec session: **19419**; it may be unavailable after app restart.
Driver stdout/stderr: campaign `campaign.log`; each stage has its own log under the run.
Full captured state: `RESTART-STATE-2026-09-09.json`.

Read `provenance.json`, `COMPLETE`, process state and Docker containers. At snapshot eight stages had passed (identity, toolchain, parser/golden, 300-case core and verifier, recovery), and three-node mixed was running with about 25/30 rows. Four-node, CI and final verifiers follow automatically. Never run the campaign again while the driver/container is active. It has fixed names `saner-next-release-mixed` and `saner-next-release-mixed-4node`.

Useful read-only checks from the repository root:

```sh
ps -p 14409 -o pid,ppid,lstart,command
docker ps --format '{{.Names}} {{.Image}} {{.Status}}'
python3 -m json.tool experiments/saner-2027/campaign-1.10.0-20260909/runs/run-v1.10.0-linux-arm64-20260909/provenance.json
tail -n 8 experiments/saner-2027/campaign-1.10.0-20260909/campaign.log
```

If it completes, require all 14 PASS stages plus COMPLETE. If it was interrupted, preserve every partial observation and log, record the restart interruption separately, and do not manufacture COMPLETE or rewrite raw outcomes. The driver has no resume switch and refuses existing destinations. Assess any still-running child container before cleanup; never start overlapping campaigns. If a full replacement run is necessary, use a new unique run ID with the same frozen protocol and lock and retain the partial attempt. A stale RUNNING provenance without a live driver is not completion.

## Frozen identities and scope

- Official version: `dispat 1.10.0 (linux_arm64)`.
- Binary SHA-256: `03d1ba5fbaef35b69582e9489f40b5438f81ae6926e02ea6d02716b5b73d92fd`.
- ARM64 image: `yohimik/dispat-alpine@sha256:f2a49c21eca0a3e30af1396eca538920b2faa475b50f12d4aae99236e2fe2955`.
- Index: `sha256:c7c03077f20d5763316d75ed22ba9ece0ec2908167a69747e56c35e5855e1af8`.
- Runner ID: `sha256:6f92932fbba5d33d61d777073f5fc155133063f4c3d4b2f950e3e5b9ed9a263e`.
- Release run 34373760312; source `1bb3b397e4749461c1102869a56b1ceb600636ae`; CLI release `7a96ae956de4d1682c61e6b73e50c06401e031f7`; final images/docs `66cffcdae1fa8910ce3672f840ec5d0ea1fd1679`.
- CCME parser remains 2.0.0, spec remains 3.0.2. Feature is standalone diagnostics, not a new release theorem or protocol change.

The driver, protocol, Dockerfile and complete apk.lock are byte-identical copies of the corrected 1.9.0 campaign. `FREEZE.json` and `protocol-sha256.json` retain the pre-execution hashes; `identity-measurements.json` preserves image inspections and measured binary/toolchain. No protocol modifications were made. The old campaign lock, raw runs, and archives are unchanged. Only its CAMPAIGN-PLAN.md heading was clarified from “not executed” to completed historical status.

Execute 300 core seeds 90001–90300, 20 recovery episodes, 30 executions per three-/four-node topology, 3 CI repetitions, all 14 stages. Preserve negative controls. Predicate counts are not independent samples. Containers are capped at 2 CPUs/4 GiB; mixed experiments use private registries and Docker Desktop. No native Windows or throughput claim.

## Already measured (final verification still pending)

- Core verifier: 300 accepted matches; zero semantic refusals, invalid executions, differences.
- Recovery generation: all 20 converged, progress every run, max four runs. Distribution **9 in two runs, 5 in three, 6 in four**, **251 raw command records**. This differs from 1.9.0 (9/6/5 and 248). Preserve it; do not attribute the difference to diagnostics without trace evidence. Dedicated recovery verification runs at the campaign end.
- Mixed outcomes so far are expected; do not assume final 30/30 or passing verifiers until recorded.
- Separate diagnostics addendum: `diagnostics/run.py`, `FREEZE.json`, `provenance.json`, `execution.log`, and `results/{observations,verification}.json`. **16/16 engineering cases passed**. No Git repository or Git on PATH; network disabled, fixture unchanged. Covers valid/invalid/empty/multiline literal strings, no Git cleanup, explicit parser references, quiet JSON warnings, nearby malformed config ignored, explicit bad config and usage errors. These are purpose-selected checks, not part of scientific sample counts or a proof of all absent internal operations. They can support the new brief system paragraph.

## Paper edits made, not final

- `paper/saner/system.tex`: added three lines explaining standalone diagnostics and its boundaries (syntax/policy, not scope existence/plan correctness).
- `paper/saner/discussion.tex`: shortened Data Availability to accurately distinguish full local work archives from older curated subset; shortened the conclusion to retain 10+2 after the new paragraph. Formal model/guarantees unchanged.
- Current build passes `python3 check.py`: **10 content + 2 references, 40 references**; hash `ac04e582d9b4e1598fa433abcf7bf238043c43b2b5aedff938623d7c52ad3e33`.
- This is an INTERMEDIATE build: empirical version labels are still 1.9.0 and recovery still 248; do not deliver or call the paper updated for 1.10.0 yet. Final visual inspection is not done.
- Delivery `output/pdf/saner-2027-paper.pdf` is untouched and remains the prior verified 1.9.0 PDF hash `62176e33ac6df95d528fd8af457e1ff80d739dac28e24783a38bde34122631c3`.
- `paper/saner/build/build-1.10.0.log` is ignored scratch output; main.log/main.pdf/verification.json are tracked and changed by intermediate compilation.

PDF skill was read and announced. Its operation marker was successfully run EXACTLY ONCE for edit/pdf before authoring; do not run it again after restart. Skill path `/Users/yohimik/.codex/plugins/cache/openai-primary-runtime/pdf/26.905.11957/skills/pdf/SKILL.md`. Final PDF skill requires a plain output file citation; no final PDF exists yet for this task. Tectonic/Poppler are at /opt/homebrew/bin. Bundled Python (PIL, etc): `/Users/yohimik/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`. Node equivalent under dependencies/node/bin/node.

## New reusable tools

- `tools/archive-campaign.py RUN`: archives a finished COMPLETE or FAILED run, including hidden Git metadata and raw outcomes; verifies all regular/hardlinked files byte-for-byte; refuses overwrite. Does not change raw work. Tested on temporary failed-run fixture with hidden metadata, hardlinks, symlink and overwrite refusal. For stale interrupted RUNNING records, preserve status evidence and assess separately; do not falsify provenance merely to satisfy this utility.
- `tools/summarize-saner-campaign.py RUN`: read-only JSON aggregation requiring COMPLETE/14 passing stages; reports separate counts, recovery distribution, mixed outcomes and overlap observations. Tested read-only against the old completed campaign; its output matched old counts, written only to `/tmp/saner-prior-summary.json`.
- `.gitignore` additionally excludes the new campaign runs/*/work/ to avoid nested repositories; raw trees must be archived before a final commit/handoff.
- No commits, pushes, publication, or automation changes were performed.
- Preserve pre-existing untracked `.idea/` and `paper/saner/tmp/`.

## Finish after restart

1. Inspect running campaign, wait for all stages or preserve interruption/failure. No duplicate.
2. Reaggregate new results using the summary tool, inspect traces and all verification reports. Confirm each topology's initial/repair/no-op counts and actual overlap timing. Do not pool versions or attempt counts. Explain material differences only if supported.
3. Archive new complete work with the archive utility, extract into a NEW temporary directory, then rerun core/recovery/three-/four-node verifiers offline in the exact runner. Core command: `python3 /results/verify-core.py /results/core 1.10.0`; recovery: `python3 /results/verify-recovery.py`; mixed scripts accept their /results/mixed-*/run-* path. Mount extracted work at /results and its harness at /exp; runner network none. Preserve the verifier outputs and archive SHA-256/file count. Add checksums for final campaign evidence, without modifying prior raw observations.
4. Write `paper/saner/evidence/EXPERIMENTS-1.10.0-20260909.md` (not yet created), with exact identity, raw counts, retained prior oracle correction, feature-check addendum, and reproduction checks. Prior 1.8.2 and 1.9.0 evidence remains historical and immutable.
5. Update *current* version/results in main.tex, evaluation.tex, mixed-results.tex, system.tex's evaluated-version POSIX-shell sentence; use 251 command records only after final verification. Historical version strings must remain accurate. The prior strict-overlap failure occurred in 1.9.0; clarify attribution when describing new rerun.
6. Update README.md, paper/saner/SOURCE.md, EDITING-REQUIREMENTS.md, CONTINUATION.md, and top of output/saner-2027/research-report.md to current verified evidence. Preserve old sections as history. Scope is canonical conference paper; do not start translations or technical-report overhaul.
7. Build Tectonic, run check.py, render all 12 pages at 1600 or better and visually inspect every page. Keep 10+2 with normal fonts/margins; shorten redundancy if needed. Copy final verified PDF to output/pdf/saner-2027-paper.pdf and record its SHA-256. Last intermediate layout passed but has not been visually checked.
8. Send final counts/paths/lock+archive+PDF hashes and limitations to the product task and user. User will personally revise before submission; public/preprint anonymity history and exact AI model labels remain author decisions. No submission or public artifact action is authorized.

## Final coordinator note before restart

README-only postrelease CI 34378282975 Build failed during proxy.golang.org go mod download with HTTP/2 INTERNAL_ERROR. Tests, native ARM64 export, format/vet passed. Official 1.10.0 release remains successful; baseline unchanged. Product coordinator retained failure log, no retry yet. Product restart record: `/Users/yohimik/Projects/dispat/output/RESTART-HANDOFF.md`. This later CI failure must not be described as a failed 1.10.0 release or a reason to change the frozen experimental binary.

Latest checkpoint 2026-09-09T17:06:54.968219+00:00: RUNNING, 9 completed stages. Consult the refreshed JSON snapshot for exact live process/container identities and mixed progress.
