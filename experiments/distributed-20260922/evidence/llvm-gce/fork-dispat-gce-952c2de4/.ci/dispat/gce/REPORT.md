# LLVM parity pair on Compute Engine, 2026-09-22

The question this experiment answers is narrow: does a dispat release of the
fork's own recipe, with its build stages delegated to worker nodes, produce the
same products as the same release on one machine, and does it take no longer.
It makes no claim about LLVM's upstream release process, and the recipe is the
40-minute fixture below, not the fork's full recipe with the check targets.

## Fixture

- Fork commit: `fbc4dcf8` on the orchestrator (`022f7284` locally; same tree),
  branch `dispat-gce`, LLVM main at `a9f4d3ff` (24.0.0git).
- Packages: `llvm`, `lld`, `polly` (standalone builds against the installed
  `llvm`, `runOnly: worker`) and `toolchain` (the bundle of the three install
  trees, `runOnly: orchestrator`). Baselines `dispat/<pkg>/v24.0.0` tagged at
  `a9f4d3ff`, so every plan is `24.0.0 -> 24.1.0` for all four.
- Recipe (`.ci/dispat/build.py`): `LLVM_FAST=1` (assertions, examples, docs and
  benchmarks off), `LLVM_SKIP_CHECKS=1` (no `check-*` targets), X86 only,
  `LLVM_BUILD_JOBS=14`, `LLVM_LINK_JOBS=2`, `LLVM_TOOLCHAIN_PROVIDERS=llvm,lld,polly`.
- Configurations: `dispat.gce.yaml` (two workers, mailbox = the orchestrator's
  own bare `origin.git`, so a snapshot push shares its objects) and
  `dispat.local.yaml` (the same recipe with no `execution` object). Both are
  untracked files at the repository root and travel in the snapshot.
- Comparison: `.ci/dispat/gce/compare.py <baseline checkout> <distributed checkout>`
  compares the four install trees file by file with the install prefix masked
  (build.py embeds it) and the toolchain archive by member list.

## Machines

| Node | Shape | Role |
|---|---|---|
| `lb-orch` | e2-standard-4, 80 GB | orchestrator: locks, plan, snapshots, authorizations, records, the `toolchain` build |
| `lb-w1` | n2-custom-14-49152 (7 cores, 14 threads), 150 GB | worker `w1` |
| `lb-w2` | n2-custom-14-49152, 150 GB | worker `w2`; the single-node baseline ran here |

Project `dispat`, zone us-central1-a, on-demand, `--max-run-duration 8h`. All
three carry Ubuntu 24.04.5 with g++ 13.3.0, cmake 3.28.3, ninja 1.11.1 and the
dispat binary built from the feature branch at `f0c9e959` (static linux/amd64).

## Attempts

