# Kernel build cells on Compute Engine workers: measured run of 2026-09-22

A first real run of the farm's image-build scripts through dispat worker nodes, on three Compute Engine VMs,
against Linux v7.3-rc4. Four build groups finished, one was lost to a spot preemption, and the run was restarted
twice because of two dispat defects found on the way. Every number below is measured unless the sentence says it
is estimated; the logs the numbers come from are named at the end.

## Machines

| Node | Shape | CPU | Memory | Disk | Price (list, estimated) | Role |
|------|-------|-----|--------|------|--------------------------|------|
| `lb-orch` | e2-standard-4, on-demand | 4 shared vCPU | 16 GB | 50 GB pd-balanced | $0.13/h | orchestrator, mailbox (bare repository over internal ssh), farm checkout |
| `lb-w1` | n2-custom-14-28672, spot until preempted, then on-demand | Intel Xeon @ 2.80 GHz, 7 cores / 14 threads | 28 GB | 120 GB pd-balanced | $0.17/h spot, $0.55/h on-demand | worker, 1 slot |
| `lb-w2` | n2-custom-14-28672, spot | same | 28 GB | 120 GB pd-balanced | $0.17/h spot | worker, 1 slot |

Software on the workers: Ubuntu 24.04, kernel.org crosstool gcc 14.3.0 (linked under the `gcc-14.3.0-2.44-nolibc`
name the scripts expect), Ubuntu clang 18 for hexagon, git 2.43. dispat: the worker-nodes branch at commit
`1146c210`, built as a static linux/amd64 binary. The farm scripts ran unchanged except that
`bin/stable-build-arch.sh` takes its build folder and log path from the environment.

Two workers rather than six because the project's global Compute Engine quota is 32 vCPUs. The 14-vCPU shape is
what fits twice beside the orchestrator.

Guenter's farm, for comparison: six machines (`server`, `saturn`, `desktop`, `jupiter`, `mars`, `neptune`), `mars`
an AMD Ryzen 9 5900X (12 cores, 24 threads) per his mail, the others not stated; buildbot runs at most two image
builds or three qemu targets per machine at once. For v7.3-rc4 its 57 upstream builders took 23.0 machine-hours in
3 h 52 min of wall time.

## What ran, in order (UTC)

| Time | Event |
|------|-------|
| 00:03:26 | Run 1 starts: plan of 7 packages (`kernel` + arm64, mips, alpha, sh, m68k, csky). |
| 00:03:32 | Both workers answer the preflight probe: 4 s round trip over the mailbox. `kernel` builds and publishes on the orchestrator. |
| 00:04:10 | `m68k` assigned to `w1`, `alpha` to `w2`. |
| 00:04:47 | Both claimed (37 s: poll back-off plus the first fetch of the 1.4 GB farm objects over the internal network). |
| 00:04:49 | Farm worktrees materialised (2 s). Cells start: kernel fetch, then the first config. |
| 00:23:08 | `w1` is **preempted** by Compute Engine, 18 minutes into `m68k`. Its build is lost. |
| 00:26:26 | `w2`: `alpha:defconfig` done, `allmodconfig` starts (21.6 min from claim, including the kernel fetch). |
| 00:41:27 | `alpha:allmodconfig` done (15.0 min); `allnoconfig` 0.7 min; `tinyconfig` under a minute. |
| 00:42:20 | `w2` reports `alpha` succeeded, then **stops itself** ("idle"): the idle window elapsed during the build. |
| 00:42:25 | Orchestrator records `alpha` published (38.2 min from assignment) and assigns `sh` to `w2`, which nobody claims. |
| 00:43:27 | Replacement `w1` (on-demand) is up. Run 1 interrupted by hand to reassign; cleanup deletes its branches by 00:43:32. |
| 00:44:01 | The new `w1` **stops itself** "idle" 34 s after starting, with a 900 s idle timeout. |
| 00:55:20 | Run 2 starts with three small cells; the preflight waits five minutes for workers that have both exited, and refuses (E225). |
| 01:06:42 | Run 3 starts, workers restarted with no idle timeout. Both ready at 01:06:46. |
| 01:07:25 | `hexagon` assigned to `w1`, `m68k_nommu` to `w2`; claimed 3 s later. |
| 01:08:41 | `w1` has fetched the kernel (71 s) and starts `hexagon:defconfig`. |
| 01:11:35 | `m68k_nommu` done on `w2` (4.1 min, 5 configs); `um` assigned to `w2`, done in 14 s (1 config). |
| 01:12:55 | `hexagon` done on `w1` (5.5 min, 3 configs). |
| 01:13:10 | Run 3 ends: 3 cells published, 0 errors, mailbox empty. VMs deleted at 01:15. |

