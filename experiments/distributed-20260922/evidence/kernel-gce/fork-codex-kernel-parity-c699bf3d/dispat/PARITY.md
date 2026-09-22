# Establish 1x before expanding the workload

Audit and experiment date: 2026-09-22. Repository initially inspected at
`f7691276`. Other projects are deferred until parity is demonstrated. The real,
compiler-matched experiment in the separate Google Cloud project
`dispat-linux-parity` completed its grouped, split, and batched trials. None met
the elapsed-time gate. The measured results and exact orchestration are in
[`gce/PARITY-20260922.md`](gce/PARITY-20260922.md). The original project's LLVM
experiment was left alone.

## What the existing run establishes

The historical [GCE report](gce/REPORT.md) records completed worker tasks, not a
speedup. Its reported script-to-farm ratios are 3.5 for alpha, 2.3 for hexagon,
and 1.8 for m68k_nommu. UML's few-second script time is not a useful throughput
baseline without a retained successful-build result. No QEMU group was measured.
The report's raw logs were not found in this repository or the inspected local
experiment directories; its timings have not been independently reconstructed.

The old wrapper treated the script exit code as success. However,
`stable-build-arch.sh` finishes with an `echo`, after accumulating errors, so
kernel failures can still return zero. It also treated `failed (config)` lines
as failures, whereas the farm's image-build observer classifies them as skips.
The old wrapper deleted its own cell log on exit. Consequently a completed or
published task does not establish that its kernel configurations passed.

The new adapter addresses those issues, records KUnit totals and traceback
markers, and rejects missing/unrecognized results. This is intentionally stricter
than treating an all-skipped group as a successful build. Per-case records are
retained so coverage can be checked, rather than comparing aggregate counts alone.
Evidence remains worker-local and must be copied out before VM deletion.

The GCE worker launcher now disables the idle timeout, as the historical report
already recommended. This is a workaround, not a fix to the dispat engine.

## Define two separate comparisons

1. **Farm parity:** exactly the same pinned kernel revision, configurations,
   compiler versions, QEMU/rootfs inputs and skip policy as the reference farm,
   with equivalent per-case results. Completion time must be no greater than the
   matching farm run. The recorded full-matrix target is 232 minutes for 57 groups;
   that full claim requires the 31 QEMU groups too.
2. **Execution overhead:** the same workload and hardware allocation, directly
   invoked versus dispatched by dispat, with matched cache state and concurrency.
   This isolates scheduling/transfer overhead from machine performance. Matching
   this baseline alone does not establish parity with the farm.

For either, define speedup as baseline seconds / candidate seconds. At least 1.0
is the target. Report the reciprocal runtime ratio explicitly if using it.
Retain both execution status and test outcome: reproducing a known baseline
failure can be equivalent coverage, but must not be published as a passing cell.

## Next controlled experiment

Start with the same alpha/hexagon/m68k_nommu groups for which reference durations
exist. Record actual pass/fail/skip cases and exact compiler versions first.
Then include x86_64, arm and powerpc: small groups alone cannot establish that the
long tail is solved. Finally run the complete matrix, including QEMU.

Use pinned source and worker images; preserve configuration lists and fixes.
Measure cold end-to-end and warm-cache runs separately. Retain per-config elapsed
time, CPU time, peak memory, disk wait, fetch/checkout/transfer durations and test
results. Run repeated direct/dispatched pairs on the same allocation and report
the median and range. Keep worker count and total CPU/RAM visible in comparisons.

Only then select an optimization supported by the measured bottleneck:

- Split long architecture groups at configuration boundaries to reduce the last
  task's duration. The existing script reuses its output directory between
  configurations, so splitting can duplicate work; compare total CPU time as well
  as elapsed time. Start with the long x86_64/arm/powerpc groups, not tiny cells.
- Budget build jobs across the host. Currently each image cell asks for
  `1.5 * nproc`; increasing worker slots without reducing jobs can oversubscribe
  the same CPU and memory.
- Prewarm sources/toolchains and measure persistent compiler caching separately.
  The existing bare Git cache saves downloads, not compilation. Use identical
  cache conditions for both arms of the experiment.
- For QEMU, preserve the existing configuration reuse in `dosetup`; split test
  execution only where it does not cause redundant kernel builds. Per-target
  filesystem caches also need concurrency review before overlapping the same
  target on one host.