| # | When (UTC) | What happened |
|---|---|---|
| 1 | 03:54-04:38 | `llvm` built and published through `w1`; `lld` and `polly` refused `llvm`'s transported install tree: the recipe's integrity fingerprint hashed full file and directory modes, which are the creating process's umask (the worker built directories 0775; dispat installs files as 0644 or 0755 and recreates directories). Discarded; the fingerprint now records the executable bit and link targets only. |
| 2 | 04:40-05:07 | `llvm`, `lld` and `polly` built and published through the workers in 27 min 21 s; the `toolchain` bundle on the orchestrator failed at once because that machine had no C++ compiler for the recipe's identity record. Discarded; a provisioning omission. |
| 3 (baseline) | 05:20-05:21 | The clone of `origin.git` on `w2` had no `dispat/*/v24.0.0` tags (they existed only in the orchestrator's checkout), so the plan started from the initials and the recipe refused the major. Discarded; the tags were pushed to `origin.git`. |
| 4 | 05:45-06:12 | Distributed run, 26 min 47.69 s wall (`/usr/bin/time`): `llvm` on `w1` 05:45:38 -> 06:07:49, `llvm:publish` on `w1` 06:08:17 -> 06:08:29, `lld` on `w2` 06:07:52 -> 06:09:58, `polly` on `w1` 06:08:31 -> 06:10:50, both published; the `toolchain` bundle on the orchestrator refused `polly`'s transported tree (`llvm` and `lld` passed). Under diagnosis against the baseline's own `polly` tree. |
| 5 (baseline) | 06:13-06:49 | The same recipe on `w2` alone: **36 min 9.09 s** wall, exit 0, four packages published. `llvm` 06:13:08 -> 06:31:11 (18:03), `lld` and `polly` in parallel 06:31:11 -> 06:33:24, the `toolchain` bundle 06:33:24 -> 06:49:17 (15:53, single-threaded xz). |
| 6 | 06:51-07:14 | Distributed again with the recipe at `2b03be6a` (fingerprint bookkeeping only: directories left out, the records kept in the receipt so a mismatch names them). Interrupted when the fixture changed to the matrix below. |
| 7 | 07:16-07:45 | The matrix, distributed: **28 min 45.63 s** wall, `llvm` on `w1` 07:17:03 -> 07:39:26 (22:23) and `llvm-aarch64` on `w2` -> 07:40:09 (23:06) in parallel, `lld` and `polly` -> 07:43:28, four packages published; the bundle refused `polly` once more, and the records the receipt now carries named the three libraries. Diagnosis: polly's `.gitattributes` marks its tree as text, and dispat captured outputs with `git add`, which rewrote every CRLF pair inside the binaries. A dispat bug, fixed on main (outputs are hashed with no filter and the index is filled by hand). |
| 8 (baseline) | 07:46-08:27 | The matrix on `w2` alone with the same recipe: **41 min 12.02 s** wall, exit 0, five packages published. `llvm` and `llvm-aarch64` shared the node from 07:46:34 to 08:25:12 and 08:25:25 (38:38 and 38:51), `lld` and `polly` -> 08:27:14 and 08:27:28, the bundle 08:27:28 -> 08:27:46. |
| 9 | 08:29- | The matrix, distributed, with the fixed dispat (`1.11.0-rc.4+main.272772cb`). Results below. |

Attempt 4's `polly` refusal was diagnosed before attempt 6: every one of the 124
entries `w1` captured (result commit `88271aa3`) is byte- and mode-identical to
the file the orchestrator installed, `llvm`'s and `lld`'s transported trees pass
the same recipe check on the orchestrator, and `w2`'s own `polly` passes its
receipt; the transport was faithful and the receipt `w1` wrote did not describe
the tree `w1` then captured. The directory records were the one part of the
fingerprint a file transport cannot reproduce, so they were removed and the
records kept.

## The matrix fixture (attempt 7)

The single-heavy-build fixture above cannot show a distributed release at or
below the single-node time whatever the transport does: one package holds
nine tenths of the work and its two consumers are small. The owner's target
for the release candidate is a fixture that does, honestly, so the fixture
became a matrix the single node has to serialize and a pool does not:

- `llvm` (X86) and `llvm-aarch64` (the same sources with
  `LLVM_TARGETS_TO_BUILD=AArch64`, products under `.ci/dispat/llvm-aarch64/_dispat`),
  two heavy builds that depend on nothing;
- `lld` and `polly` against the X86 `llvm`;
- the `toolchain` bundle with `LLVM_BUNDLE_COMPRESSION=none` on both sides (a
  single-threaded xz of the whole install tree was a 16-minute serial step on
  either side and says nothing about placement), built and published on the
  orchestrator's own checkout with no declared outputs (so nothing of the
  1.85 GB tar is captured).

Fork commit `d8fb8408` (`feat(llvm-aarch64): build the AArch64 target as a
package of the matrix`), the same recipe and per-package settings on both
sides; the baseline runs it on `w2` alone with its two build slots, the
distributed run with `w1` and `w2` as workers and the bundle on `lb-orch`.
Results below.

## Results

### The matrix (attempts 8 and 9)

| | Baseline, `w2` alone | Distributed, `w1` + `w2` + `lb-orch` |
|---|---:|---:|
| `llvm` (X86) | 38:38, sharing the node | 22:08 on `w1`, including the 1.4 GB result push |
| `llvm-aarch64` | 38:51, sharing the node | 23:22 on `w2`, including its result push |
| `lld` + `polly` | 2:16 | 2:13 on the two workers, after `llvm`'s outputs reached them |
| bundle (uncompressed tar) | 0:18 | 0:32 on `lb-orch` |
| whole release, GNU `time` | **41:12.02** | **27:48.94** |

