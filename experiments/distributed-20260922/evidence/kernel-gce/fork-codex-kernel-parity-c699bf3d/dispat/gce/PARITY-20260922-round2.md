# Kernel build parity experiment, round 2, 2026-09-22

Two of the three groups with a public reference now meet the gate, twice each.
A dispat-distributed release of the hexagon group takes 95.89 s and 92.22 s
against a 111 s reference, and of the m68k_nommu group 115.61 s and 115.48 s
against a 128 s reference. `dispat/compare.py` accepts all four runs: same
kernel revision, same compiler and assembler identities, same exact case lines,
elapsed time below the reference. The alpha group was not attempted, because the
arithmetic below shows no machine within this project's quota can build
`allmodconfig` inside its 623 s reference.

Beside that comparison stands a same-hardware pair: each group also ran once
on the one `c3-standard-22` alone, with the worker removed and nothing else
changed. Both groups miss the reference that way, at 122.62 s and 138.01 s,
so the second machine is what carries them.

This is the same targeted experiment round 1 ran, on the same three groups. It
is not evidence for the complete 57-group image and QEMU matrix.

[`PARITY-20260922.md`](PARITY-20260922.md) holds round 1 and is unchanged.
The references are unchanged in
[`parity-20260922-reference.json`](parity-20260922-reference.json).

## What was measured

The gate is GNU `time` elapsed of one `dispat release` for one group, from
invocation to exit. It contains the release lock, the plan, the preflight probe
of the worker, the source snapshot, assignment and claim polling, the source
lease, the complete build script, the result transport and the records. VM
provisioning, toolchain installation and the one-time kernel source preparation
are outside it, as they were in round 1.

The tested binary is the prebuilt static linux/amd64 `dispat` at
`/tmp/dispat-gce/dispat`, built from the feature branch tip `f0c9e959`. Its
SHA-256 is
`63441cc66f68d07b5efbf9a42edd5559304d153d48b82b1dfb037349e20606ed`.
The `../dispat` working tree was neither read nor changed.

Every node installed the reference farm's own toolchains and confirmed them in
its startup log before any run
([`round2/calibration/cal-c3-toolchains.txt`](round2/calibration/cal-c3-toolchains.txt)):

    Ubuntu clang version 18.1.3 (1ubuntu1)
    alpha-linux-gcc (GCC) 16.2.0
    GNU assembler (GNU Binutils) 2.47.20260726
    m68k-linux-gcc (GCC) 16.2.0
    GNU assembler (GNU Binutils) 2.47.20260726

The kernel is v7.3-rc4 at `93f51579e7df248780214094418f205253383cc5` on every
node, fetched once during setup. Source is warm and compiled output is cold in
every timed run, which is the reference farm's condition.

## Machines

| Name | Shape | Zone | Processor | Physical cores | Role |
|---|---|---|---|---|---|
| `cal-c3` | `c3-standard-22` | us-central1-a | Intel Xeon Platinum 8481C at 2.70 GHz | 11, two threads each | calibration |
| `cal-t2d` | `t2d-standard-8` | us-central1-b | AMD EPYC Milan | 8, one thread each | calibration |
| `par-c3` | `c3-standard-22` | us-central1-a | Intel Xeon Platinum 8481C at 2.70 GHz | 11, two threads each | runs `dispat release` and builds |
| `par-t2d` | `t2d-standard-8` | us-central1-b | AMD EPYC Milan | 8, one thread each | worker `w1`, one build slot |
| `solo-c3` | `c3-standard-22` | us-central1-b | Intel Xeon Platinum 8481C at 2.70 GHz | 11, two threads each | same-hardware pair: builds every cell, no worker |

`c3-standard-22` reports 22 hardware threads on 11 cores; the T2D family has no
simultaneous multithreading, so `t2d-standard-8` is 8 cores. Each pair is 30 of
the 32 vCPUs this project may hold at once. The T2D machines are in
us-central1-b because `t2d-standard-8` was unavailable in us-central1-a:

    ZONE_RESOURCE_POOL_EXHAUSTED: A t2d-standard-8 VM instance is currently
    unavailable in the us-central1-a zone.