Scheduling more cells on already saturated machines is not itself a speedup.
The historical README estimates a 180–232 minute scheduling range on the original
farm. The GCE report's larger-machine and full-matrix forecasts are estimates,
not parity evidence. Its sums of builder durations must not be silently equated
with exclusive machine-hours when builders overlapped on a host.

## Reference recovered for the experiment

The actual farm logs use GCC **16.2.0** and binutils **2.47.20260726** for
alpha and m68k_nommu, and Ubuntu clang **18.1.3 (1ubuntu1)** for hexagon.
The older GCE experiment's GCC 14.3 is not a matching reference compiler.
All three groups test kernel commit `93f51579e7df248780214094418f205253383cc5`
(`v7.3-rc4`).

| Group | Farm build-step elapsed | Required successful cases |
|---|---:|---:|
| [alpha](https://kerneltests.org/builders/upstream-alpha-master/builds/332) | 623 s | 4 |
| [hexagon](https://kerneltests.org/builders/upstream-hexagon-master/builds/330) | 111 s | 3 |
| [m68k_nommu](https://kerneltests.org/builders/upstream-m68k_nommu-master/builds/331) | 128 s | 5 |

These are individual build-step durations, not the wall time of a three-group
parallel farm run. Their sum must not be presented as that wall time. Each new
architecture phase is judged against its own reference, including the new
phase's dispatch and reporting overhead. `compare.py` implements that gate with
the retained exact configuration lines and tool identities.

## Orchestration and changes under test

The orchestrator prepares a signed source snapshot and assigns ready packages.
A worker polls task refs, checks out the farm scripts, and invokes
`dispat/run-cell.sh`. That wrapper prepares the pinned kernel tree, then invokes
`bin/stable-build-arch.sh`. The original grouped script executes its architecture's
configurations sequentially. It does not itself dispatch work to other machines.

The control placed hexagon, then m68k_nommu, then alpha on the single C3 worker.
This was observed scheduling order, not a declared dependency between those
architectures. There is no coordinator queue pause after a received result: the
next task is assigned in the same logged second. Initial source transfer took
45 seconds, the first assignment took 27 seconds to be claimed, farm worktree
creation took approximately 3 seconds, and completed results took 4–5 seconds
to reach the coordinator.

The candidate experiment exported only image-build inputs (with a SHA-256 manifest),
used a single Git repository for source and task refs, and scheduled individual
configurations on two workers. Each cell still uses a private kernel tree and
fresh build output. A warm kernel source cache is not a compiled-object cache.
The wrapper records kernel fetch, checkout, and lock wait separately from the
build script. `timing.py` reconstructs assignment and reporting delays from both
coordinator and worker logs.

Finer scheduling cannot shorten a single configuration's compilation by itself.
If that critical task exceeds its reference, the next experiment must address
its compute capacity or compilation strategy. The local `../dispat` repository
belongs to another agent and is not changed by this work.

## Resource check

At approximately 02:05 UTC, project `dispat` reported 32/32 global vCPUs in use:
`lb-orch` (4), `lb-w1` (14), and `lb-w2` (14). These are a newer LLVM experiment,
not the deleted kernel-run VMs described in the historical report. Both workers
had no compiler activity in the snapshot; the orchestrator was running Git during
source preparation for run `62c1d6e407137e204dad090a311ff478`.

At the user's request, created the separate project
`dispat-linux-parity`, linked the existing billing account and enabled Compute
Engine. It has a 32-vCPU global limit. Initial resources are an e2-standard-2
orchestrator, a c3-standard-22 worker (11 physical cores, two threads per core),
and a t2d-standard-8 worker (8 physical cores, one thread per core). Only the C3
worker participated in the grouped control. The second worker participated in
the split and batched experiments. Instances were created with a two-hour
automatic stop limit. After evidence collection, all three VMs and their attached
disks were deleted at the user's request. The verified evidence archive remains local.

The original project's active LLVM run and the default CLI project (`dispat`)
remain unchanged. Any later machine change must be reported with the measured
result; this experiment does not imply equal hardware or equal cost to the farm.
**Do not claim 1x until the complete measured phase passes the comparison gate.**
