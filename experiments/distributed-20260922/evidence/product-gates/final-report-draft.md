# Final report draft (rc 1.11.0-rc.4 with worker nodes; parity experiments)

## State of the branch
- `claude/worker-nodes` in `~/Projects/dispat-worker-nodes`, tip e389789a (+ any later), cut from main 599448fd; NOTHING PUSHED.
- Release preview (`dispat status`): held=0, releasing=10: dispat, models, docs, agent-guide 1.11.0-rc.4, cli + dispat-alpine/debian/dind/ubuntu propagated, ccme-spec 3.1.0-rc.3. Hold 3ac7cc4f lifted by 0b33ac46.
- Gates verified: full sharded suite 6/6 on 729ef327 and e389789a; publication subset + execution -race; unit suites; namingcheck 0; test plan 1535 refs, 139/139, critical 70/70; spec verify/test pass; docs build + typecheck (gate 15).
- TinyGo gate: SKIPPED for this rc on the user's order; dispatch input `skip_tinygo_gate: true` (5dcd9e0d).
- Coverage: integration-only 94.21% (gate 95%): dispatch input `coverage_minimum_integration` (181a795c, docs b91144bc); the user states 94 at dispatch or holds.
- Tip: b91144bc. Preview unchanged: 10 releasing.
- How to release: push `claude/worker-nodes` (or merge to main and push), dispatch release.yml with skip_tinygo_gate=true and coverage_minimum_integration=94; the rc preview JPEGs still show the previous candidate's words (crier cannot render locally).

## Bugs found after testing (separate list, as asked)
(by gate; each has a test and a bug-fence row)
- Gate 2: node name with `..`; ssh://git@host refused; scp endpoint echoed password.
- Gate 3: `.` and package-holding roots accepted as build outputs.
- Gate 5: git runner returned stdout on failure to 70 callers (TagObject of a missing tag).
- Gate 6: MAC over document bytes only (cancel relabelled as go).
- Gate 7: queued work never re-looked at (Reconsider); snapshot branches logged as rejected assignments.
- Gate 8-9: oversize manifest pushed then unreadable (waited out the deadline); tracked files in roots counted as stray; symlink climbing after descending.
- Gate 9b: orchestrator-pinned package refused at preflight; local build held the snapshot guard for its whole duration.
- Gate 10: consumer held a pool slot while waiting for its provider (deadlock).
- Gate 11: delegated publication of a package with buildOutputs refused (results run through admission).
- Gate 12-13: withdrawal leased against a stale object (interrupts wrote no cancellation); unwritable authorization push retained a lock; queue time counted as run time; idle clock; unfetchable branch stalled the poll; cancel tips unauthenticated.
- Gate 14: mode L wholly broken (closure materialization order); one failed read cost a task deadline; fixture repack.
- Gate T: discovery failure logged as "refusing to release".
- State lock: empty lock read as stale (two workers on one folder).
- Gate A: (none in gate A code; two existing tests re-aimed by design: TestPolyrepoSameTagSpelling..., TestPublishOrderCountsOnlyDeclaredProviders...).
- After coverage rows (found by crafted tests, fixed 80e9aabe): refused authorization never reported (deadline + E228 + retained lock for nothing); withdrawal over an unread authorization refused as replay.
- LLVM field runs: fixed report timeout (f0c9e959: 1.7 GB result push killed at 30 s).
- Load-dependent rows re-aimed: TestExecutionUnauthorizedPublisherNeverStarts (two valid loss paths).

## Deviations from the spec / decisions
- Owed windows + E201 (51d96afe) NOT implemented (departure recorded a7bce48e); consumer sitting out the run where its provider releases the owed commit stays stranded.
- Script reconciliation with every provider dead may keep the optimistic write (§19.5).
- isBlocking default false for none (user: consumer with own change proceeds).
- `pkg/models` field type change IsBuildWaitingPublish *bool → *StageRelation as feat (minor).
- One failed lock read = loss (safe side, no retry).
- Category native-recording-or-lock not attached at legacy sites.
- `waitingOn` direct-only; optional deps both order and block; dev-only cycle refused.
- publish delegated only by explicit worker; login pins to orchestrator.

## Follow-ups / tech debt
- bundle service; per-link secrets; cross-run output cache; distributed `dispat run`; elastic/dynamic pool + quorum preflight + retry on another node; keep-ref/history-free snapshot (repeated whole-history push); claim-before-fetch (cold worker first claim minutes late); worker-speed-aware placement / per-package node pin (1.8x on the kernel fleet); configurable poll interval (preflight 3-8 s); results retention of exports; maxManifestBytes floor; flock-based state lock; Pool.Acquire unused wrapper; DISPAT_EXPORT_GITHUB attachments from workers; syncLock after re-reconciliation; re-reconciliation ordering vs worker-placed publish snapshot; suite t.Parallel; TestDiagnosticCodesAreDocumented scans plan.go only; three tag-push paths; fleet PushRelease re-annotation; coverage-flush question for SIGINTed runs; CI timeouts raised (gotest 60m/90m race, tiny 120m).

## Parity
- Linux round 2: PASS hexagon 92.22/95.89 vs 111; m68k_nommu 115.48/115.61 vs 128; same-hardware pairs 122.62→92.22, 138.01→115.48; alpha needs c3-standard-88 (quota C3 ≥ 88, all-regions ≥ 96); branch codex/kernel-parity c699bf3d (dispat-prototype unchanged at f7691276).
- LLVM, single-heavy fixture: baseline 36:09 (w2 alone); distributed 26:47 for llvm+lld+polly vs 20:16 for the same three: time NOT ≤ original (transfer of the 1.4 GB install tree; two tiny consumers).
- LLVM, matrix fixture (llvm X86 + llvm AArch64 + lld + polly + uncompressed bundle, same recipe both sides, fork d8fb8408 / lb-orch 6c1a5fcd): baseline on one node 41:12.02 (five packages); distributed attempt 7 reached lld/polly published at 26:35 then failed the bundle on the THIRD dispat bug (attributes corrupting captured binaries; fixed 9f649f88 on main); attempt 9 with the fixed binary: PENDING (expected ~29 min) + compare.py verdict.
- Third bug found by the field run: `git add` capture honoured `.gitattributes` `text` and rewrote CRLF pairs inside polly's libraries; fix: hash-object --no-filters + update-index --index-info; unit + integration bug fences; main 272772cb; full suite 6/6 green.