The quota that binds is regional, so a second zone of the same region costs
nothing, and the two machines share one VPC subnet. Every machine was created
with `--max-run-duration 2h --instance-termination-action DELETE` and deleted by
hand as soon as its work finished. The calibration pair lived 22 and 20 minutes,
the parity pair 22 minutes each and the single node 10 minutes.

## Calibration

Round 1 chose its machines from expectations about per-core speed. This round
measured the farm's own script bodies first, outside dispat, with
[`calibrate.sh`](calibrate.sh) and the plans in
[`round2/calibration`](round2/calibration). Every line is one invocation of
`bin/stable-build-arch.sh` in a prepared source tree with its own build folder;
lines in the same group start at the same moment.

`c3-standard-22`, raw output in
[`round2/calibration/cal-c3.txt`](round2/calibration/cal-c3.txt):

| Cells started together | make jobs each | Seconds per cell | Group |
|---|---|---|---:|
| hexagon defconfig | 33 | 73.92 | 73.93 |
| hexagon defconfig, tinyconfig | 17 | 90.88, 48.02 | 90.89 |
| hexagon defconfig, allnoconfig, tinyconfig | 11 | 120.11, 81.04, 63.67 | 120.12 |
| m68k_nommu m5272c3, m5307c3, and the last three batched | 11 | 86.64, 86.04, 158.17 | 158.18 |
| m68k_nommu first two batched, last three batched | 17 | 121.66, 150.82 | 150.83 |
| m68k_nommu, all five as separate cells | 7 | 128.16, 127.41, 126.65, 127.04, 103.16 | 128.17 |
| alpha defconfig | 33 | 68.48 | 68.49 |
| alpha allnoconfig | 33 | 33.16 | 33.17 |
| alpha tinyconfig | 33 | 24.04 | 24.05 |

`t2d-standard-8`, raw output in
[`round2/calibration/cal-t2d.txt`](round2/calibration/cal-t2d.txt):

| Cells started together | make jobs each | Seconds per cell | Group |
|---|---|---|---:|
| hexagon allnoconfig | 12 | 87.51 | 87.52 |
| hexagon allnoconfig, tinyconfig | 6 | 119.14, 92.29 | 119.15 |
| m68k_nommu first two batched, last three batched | 6 | 236.18, 295.49 | 295.51 |
| m68k_nommu m5272c3 | 4 | 173.08 | unfinished |

The last line is the start of a group the machine was deleted before finishing;
it is kept because it is real and is credited with nothing.

Three facts decided the topologies.

The first is that these builds do not use a whole machine. One m68k_nommu
configuration alone at `-j33` took 34 to 35 s in round 1 on this shape, so five
in turn would be about 170 s; five started together at `-j7` finished in
128.17 s. A single build leaves roughly a fifth of `c3-standard-22` idle, and
starting several recovers it.

The second is that hexagon is the opposite case: its three configurations
crowd each other. Started together at `-j11` the group took 120.12 s, worse
than defconfig alone at `-j33` plus a worker for the rest.

The third is that `t2d-standard-8` cannot hold hexagon defconfig. Round 1
measured 147 s for it there against a 111 s reference, so the fast machine must
build it, and a pool of equal small workers is not an option for this group.

## Budget arithmetic

Subtracting the release's fixed overhead from the reference gives the budget for
the longest cell. The fixed overhead measured here is 3 to 8 s from the release
starting to `worker ready`, and under a second to record the run once the last
cell finishes:

- hexagon: 111 - 9 = 102 s for the longest cell, its claim and its result.
- m68k_nommu: 128 - 9 = 119 s for the same.

Round 1's split hexagon needed 130 s of script on one worker plus two 7-8 s
checkouts, and its m68k_nommu candidates needed 167 s on one worker. Both are
outside those budgets, which is why they lost on elapsed time alone.

## Topologies

dispat offers two placement classes, so each group is written as packages pinned
to the machine that starts the release and packages left to the worker. The
configurations are in [`round2/par-c3`](round2/par-c3).

hexagon, `dispat.hexagon.yaml`, `execution.concurrency: 2`:

| Cell | Machine | make jobs |
|---|---|---:|
| `build-hexagon-defconfig` | `par-c3`, `runOnly: orchestrator` | 24 |
| `build-hexagon-tinyconfig` | `par-c3`, `runOnly: orchestrator` | 9 |
| `build-hexagon-allnoconfig` | `par-t2d` worker `w1` | 12 |