## Cell timings against Guenter's

His numbers are the `buildcommand` step of the same builder on the v7.3-rc4 run, measured while sharing the
machine with one other build.

| Cell | Configs | Guenter | Here, claim to result | Of which fixed overhead | Script time | Ratio (script / his step) |
|------|---------|---------|------------------------|--------------------------|-------------|----------------------------|
| alpha | 4 | 623 s (`saturn`) | 2250 s | about 70 s (kernel fetch, cold) | about 2180 s | **3.5** |
| hexagon | 3 | 111 s (`mars`) | 324 s | 71 s (kernel fetch, cold) | 253 s | **2.3** |
| m68k_nommu | 5 | 128 s (`jupiter`) | 246 s | about 10 s (cache warm) | about 236 s | **1.8** |
| um | 1 | 24 s (`saturn`) | 14 s | about 10 s | a few seconds | below 1, fixed costs dominate both sides |
| m68k | 9 | 799 s | lost at 18 min to the preemption | | | |

Inside the alpha cell: `defconfig` about 20 min, `allmodconfig` 15.0 min, `allnoconfig` 0.7 min, `tinyconfig`
under a minute. The `defconfig` figure includes the cold kernel fetch and `git clean`; the 20-second poller that
would have split it was started late. Inside hexagon: `defconfig` 2.3 min, `allnoconfig` 1.3 min, `tinyconfig`
about 0.5 min.

Each cell exported its pass, fail and skipped counts and the `git describe` reference to the run (five values per
cell, the orchestrator counted them), but nothing in this setup retained the values: the log keeps the count, the
mailbox was deleted with the VMs. Every cell's script exited 0. A results page is the first thing a second run
needs.

## Coordination overhead, measured

| Step | Cold | Warm |
|------|------|------|
| Probe round trip (orchestrator to worker and back over the mailbox) | 4 s | 4 s |
| Assignment to claim | 37 s (first fetch of the 1.4 GB farm objects) | 3 s |
| Claim to farm worktree ready | 2 s | 2 s |
| Kernel fetch, one commit deep, from git.kernel.org | 71 s | about 0 s |
| Result pushed to orchestrator noticing it | 5 s | 5 s |

Against cells of four to eighty minutes the coordination is noise. The kernel fetch is the one cost worth
removing, and a warm cache removes it.

## Why the ratio, and what it says about the forecast

The n2 shape here is 7 physical cores at 2.8 GHz with hyperthreads; a 5900X is 12 cores at up to 4.8 GHz. A
per-cell ratio of 1.8 to 3.5 against his step times, which were themselves taken under sharing, is what that
hardware gap predicts. The ratio grows with the share of `allmodconfig` and `allyesconfig` work in a cell, and his
long groups (x86_64, i386, powerpc, arm, riscv64) are made of exactly that, so the pessimistic band is the one to
plan the long groups by.

The first email's replay of his step times on "24 slots" assumed a slot is a machine's worth of CPU. It is not,
and his reply said so: his machines are saturated by two image builds. The forecast below therefore counts
machines, not slots, and uses measured cells.

