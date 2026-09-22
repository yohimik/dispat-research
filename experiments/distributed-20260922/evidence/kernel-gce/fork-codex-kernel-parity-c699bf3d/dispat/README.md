# The upstream matrix as a dispat run

A prototype, on the branch `dispat-prototype` of a fork. It describes the builders of the `master` branch to
[dispat](https://github.com/yohimik/dispat) and runs the farm's scripts. The original
measurements below used stand-in scripts. The subsequent real kernel run is in
[`gce/REPORT.md`](gce/REPORT.md); the current parity requirements and audit are in
[`PARITY.md`](PARITY.md). The compiler-matched grouped/split/batched measurements
are in [`gce/PARITY-20260922.md`](gce/PARITY-20260922.md); none met the 1x time gate.

## What is here

| File | What it is |
|------|------------|
| `dispat.yaml` | The run: 58 packages, generated. One `kernel` package naming the revision under test, 26 `build-<arch>` packages and 31 `qemu-<target>` packages that depend on it. |
| `dispat/generate.py` | Writes `dispat.yaml` from the two lists copied out of `master/master.cfg` (`stable_arches`, `qemu_targets_master`). `--workers` and `--mailbox` name another pool. |
| `dispat/kernel/ref.env` | The kernel repository, ref and branch one run tests. |
| `dispat/run-cell.sh` | The build stage of every cell. Checks the revision out of a per-machine bare clone into a worktree of its own, then calls `stable-build-arch.sh <arch> <branch>` or `run-qemu-<target>.sh`, and counts the `Building ... passed/failed/skipped` lines the way `master/shellcommands.py` counts them. |
| `dispat/build/<arch>/cell` | A folder per image build group, because a package is a folder. The qemu cells use the folders `rootfs/<target>` already is. |
| `bin/stable-build-arch.sh` | Isolated output/log paths, optional single-configuration selection, and explicit compiler/job settings for controlled comparisons. Existing defaults remain available. |
| `dispat/export-build-harness.py` | Exports image-build scripts and inputs with checksums, without QEMU assets or Git history. |
| `dispat/compare.py` | Accepts a measured run only if cases, revision, tools and total elapsed time match its reference. |

## How a run works

1. Change `dispat/kernel/ref.env` in a commit of its own, `feat(kernel)^^: test v7.3-rc4`. The `^^` carries the change
   to every package that depends on `kernel`, so all 57 cells enter the plan.
2. On the machine that coordinates, with `DISPAT_EXECUTION_SECRET` set: `dispat release --config dispat.yaml`.
3. On every build machine, a file naming that machine (`execution.name`), the mailbox and the same secret, then
   `dispat worker --root <folder> --idle-timeout 0`. A worker polls the repository over Git. It needs no
   inbound port. The measured engine's idle timer can expire during a long build, so this experiment uses a
   separate VM lifetime limit and explicit cleanup instead.
4. Every cell is placed on whichever listed machine has a free slot (`runOnly: worker`: the coordinating machine spends
   no slot). A cell that passed is tagged (`qemu-arm@0.0.1`) and drops out of the next run. A cell that failed stays a
   candidate, so running the same command again repeats the failures and nothing else.

## What was measured

A dry run on one laptop: two workers with two slots each, a local bare repository as the mailbox, stand-in scripts that
print two result lines and sleep two seconds, a one-commit repository standing in for the kernel.

- The plan is 58 packages from the one commit, and the run ends with exit code 0, 58 tags and an empty mailbox.
- The 57 cells were shared 29 to 28 between the two workers.
- From assignment to reported result a cell took 9 seconds on average (8 to 21), of which about 2 were the stand-in
  script. The rest is coordination and the per-task checkout of this repository, whose working tree is 1.9 GB of root
  file systems. Against cells that take one to eighty minutes that is under one percent.
- The whole run took 147 seconds for 57 cells on four slots.

## What is not measured, and what Guenter's reply changed

The first reading of the v7.3-rc4 build pages treated a machine's two concurrent builders as two slots of capacity and
concluded that free placement alone would halve the run. That was wrong. The machines are fully used by two parallel
builds or three qemu runs, so the step times on the pages were measured under that sharing and more slots add nothing.
What the pages do show is idle time between builders: the six machines were busy 138 to 231 minutes of a 232 minute
run, 1079 machine-minutes in all. Perfect balance at the same step durations would be about 180 minutes. The honest
range for better placement on the same hardware is therefore 180 to 232 minutes, and only more machines move it
further.

Turnaround is not the constraint either. The farm starts at midnight because of the price of electricity, and the
work is the same number of kilowatt-hours however it is scheduled. What a different scheduler can offer this farm is
smaller than speed:

- placement that is not tied to a builder-to-machine assignment nobody intended;
- a run that ends, and machines that can sleep when it does, instead of a master and six slaves that idle at 300 to
  400 W;
- reruns that repeat only what failed;
- one configuration file generated from the same lists, instead of a buildbot version that can no longer be upgraded.

## What does not fit yet

- **Results.** `results.py` classifies build and QEMU output using the farm's patterns,
  exports counts (including KUnit totals), and rejects failed, empty, unrecognized or
  skipped-only cells even when the script exits zero. Logs and JSON results survive
  worktree cleanup under `~/.local/state/dispat-farm/results`, overridable with
  `DISPAT_FARM_RESULTS`. They still need collection before a worker VM is deleted.
  There is no results page. Run the adapter checks with
  `python3 -m unittest discover -s dispat -p 'test_*.py'`.
- **One image build per machine, several qemu runs.** buildbot expresses that with an exclusive and a counting lock.
  A dispat worker has one number, `execution.concurrency`, and every task counts as one. With the build folder now per
  cell two image builds can share a machine, which is what `concurrency: 2` means here. It is an approximation.
- **One qemu target per machine at a time** came from the single qemu checkout per builder directory. Each cell has a
  kernel worktree of its own here, so the rule is gone, at the price of a worktree per cell.
- **dispat is a release tool.** A test run is modelled as a release: every cell gets a version and a tag per run, 58
  tags each time. A scheduler for work that releases nothing (`dispat run` across worker nodes) does not exist yet and
  would be the better fit.
- **Only `master`.** The stable branches, `next`, `pending-fixes`, the hwmon branches and the smatch builders are not
  described. The per-branch skip lists of `master.cfg` would become one generated file per branch.
- **Source transport.** A full farm snapshot includes large QEMU assets even for image-only tasks. The image-only
  export below avoids that payload. Source and task refs can share one Git repository; a separate mailbox repository
  is optional. Reducing the source payload and reusing objects are the performance changes, not the repository count.
- **`git describe` and `git branch`.** The scripts name a build from the checkout. The worktree is detached, so the
  branch is passed as an argument, which `stable-build-arch.sh` accepts and the qemu scripts have not been checked for.

## Configuration-level image cells

The default still schedules one architecture group per task. Within that task,
`stable-build-arch.sh` runs its configuration array sequentially. Independent
architecture tasks have no declared order; an available worker takes a task.

For experiments with finer scheduling, generate a separate configuration:

```sh
python3 dispat/generate.py --arches alpha,hexagon,m68k_nommu --qemu '' \
  --split-configs --jobs 11 > dispat.split.yaml
```

This creates 12 image packages from the exact arrays in
`bin/stable-build-targets.sh`. Splitting all 26 image groups produces 166 packages
before branch-specific skips. QEMU groups are unchanged. Each image package names
its architecture and one configuration, uses its own kernel worktree/output
directory, and runs the original fixups and skip policy. Shared kernel-cache
updates are serialized. The optional third argument to `stable-build-arch.sh`
selects one configuration or a comma-separated subset. Subsets execute in the
architecture's original order and share the invocation's output directory.
Unknown, duplicate and malformed selectors are rejected. For example, a package
with `FARM_ARCH=hexagon` and `FARM_CONFIG=allnoconfig,tinyconfig` retains reuse
between those two builds. The generator's `--split-configs` still produces
individual configurations; grouping is an explicit experiment configuration.

`--jobs` sets `FARM_BUILD_JOBS` per cell; it does not set worker concurrency or
reserve CPUs. For example, two active cells with 11 jobs each budget 22 compile
jobs across a 22-vCPU host. `FARM_GCC_CURRENT` can pin the current-branch compiler
directory suffix to match a reference farm; the default remains unchanged.

`FARM_DISTCC=1` is an optional GCC cross-compiler launcher for experiments with
distributed compilation. It requires a separately configured distcc installation
and matching compilers on its servers. Only target compilation is wrapped;
configuration probes, compiler identity checks and binutils remain unchanged.
LLVM and host `tools/perf` builds reject this option. Unsupported distcc jobs can
fall back locally, so inspect remote-job statistics before attributing a gain to
distributed compilation. This option is not a measured speedup by itself.

The source script reuses its output directory between configurations in a group.
Splitting loses some of that reuse and adds checkouts and dispatches, so it is an
experimental option, not a claimed speedup. Compare complete case lists and total
elapsed time against the grouped control. Use `--no-write-cells` to preview a
configuration without creating its package directories.

## Image-only source export

```sh
python3 dispat/export-build-harness.py /absolute/path/to/new-harness
```

The destination must not exist. The export copies the current build inputs and
records each file's SHA-256 alongside the original source commit. Initialize it
as an independent Git checkout and generate its matrix with `--qemu ''` before
dispatching. Its origin may also be the workers' dispatch endpoint: source
branches, release tags and task refs have distinct names.

This is an image-build experiment package. QEMU tests still need their rootfs
assets. Do not use an image-only result to claim coverage or timing parity for
the complete farm matrix. Record source preparation and cold kernel downloads
separately from repeated runs with prepared source caches; neither implies a
compiler cache or a previously built kernel.

`run-cell.sh` records kernel-fetch, kernel-checkout and cache-lock timings as
well as script time. Use the whole orchestrator run duration for acceptance,
including transfer, dispatch, reporting and cleanup. Given a retained baseline
JSON and the exact result files from one architecture run:

```sh
python3 dispat/compare.py --baseline baseline.json --arch hexagon \
  --elapsed 100.25 results/hexagon-*/result.json
```

The comparison rejects missing or duplicated configurations, changed compiler
or assembler identities, a different kernel revision, unsuccessful cells, and
elapsed time greater than the reference. The elapsed value must come from the
run's measured wall clock; summing worker script times is not equivalent.