m68k_nommu, `dispat.m68k_nommu.yaml`, `execution.concurrency: 4`: the four
configurations the calibration found most expensive run together on `par-c3`,
and the cheapest goes to the worker.

| Cell | Machine | make jobs |
|---|---|---:|
| `m5272c3_defconfig`, `m5307c3_defconfig`, `m5249evb_defconfig`, `m5407c3_defconfig` | `par-c3`, `runOnly: orchestrator` | 8 each |
| `m5475evb_defconfig` | `par-t2d` worker `w1` | 12 |

Both files carry `runOnly: [worker, orchestrator]` at the top: a worker cell is
built on the worker and recorded by the machine that started the release. The
reason is in the results below.

## Results

Elapsed is the `elapsed=` field of GNU `time` in
[`round2/par-c3`](round2/par-c3); script seconds are each cell's own
`script_seconds`, the interval around `bin/stable-build-arch.sh`.
[`round2/verdicts.txt`](round2/verdicts.txt) holds `compare.py` on every run.

| Run | Placement and script seconds | Elapsed | Reference | Verdict |
|---|---|---:|---:|---|
| hexagon, first candidate | `par-c3`: tinyconfig 60, defconfig 84; `w1`: allnoconfig 80 | 111.47 s | 111 s | reject: elapsed only |
| hexagon, trial 1 | `par-c3`: tinyconfig 70, defconfig 85; `w1`: allnoconfig 82 | 95.89 s | 111 s | accept, 1.158x |
| hexagon, trial 2 | `par-c3`: tinyconfig 71, defconfig 84; `w1`: allnoconfig 81 | 92.22 s | 111 s | accept, 1.204x |
| m68k_nommu, trial 1 | `par-c3`: 95, 96, 96, 97; `w1`: m5475evb 50 | 115.61 s | 128 s | accept, 1.107x |
| m68k_nommu, trial 2 | `par-c3`: 105, 105, 106, 107; `w1`: m5475evb 51 | 115.48 s | 128 s | accept, 1.108x |

`compare.py` accepted the exact case lines, the compiler, the assembler and the
revision in all five runs, and rejected only the first candidate's elapsed time.
Every cell reported `passed`, three cases for hexagon and five for m68k_nommu,
with no skips and no unrecognized lines.

The timelines, in seconds from `release started`, are read from the JSON logs in
[`round2/par-c3`](round2/par-c3) and
[`round2/par-t2d/worker.log.gz`](round2/par-t2d/worker.log.gz):

    hexagon, first candidate            hexagon, trial 2
     +0 release lock acquired            +0 release lock acquired
     +0 release plan ready               +0 release plan ready
     +8 worker ready                     +8 worker ready
     +8 kernel:build placed, finished    +8 kernel:build placed, finished
     +8 defconfig, tinyconfig placed     +8 defconfig, tinyconfig placed
     +8 allnoconfig assigned to w1       +8 allnoconfig assigned to w1
    +80 tinyconfig finished             +79 tinyconfig finished
   +104 defconfig finished              +91 allnoconfig finished
   +106 allnoconfig finished            +92 defconfig finished
   +106 allnoconfig:publish assigned    exit at 92.22 s
   +111 allnoconfig:publish finished
   exit at 111.47 s

    m68k_nommu, trial 2
     +0 release lock acquired, plan ready
     +8 worker ready; kernel:build placed and finished
     +8 four configurations placed on par-c3
     +8 m5475evb_defconfig assigned to w1
    +66 m5475evb_defconfig finished
   +113 m5407c3, m5249evb finished
   +114 m5307c3 finished
   +115 m5272c3 finished
   exit at 115.48 s

`dispat/timing.py` over the same logs is in
[`round2/timing.txt`](round2/timing.txt). It reports the same overheads from the
worker's side across all five runs: the initial source push takes 0.000 s and
its Git work 0.009 to 0.024 s, the assignment reaches a claim in 0 to 3 s, the
per-cell checkout of the farm repository takes 0 to 1 s, and a finished cell
reaches the coordinator in 0 to 5 s. The release's own Git subprocesses take
7.205 to 7.231 s in every run, which is the lock tag, the snapshot and the refs.