## Forecast: the full 57-group upstream matrix on this worker shape

Guenter's 26 image-build groups sum to 10.6 machine-hours and his 31 qemu groups to 12.3 on his farm. Scaling by
the measured ratios and adding 50 s of overhead per cell, with a longest-task-first placement:

| Ratio | Builds only, machine-hours | 4 workers | 6 workers | 8 workers | 12 or more | Cost at 8 (spot / on-demand) |
|-------|-----------------------------|-----------|-----------|-----------|------------|-------------------------------|
| 1.8 optimistic | 20.0 | 5.0 h | 3.4 h | 2.6 h | 2.5 h (x86_64 sets the floor) | $4.3 / $12.7 |
| 2.5 neutral | 27.4 | 6.9 h | 4.7 h | 3.5 h | 3.4 h | $5.9 / $17.4 |
| 3.5 pessimistic | 37.6 | 9.4 h | 6.5 h | 4.8 h | 4.7 h | $8.1 / $23.8 |

With the qemu groups scaled the same way (untested: no qemu ran here), the whole matrix is 43 to 81 machine-hours
and needs 24 workers of this shape to reach 2.5 to 4.7 hours of wall time, which is what his six machines already
do in 3 h 52 min.

So on 14-vCPU Xeon workers the farm is not beaten; matched at best, at about 24 machines. The realistic reasons
to run it this way are elasticity and idle cost, not speed: machines exist only while a run does, and
`--max-run-duration` deletes them even if nothing else does. To beat the farm's wall time on Compute Engine one
needs a shape with more and faster cores per cell (a 32-vCPU n2 or a c3 halves the pessimistic ratio to about
1.8, estimated, not measured) and the qemu groups measured.

For the six-cell set the first run set out to build (88 of his farm-minutes), the neutral ratio gives 3.7
machine-hours, or about 1 h 50 min of wall time on two of these workers. It was never going to take an hour.

## Incidents and defects found

1. **Spot preemption** killed `w1` 18 minutes into a build. dispat has no retry on another node yet: the cell
   stayed assigned until the run was interrupted. Builds on spot machines need that retry; publishes must never
   run on spot machines.
2. **`--idle-timeout` misfires** (dispat defect, fenced for the recovery gate): the idle clock is not restarted when
   a task that outlasted the window ends (`w2` stopped 5 s after a 38-minute build), and a freshly started node
   stopped "idle" after 34 s. The second run was lost to it.
3. **Snapshot branches logged as rejected assignments** (dispat, cosmetic): every `…-snapshot-…` branch produces a
   warn line `E226 unreadable` on the worker. Fenced for the recovery gate.
4. **Operator mistakes** worth writing down: a `pgrep -f`/`pkill -f` pattern that matches the ssh session running
   it (killed my own restart script and later a poller); a monitor that never ended for the same reason; the
   per-config poller started twenty minutes after the first cell.
5. **Results are not retained**: the exported counts reached the orchestrator and went nowhere.

## What a second run should change

- A results page or file per run from the exported values, and the cell log tail in the result.
- `--idle-timeout 0` on workers until the defect is fixed; kill them with the VMs.
- Warm the kernel cache in the worker image, or keep the worker VMs' disks between runs.
- On-demand for anything a run cannot lose; spot only once builds can be retried on another node.
- A 32-vCPU shape to measure the long groups (x86_64, i386, powerpc, arm) once each; those set the floor.
- Six workers and the qemu groups, which need the farm's qemu build on the image.

Cost of this experiment: about one dollar of machine time (estimated from list prices), plus the network egress of
one kernel fetch per worker.

Logs kept: `release-run1.log`, `release-run2.log`, `release-run3.log` (orchestrator, debug level), `w1/worker.log`,
`w1/worker-run3.log`, `w2/worker.log`, `w2/worker-run3.log`, and the 20-second `cell-timeline.log` of each worker.
