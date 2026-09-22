# Reproducing the two parity experiments of 2026-09-22

This kit reproduces, on the same machine shapes and from the same pinned
sources, the two measurements the CCME 3.1.0 release candidate records for its
distributed execution profile (`specs/ccme-spec/DESIGN-HISTORY.md`, entry
"2026-09-22: Distributed execution implemented"):

- the **Linux kernel farm parity** of `yohimik/linux-build-test` (branch
  `codex/kernel-parity`, `c699bf3d`, report `dispat/gce/PARITY-20260922-round2.md`):
  two groups of the kerneltests.org image matrix (`hexagon`, `m68k_nommu`) built
  on a `c3-standard-22` that starts the release plus a `t2d-standard-8` worker,
  against the public reference times, twice each, and once on the `c3-standard-22`
  alone (the same-hardware pair);
- the **LLVM matrix pair** of `yohimik/llvm-project` (branch `dispat-gce`,
  `952c2de4`, report `.ci/dispat/gce/REPORT.md`, attempts 8 and 9): five packages
  (`llvm` for X86, `llvm-aarch64` from the same sources, `lld` and `polly`
  consuming `llvm`'s outputs, and a bundle) released once through two
  `n2-custom-14-49152` workers from an `e2-standard-4` orchestrator, and once by
  the same recipe on one such worker alone, with the products compared.

Docker pins every environment (base image by digest, packages from the Ubuntu
archive snapshot of the measurement day, cross toolchains by checksum, the
`dispat` binary rebuilt from its commit); Terraform creates the machines, the
network, the keys and the signing secret; two runbooks drive the runs over ssh,
collect every log and result, and judge them with the forks' own oracles. The
raw evidence of the original runs sits in [`evidence/`](evidence/) (maintained by
the research session; see its `README.md` and `MANIFEST.json`). Every identity
this kit depends on is listed in [`pins.json`](pins.json).

What this kit does **not** do: it does not claim a speedup. The original pairs
were one repetition per side; a rerun is another repetition on the same shapes,
and the honest comparison is the one `compare.py` makes on each fork.

## Layout

| Path | Purpose |
|---|---|
| `docker/dispat/Dockerfile` | Rebuilds the experiment binary from a pinned commit; byte-identical to the deployed binaries (see below). |
| `docker/kernel-node/Dockerfile` | A kernel farm node: Ubuntu 24.04 (digest), the apt snapshot of 2026-09-22, kernel.org crosstool 16.2.0 (alpha, m68k), Ubuntu clang 18.1.3, `node-prepare` and `node-identity`. |
| `docker/llvm-node/Dockerfile` | An LLVM node: the same base and snapshot, g++ 13.3, cmake 3.28.3, ninja 1.11.1. |
| `terraform/modules/gce-node` | One VM with a bounded lifetime that deletes itself. |
| `terraform/kernel`, `terraform/llvm` | The two fleets, networks, firewall rules, keys and secret. |
| `scripts/kernel/run.sh`, `scripts/kernel/prepare-farm.sh` | The kernel runbook, from a bare fleet to `verdicts.txt`. |
| `scripts/llvm/run.sh`, `scripts/llvm/prepare-llvm.sh`, `scripts/llvm/prepare-llvm-baseline.sh` | The LLVM runbook, from a bare fleet to `compare.txt`. |
| `scripts/*/node-startup.sh` | What a VM does at boot: Docker, the two images built from the Dockerfiles in its metadata, the `node-run` helper, the ready marker. |
| `local/kernel-compose.yaml`, `local/kernel-smoke.sh` | A laptop-sized end-to-end check of the kernel pipeline with two containers and a shared mailbox. |
| `runs/` | Where the runbooks write their evidence (ignored by git until reviewed). |

## The binary, verified

The two binaries the measurements used were built by hand on 2026-09-22 with
`go1.26.5`, `CGO_ENABLED=0`, `-trimpath` and `-buildvcs=false`, from
`services/dispat` inside the repository's `go.work` workspace. The Dockerfile
under `docker/dispat` repeats that recipe from a pinned commit and a
digest-pinned `golang:1.26.5-alpine`, on any host platform (Go builds are
reproducible across hosts for a fixed toolchain and flags). On 2026-09-22 it
reproduced all three hashes byte for byte:

| Commit | Stamp | SHA-256 | Used by |
|---|---|---|---|
| `f0c9e959` | none | `63441cc66f68d07b5efbf9a42edd5559304d153d48b82b1dfb037349e20606ed` | kernel round 2 (as deployed) |
| `272772cb` | `1.11.0-rc.4+main.272772cb` | `46bc2cf821dd57479c27bf2a4b7eee63b69e01db6f18fbd6e663ad66e6812ba8` | LLVM matrix pair (the deployed copy, `feba0210…`, was built in a checkout with uncommitted files and differs by Go's `vcs.modified` stamp only) |
| `272772cb` | none | `f1dec45d48df4d7fe5a681f5244ce946d71e140ccfbe97c2f8f3a6842f69b196` | reference |

```sh
cd docker/dispat
docker buildx build --platform linux/amd64 \
  --build-arg DISPAT_COMMIT=272772cb62a874289e97c5efbfab1a5c33b03efc \
  --build-arg 'DISPAT_VERSION=1.11.0-rc.4+main.272772cb' \
  --output type=local,dest=out .
cat out/dispat.sha256 out/dispat.buildinfo
```

When `1.11.0-rc.4` is released, its Linux asset is the release Dockerfile's build
of whatever commit was dispatched, stamped `1.11.0-rc.4`: verify it with
`dispat --version` and `go version -m`, do not expect any hash above.

## Prerequisites

On the operator machine: Docker with BuildKit (Docker Desktop 4.x or `docker.io`
with buildx), Terraform 1.6 or newer, the Google Cloud SDK authenticated for the
target project, `jq`, `ssh`, `rsync`, `python3`, `git`. Terraform needs
credentials; either `gcloud auth application-default login` once, or for a
single shell:

```sh
export GOOGLE_OAUTH_ACCESS_TOKEN=$(gcloud auth print-access-token)
```

Quotas that must exist in the project's region (`us-central1`): kernel, 30
vCPUs at once (`C3_CPUS` 22, `T2D_CPUS` 8; the solo node adds 22 more, run it
after the pair or raise the quota); LLVM, 32 vCPUs (`N2_CPUS` 28, `E2_CPUS` 4).
The original projects were `dispat-linux-parity` and `dispat`.

Cost, at on-demand list prices of September 2026, is a few dollars per experiment:
the kernel pair lives about 25 minutes, the LLVM fleet about 100 minutes.

## Kernel farm parity

```sh
cd terraform/kernel
terraform init
terraform apply -var project=dispat-linux-parity          # add -var solo=true for the same-hardware pair
../../scripts/kernel/run.sh
terraform destroy -var project=dispat-linux-parity
```

`apply` creates the network, two (or three) VMs, an operator key, a mailbox key
and the run's signing secret (under `terraform/kernel/.secrets/`, ignored by
git). Each VM's startup script installs Docker, builds `dispat-experiment:pinned`
and `dispat-kernel-node:pinned` from the Dockerfiles carried in its metadata,
prepares a bare cache of `v7.3-rc4` and five pristine source trees under
`/srv/farm`, records its toolchain identities and marks itself ready; about ten
minutes.

`run.sh` then, exactly as `dispat/gce/orchestrator-round2.sh`, `worker.sh`,
`release-group.sh` and `reset-release-tags.sh` of the fork did:

1. exports the image-only farm harness on the orchestrator
   (`dispat/export-build-harness.py`), regenerates the four round-2
   configurations with the flags that reproduce the retained
   `dispat/gce/round2/{par-c3,solo-c3}/*.yaml` byte for byte (only the mailbox
   path differs), commits the harness as `feat(kernel)^^: test v7.3-rc4` and
   pushes it to the bare mailbox `~/mailbox.git`;
2. starts `dispat worker` on the `t2d-standard-8` (one slot, the mailbox over
   ssh with the mailbox key);
3. runs `dispat release` for `hexagon` twice and `m68k_nommu` twice under GNU
   `time`, deleting the release tags between trials so every trial plans the same
   cells, moving each trial's cell evidence aside;
4. on the solo node, when present, the same two groups once each with the
   `--no-workers` configurations;
5. copies every release log, `time` record, `result.json`, worker log, startup
   log and identity file into `runs/kernel-<utc>/`, and judges every trial with
   the fork's `dispat/compare.py` against `dispat/gce/parity-20260922-reference.json`
   into `verdicts.txt`.

Expected on the original shapes: `accepted: true` for the paired trials
(2026-09-22: `hexagon` 95.89 s and 92.22 s against 111 s, `m68k_nommu` 115.61 s
and 115.48 s against 128 s), `accepted: false` on elapsed time alone for the solo
node (122.62 s, 138.01 s). Every run must show the same revision
`93f51579…`, the same compiler and assembler identities and the same case
lines; a run that differs there is not a reproduction, whatever its time.

## LLVM matrix pair

```sh
cd terraform/llvm
terraform init
terraform apply -var project=dispat
../../scripts/llvm/run.sh
terraform destroy -var project=dispat
```

The startup script builds `dispat-llvm-node:pinned` on each VM. `run.sh` then,
as `.ci/dispat/gce/orchestrator.sh` and `worker.sh` of the fork did:

1. on the orchestrator, clones the fork branch in full, tags the baselines
   `dispat/<package>/v24.0.0` at the LLVM main commit `a9f4d3ff` (so the window
   holds the fork's own commits), adds the trigger commit
   `feat(llvm)^^: time a distributed build on Compute Engine workers`, makes the
   bare `~/origin.git` that is both the release's origin and the workers'
   mailbox, and fills `dispat.gce.yaml` and `dispat.local.yaml` from their
   templates;
2. on each worker, writes the node file (`w1`, `w2`, one slot, the transfer
   limits of the report), seeds the worker's object cache from the mailbox so
   that sources are warm as they were in attempts 8 and 9, and starts
   `dispat worker`;
3. runs the distributed release on the orchestrator under GNU `time`
   (`dispat.gce.yaml`: `llvm` and `llvm-aarch64` on the two workers, `lld` and
   `polly` after `llvm`'s outputs reach them, the bundle on the orchestrator);
4. stops the worker on `w2`, clones the orchestrator's origin there at the same
   trigger commit with only the baseline tags, and runs the same recipe alone
   (`dispat.local.yaml`, two build slots) under GNU `time`;
5. copies the orchestrator's product trees to `w2` and runs
   `.ci/dispat/gce/compare.py` over both checkouts;
6. copies both `time` records, all logs, the plans, the receipts
   (`build-info.json`) and identities into `runs/llvm-<utc>/`.

Expected on the original shapes: exit 0 on both sides with five packages
published; on 2026-09-22 the distributed release took 27:48.94 against 41:12.02
alone. `compare.py` prints `NO PARITY` and lists differences of exactly the
reproducible-builds kind (the compiled-in revision and build-id, the repository
string, RPATH and source paths; `libLLVMCore.a` byte-identical); the recipe
does not set `-DLLVM_APPEND_VC_REV=OFF`, `-ffile-prefix-map` or a relative RPATH,
so byte identity is not expected. The receipts the workers wrote are verified
against the installed trees by the bundle step itself; that check, not the
comparison, is what says the transport was faithful.

The fork's report also records the single-heavy fixture (one `llvm` with two
small consumers) as the negative case the specification predicts: 26:47
distributed against 20:16 alone for three packages. This kit runs the matrix
fixture; the single-heavy configuration is the report's attempts 4 and 5 and
needs the recipe of fork commit `fbc4dcf8`, which is not on the branch.

## Checking the pipeline without a cloud project

```sh
cd docker/dispat && docker buildx build --platform linux/arm64 \
  --build-arg 'DISPAT_VERSION=1.11.0-rc.4+main.272772cb' --target export --load \
  -t dispat-experiment:272772cb-arm64 . && cd ..
docker buildx build --platform linux/arm64 --build-arg DISPAT_IMAGE=dispat-experiment:272772cb-arm64 \
  --load -t dispat-kernel-node:272772cb-arm64 -f kernel-node/Dockerfile kernel-node
cd ../local
docker compose -f kernel-compose.yaml up -d
./kernel-smoke.sh
docker compose -f kernel-compose.yaml down -v
```

Two containers, one shared mailbox directory, the same harness and generated
configurations: the `hexagon` group runs end to end and `compare.py` judges it.
The revision, case lines and toolchain identities must be accepted; the
elapsed time is whatever the machine gives and says nothing about parity. (Use
`linux/amd64` on an x86 host; the kernel.org crosstool exists for both.)

Run on 22 September 2026 on an Apple silicon workstation (15 CPUs, arm64
images): the worker built `allnoconfig` (37 s of script), the orchestrator
`defconfig` and `tinyconfig` (53 s and 49 s), the release exited 0, and
`compare.py` accepted the run with three cases at 63.47 s elapsed
(`runs/local-kernel-20260922T184954Z/verdict.json`, kept as the record of the
pipeline check).

## What differs from the original runs, and why it does not matter

- The original nodes ran the toolchains directly on the VM; here they run in a
  container on the VM, which pins the packages to a dated archive snapshot. A
  CPU-bound build in a container on host networking has no measurable overhead.
- The original VMs were created from the image family `ubuntu-2404-lts-amd64`
  by hand with `gcloud`; here the exact image that family resolved to on
  2026-09-22 is named, and Terraform creates the same shapes, zones, disk sizes
  and lifetimes.
- The mailbox key and the signing secret were generated by hand; here
  Terraform generates them, and they never leave `.secrets/` except into the
  nodes' environment and `~/.ssh`.
- The LLVM workers were warm because earlier attempts had fetched the mailbox's
  objects; here the worker's object cache is seeded before the timed run (the
  cache path follows `services/dispat/internal/execution/state.go`). Set
  `PREWARM=0` for the cold case the report also describes (a first claim minutes
  late while the worker fetches history).

## Evidence of the original runs

See [`evidence/README.md`](evidence/README.md) and
[`evidence/MANIFEST.json`](evidence/MANIFEST.json): the raw release and worker
logs of both fleets, the forks' trees at their pinned commits, the round-1
archive, the public reference pages, and a cross-check of every headline number
against its raw file.