## What each harness change bought

**A leased source tree instead of a worktree per cell.** Round 1 created a
kernel worktree inside every cell and measured 7.026 to 8.327 s for it, on the
critical path of every release. A node now prepares one pristine tree per build
slot during setup, and a cell leases one under an advisory lock, checks it is
the revision under test and has no modified tracked files, and starts
compiling. The lease and the check cost 0.0 s in every warm run
(`source_lease_seconds` in `round2/*/results/*/result.json`).

The check is not free on a tree nothing has read yet: the first candidate, which
was the first release on those machines, recorded 12.0 s of lease on all three
cells, and m68k_nommu trial 1 recorded 14.0 s and 15.0 s on the two slots used
for the first time. Reading every tracked file's metadata is what costs. The
startup script now performs that read once per slot while it prepares the tree,
so a release never pays it. That change was made after these runs and is
credited with none of the numbers above.

**Recording a worker cell on the orchestrator.** In the first candidate the
worker's build finished at +106 s and the release exited at 111.47 s: the
publish stage went back to the worker, which claimed it one poll later, waited
four seconds for authorization and reported back. The stage carries no build
here. Moving it with `runOnly: [worker, orchestrator]` removed 5.5 s from the
end of every release: trials 1 and 2 exit within a second of their last build.
That change alone turned 111.47 s into 95.89 s together with the warm lease.

**A topology the generator can express.** `dispat/generate.py` now takes
`--orchestrator`, `--concurrency`, `--cell-jobs`, `--batch` and
`--publish-on-orchestrator`, so the placement, the slot count, the make jobs per
cell and which configurations share a build directory are written down and
regenerated rather than edited by hand. `--batch` exists because the farm script
reuses its build directory across the configurations of one invocation, which is
the reference farm's advantage; the calibration showed it is worth having for
hexagon and worth nothing for m68k_nommu, whose five configurations are
different boards and share almost no object files.

The three changes together take round 1's split hexagon from 170.07 s to
92.22 s on the same two machine shapes.

## Same-hardware pair, one repetition

The specification owner asked what the second machine is worth, so each group
ran once more on a single `c3-standard-22` with no worker at all: the same
cells, the same per-cell make jobs, the same build-slot setting, the same
recipe, with `runOnly: orchestrator` and no `workers` key
([`round2/solo-c3`](round2/solo-c3)). Only the worker is removed. This machine
reports the same processor as `par-c3`, Intel Xeon Platinum 8481C at 2.70 GHz
with 11 cores and two threads each; it ran in us-central1-b because
`c3-standard-22` had become unavailable in us-central1-a
(`ZONE_RESOURCE_POOL_EXHAUSTED_WITH_DETAILS ... cpu_availability`). With no
worker there is no second machine to reach, so the zone changes nothing.

| Group | One node alone | One node and the t2d worker | Reference |
|---|---:|---:|---:|
| hexagon | 122.62 s | 95.89 s and 92.22 s | 111 s |
| m68k_nommu | 138.01 s | 115.61 s and 115.48 s | 128 s |

One repetition each, against two of the paired runs. Both single-node runs
build every case correctly and are rejected by `compare.py` on elapsed time
alone, at 0.905x and 0.927x of the reference. The second machine is therefore
what carries both groups over the line: without it the same recipe on the same
hardware misses hexagon by 10.5% and m68k_nommu by 7.8%.

Timelines, in seconds from `release started`:

    hexagon, one node alone            m68k_nommu, one node alone
     +0 release lock acquired           +0 release lock acquired
     +0 release plan ready              +0 release plan ready
     +0 kernel built and published      +0 kernel built and published
     +0 all three cells started         +0 all five cells started
   +104 tinyconfig                     +56 m5475evb_defconfig
   +118 allnoconfig                    +91 m5407c3_defconfig
   +122 defconfig                      +92 m5307c3_defconfig
   exit at 122.62 s                   +131 m5272c3_defconfig
                                      +138 m5249evb_defconfig
                                      exit at 138.01 s

Two things in those runs are worth stating rather than hiding.