Five packages published on both sides, exit 0 on both, the same recipe and the same per-package settings
(`LLVM_BUILD_JOBS=14`, `LLVM_LINK_JOBS=2`, `LLVM_FAST=1`, `LLVM_SKIP_CHECKS=1`, `LLVM_BUNDLE_COMPRESSION=none`).
The distributed release took 67.5% of the single node's time: the two heavy builds ran on two machines
instead of sharing one, and the transfer of `llvm`'s install tree (1.4 GB into the mailbox, then into two
consumers' checkouts and the orchestrator's) cost less than the sharing did. One repetition per side; the
distributed side had been measured once before with the same placement and timings within a minute
(attempt 7, 28:45 to the same point plus a bundle that failed on the dispat defect below).

### Products

The bundle on the orchestrator passed the recipe's own integrity check for every provider it merged: the
receipt each worker wrote describes the tree the orchestrator installed, file by file, so the transport is
byte-faithful (attempt 7's failure was dispat applying the checkout's `.gitattributes` to captured outputs, fixed
before attempt 9). `compare.py` then finds the two sides differ in bytes, and every difference it finds is of
the reproducible-builds kind rather than a transport one:

- every tool of equal size (`llc`, `lli`, `llvm-ar`, `llvm-cov`, ...) differs first at its `.note.gnu.build-id`
  and then only in the compiled-in VCS revision: LLVM embeds the checkout's commit (`VCSRevision.h`: `6c1a5fcd`
  on the single node, the snapshot commit `dbc1e8a7` on a worker, which builds from the prepared input state
  rather than from the trigger commit) and the build id is a hash over that content;
- `llvm-config` and `lld` also embed the repository string, which differs in length between the two checkouts;
- `LLVMPolly.so`, `libPolly.a`, `libPollyISL.a` and `liblldCommon.a` differ by a few kilobytes: the RPATH and the
  `__FILE__` strings carry the checkout's absolute path, which is longer on a worker;
- `libLLVMCore.a`, which embeds neither, is byte-identical.

Byte identity across the two sides is therefore a recipe matter: `-DLLVM_APPEND_VC_REV=OFF`,
`-ffile-prefix-map=<checkout>=/src` and a relative RPATH would make the products identical wherever they are
built. The fixture did not set them, so the claim this pair supports is: the same five products, built by the
same recipe on two placements, verified by the recipe's own receipts, differing only in the revision, build-id
and path strings the recipe chooses to embed.

### The single-heavy fixture (attempts 4 and 5), for the record

| | Baseline (`w2` alone) | Distributed (attempt 4) |
|---|---:|---:|
| `llvm` build | 18:03 | 22:11 on `w1`, including the 1.4 GB result push |
| `lld` + `polly` | 2:13 (parallel) | 2:07 / 2:19 on `w2` / `w1` (parallel) |
| `llvm`, `lld`, `polly` published | 20:16 | 26:47 |
| `toolchain` bundle (xz) | 15:53 | not reached |
| whole release | 36:09 | (bundle failed on the orchestrator's missing compiler) |

With one package holding nine tenths of the work, distribution cannot win: the transfer of `llvm`'s install
tree and the consumers' installs cost about six and a half minutes that two small consumers cannot pay back.
The matrix above is the fixture that says what the profile is for.

## What the pair measured about dispat

- A cold worker's first claim comes minutes after a warm one's: the node's
  poll fetches the snapshot branch before it can read the assignment (about
  10 minutes for the 3.6 GB history on a cold cache; 6 s warm).
- Coordination is cheap beside the builds: probe 1-4 s, claim 3-6 s warm,
  result noticed within 5 s, authorization to publish command 8-12 s.
- A result carrying outputs (1.4 GB for `llvm`) reports under
  `execution.transfer.timeout`; the fixed 30 s report bound of the earlier
  binary killed that push (fixed in dispat before this pair).
- Placement is first-free; the pair's workers are equal, so nothing here says
  what an unequal pool would do (the kernel farm experiment does).