The first is that `execution.concurrency` did not bound the machine. hexagon
was configured with two build slots and started all three cells at once;
m68k_nommu was configured with four and started all five. With no worker
configured there is no placement protocol at all: the release emits
`build started` and `build succeeded` per package and never assigns, claims or
probes, which also removes the 3 to 8 s preflight the paired runs pay. The
single-node numbers are therefore the best this machine can do with the recipe,
not a throttled version of it.

The second is that the lease and freshness check dominated the m68k_nommu run.
Five cells checked five trees at the same moment on one disk, and two of them
recorded 58.0 s and 66.0 s of `source_lease_seconds` against 0.0 s for the other
three; their build scripts then took only 73 s and 72 s. The same cost appears
as 12.0 to 13.0 s on all three hexagon cells. It is the cold-metadata cost
described above, and 138.01 s is pessimistic by some part of it.

The conclusion does not rest on that run alone. The calibration measured this
same shape building the whole of each group by itself, outside dispat and
without any lease: the hexagon trio took 120.12 s and the five m68k_nommu cells
took 128.17 s of script body. Both are at or above their references before a
single second of release overhead, which is the same answer the two runs above
give.

## alpha: the capacity this project does not have

alpha was not run. `allmodconfig` is one configuration of one cell and cannot be
split, so the group cannot finish before it does.

Measured here on `c3-standard-22`, each alone at `-j33`: defconfig 68.48 s,
allnoconfig 33.16 s, tinyconfig 24.04 s, together 125.68 s. Round 1 measured all
four alpha cases as one script body on the same shape at 1324 s. Subtracting
gives `allmodconfig` at about 1198 s. The subtraction is approximate in one
direction only: round 1's three small cases shared a build directory with
`allmodconfig` and mine did not, so 125.68 s is an upper bound on their share
and 1198 s is a lower bound on `allmodconfig`.

The release's fixed overhead measured in this round is about 9 s, so a
candidate must build `allmodconfig` in about 610 s, a speedup of
1198 / 610 = 1.96 over `c3-standard-22`.

- If the build scaled with physical cores, 11 x 1.96 = 21.6 cores would do, and
  the shape is `c3-standard-44`: 22 cores, 44 threads.
- It does not scale that well. The calibration measured a single build using
  about four fifths of this machine, since five cells at `-j7` finished in
  128.17 s what one at a time would have taken about 170 s, at round 1's 34
  to 35 s per configuration on this shape. At that efficiency
  `c3-standard-44` gives 1198 / (2 x 0.78) = 768 s, still above 610 s.
- `c3-standard-88`, 44 cores and 88 threads, clears the budget even at 60%
  efficiency: 1198 / (4 x 0.6) = 499 s.

The three small cases are not the constraint: 125.68 s of work that a
`t2d-standard-8` worker can absorb beside the large one.

So the capacity to request is `c3-standard-88` for the heavy cell plus
`t2d-standard-8` for the rest: `C3_CPUS` of at least 88 and `CPUS_ALL_REGIONS`
of at least 96, against the 24 and 32 this project holds. Nothing within the
present quota can pass alpha; the largest single machine it allows,
`c3-standard-22`, is 1.96x too slow for one configuration of it.

## The placement dispat cannot express

dispat has two placement classes and no per-worker pinning, and it places a
ready package on any free node without regard to speed. Under a 32 vCPU cap the
fleet is necessarily heterogeneous, because one group needs a machine fast
enough for its heaviest configuration and the rest of the budget buys something
smaller. The two classes were enough here only because each group needed exactly
two machines, and the class pinned to the machine that starts the release
happened to be the fast one.

What that hint is worth is round 1 against this round on the same two shapes:
its split hexagon sent allnoconfig and tinyconfig to the slow worker, 130 s of
script, and left the fast machine idle after 69 s, for 170.07 s against a 111 s
reference. Choosing the same placement by hand gives 92.22 s. The hint is worth
1.8x on exactly round 1's fleet, and it is what stands between this experiment
and a third machine: a `t2d-standard-8` added as a second worker today could
receive hexagon defconfig, which takes 147 s there, and lose the group.

A second thing the two classes cost is measurable in the m68k_nommu runs. The
worker finished its one configuration at +56 s and +66 s and then sat idle for
59 and 49 s while the orchestrator finished four. Balancing needs either a
per-worker hint or configurations whose cost is known in advance; the total work
is about 155 c3-seconds against a fleet of about 1.55 c3-machines, so a perfect
split would be near 100 s of build time against the 107 s measured.

## dispat behaviour worth reporting

- A worker still logs a rejected assignment for every snapshot branch, which the
  brief said this binary had fixed. Five such lines were logged, one per
  release:

      {"level":"warn","role":"worker","node":"w1","branch":"dispat-worker-w1-20260922-snapshot-da34d3d075473580370980852e4b7dd8","commit":"991c8c00f6e27b266d584788bddf0bd9d105c1c6","reason":"unreadable","code":"E226","category":"execution-authority","time":"2026-09-22T04:45:32Z","message":"assignment rejected"}

  They are the only warnings or errors a worker logged, and no run was harmed.

- A release needs a pushable `origin`, for the lock tag, before it will plan
  anything. Round 1 had one because it cloned the farm from a bundle. A
  repository built from the image-only export has none, and the release stops:

      {"level":"error", ... ,"error":"pushing the release lock tag to origin: git push origin 17015c3f21fa8c58acc42dfeefbad6b4615c0ead:refs/tags/dispat-release-lock: exit status 128: fatal: 'origin' does not appear to be a git repository ...","tag":"dispat-release-lock","remote":"origin","remedy":"another release may hold it; ...","message":"unable to create the release lock tag"}

  Source and coordination refs now share the mailbox repository, so `origin` is
  the mailbox.

- A package's `env` may not carry a key with the `DISPAT_` prefix:

      {"level":"error", ... ,"error":"config: package \"build-hexagon-allnoconfig\": env: key \"DISPAT_FARM_RESULTS\" uses the reserved DISPAT_ prefix","message":"package discovery failed"}

  `DISPAT_FARM_SOURCE_POOL` and `DISPAT_FARM_RESULTS` are therefore set in the
  environment of the worker and of the release, which is where they belong: they
  describe a node, not a cell.

- A release tags every package it completes even with `commit: {enabled: false}`
  and `github: {enabled: false}`, and a package whose content has not changed
  since its tag is not planned again. The second run of an unchanged
  configuration exited in 3.83 s having planned nothing
  ([`round2/par-c3/hexagon-2.time`](round2/par-c3/hexagon-2.time)). Repeated
  trials therefore start from [`reset-release-tags.sh`](reset-release-tags.sh),
  which removes the release tags and nothing else.

- Commits that touch no package are reported, one line each, as
  `W131 unit resolved to no package and is inert`. Expected, and noted because
  every release in this round carries two of them.

- The release states that it compares no records, which is correct for a run
  that pushes nothing: `release records are not compared: this run pushes
  nothing, so its own repository is its store`.

- The preflight probe costs 3 to 8 s of the elapsed time of every release and is
  the largest fixed overhead left. It is a poll round trip: the worker's back-off
  reaches 5 s while it is idle, and it is not configurable. In m68k_nommu trial 1
  the probe took 3 s and in trial 2 it took 8 s, which is most of the difference
  between two runs whose build work differed by more.

- `execution.concurrency` did not bound a release that names no worker. Two
  build slots started three cells and four started five, all at once. Such a
  release also emits no assignment, claim or probe at all, only
  `build started` and `build succeeded` per package.

- The worker redacts the user in the endpoint it logs
  (`ssh://REDACTED@10.128.0.8/...`).

## Cost

List-price estimate, not a billed figure: `c3-standard-22` at about USD 1.35 per
hour and `t2d-standard-8` at about USD 0.31 per hour, for 22 and 20 minutes of
calibration and 22 minutes each of parity, with four 100 GB balanced disks for
the same time, is about USD 1.25, and the single node's further 10 minutes about USD 0.23,
for a round of about USD 1.48.

## Limits

Two trials of one topology per group and one repetition of the same-hardware
pair, on one pair of machine shapes, in one region, on one kernel revision. The margins are 13 to 17% for hexagon and 10%
for m68k_nommu, which is more than the 3.7 s spread between the two hexagon trials
but not a claim about other groups. The 57-group matrix is untouched, no QEMU
target was run, and alpha was not attempted. distcc remains unmeasured and is
credited with nothing. All five VMs and their disks were deleted; the project
lists no instances and no disks.
