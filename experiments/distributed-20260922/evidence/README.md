# Distributed-execution evidence, 22 September 2026

Raw observations of the first measured runs of the CCME §28 distributed
execution profile: a Linux kernel build-farm parity experiment and an LLVM
dependent-build pair, both on Google Compute Engine. The measurements were
made by the Dispat product side on 22 September 2026 (UTC; the LLVM matrix pair
is dated 23 September in the specification entry because of the local
calendar). This directory holds unaltered copies of the logs, drivers,
receipts and reports, with `MANIFEST.json` recording every file's origin and
SHA-256. Nothing here was edited, and nothing was deleted at its source.

The reproduction kit for these experiments is being written in the parent
directory by the reproducibility session; its Docker recipe rebuilds the
pinned binaries. The specification's own record of both measurements is the
entry **2026-09-22: Distributed execution implemented** in
`specs/ccme-spec/DESIGN-HISTORY.md` of the product repository at commit
`e383de0e` (main `252216ba`, CCME `3.1.0-rc.2`). Quote it by path and commit;
the product repository is not copied here.

## What the measurements show, with the caveats that travel with every number

The stance written into the specification, preserved verbatim: **"No speedup
of the profile or of the engine is claimed beyond what these pairs measured."**

**Linux kernel, same-hardware pairs (round 2).** Kernel `v7.3-rc4` at
`93f51579`, fork `yohimik/linux-build-test` branch `codex/kernel-parity` at
`c699bf3d`, dispat built from `f0c9e959`. One `c3-standard-22` node (Xeon
Platinum 8481C, 11 cores) alone, then the same node plus one `t2d-standard-8`
worker (AMD EPYC Milan, 8 cores), same recipe and per-cell settings:

| Group | Alone | With the worker | Public farm reference |
|---|---:|---:|---:|
| hexagon (defconfig, tinyconfig, allnoconfig) | 122.62 s | 92.22 s and 95.89 s | 111 s |
| m68k_nommu (five cells) | 138.01 s | 115.48 s and 115.61 s | 128 s |

The single node ran once per group, so variability was not measured. The
worker is a slower machine of another family, so each pair is one node against
that node plus a second, slower one. The single-node m68k_nommu figure includes
58 to 66 s of source-lease contention on two of its cells (see
`source_lease_seconds` in the per-cell `result.json`); the same five cells
measured 128.17 s outside the engine. A paired release moved about 512 KB of
exported source and no build outputs. These pairs show placement of
independent cells on a second node; they do not exercise the transfer of
dependent outputs. The public reference times come from other hardware and
were deliberately left out of the specification entry; the fork's
`compare.py` gate accepted all four paired runs (same revision, compiler,
assembler and case lines, elapsed below the reference).

**Linux kernel, round 1 (Codex agent).** Every candidate failed the 1x gate on
elapsed time only: split hexagon 170.07 s, split m68k_nommu 159.03 s, batched
hexagon 165.30 s, batched m68k_nommu 196.23 s, against 111 s and 128 s. The
grouped control release took 1797.75 s with alpha's script alone at 1324 s
against a 623 s reference. Preserved as failed attempts; not pooled with
round 2.

**LLVM matrix pair.** Fork `yohimik/llvm-project` branch `dispat-gce` at
`6c1a5fcd` (recipe committed as `d8fb8408`, report as `952c2de4`), five
packages `24.0.0 -> 24.1.0`: `llvm` (X86) and `llvm-aarch64` from the same
sources, `lld` and `polly` consuming `llvm`'s outputs, and a `toolchain`
bundle on the orchestrator. `LLVM_FAST=1`, `LLVM_SKIP_CHECKS=1`, 14 build
jobs, 2 link jobs, uncompressed bundle. Ubuntu 24.04.5, g++ 13.3.0, cmake
3.28.3, ninja 1.11.1. GNU `time` from invocation to exit:

| | One `n2-custom-14` alone (attempt 8) | `e2-standard-4` orchestrator + two `n2-custom-14` workers (attempt 9) |
|---|---:|---:|
| `llvm` (X86) | 38:38, sharing the node | 22:08 on w1, including the 1.4 GB result push |
| `llvm-aarch64` | 38:51, sharing the node | 23:22 on w2 |
| `lld` + `polly` | 2:16 | 2:13 on the opposite workers, after `llvm`'s outputs reached them |
| bundle | 0:18 | 0:32 on the orchestrator |
| whole release | **41:12.02** | **27:48.94** |

Attempt 8 used dispat `f0c9e959`; attempt 9 used `1.11.0-rc.4+main.272772cb`.
One repetition per side, so variability is unmeasured; the distributed side had
two build nodes against one; the two heavy builds are one project for two
targets, a fair matrix but not two projects. `llvm`'s declared outputs, 1.4 GB
in 2647 files, were pushed once and fetched by two consumers and the
orchestrator. The bundle verified every provider's receipt against the
installed tree, so the transported bytes are what the workers built. The two
sides' products differ only in what the recipe embeds about its checkout
(compiled-in revision and build-id, repository string, RPATH and `__FILE__`
paths); `libLLVMCore.a` is byte-identical. Byte identity throughout needs
`LLVM_APPEND_VC_REV` off, a file prefix map and a relative RPATH, which this
recipe does not set.

**LLVM negative case (attempts 4 and 5).** One heavy package with two small
consumers: 26 min 47.69 s distributed against 20 min 16 s alone for `llvm`,
`lld`, `polly`, because moving a 1.4 GB install tree to consumers that build in
two minutes cannot pay for itself. This is the case §28.7 predicts.

**Discarded LLVM attempts, kept as failures.** Attempt 1: the fork's integrity
fingerprint hashed umask-dependent modes (fork fix `022f7284`). Attempt 2: the
bundle failed on an orchestrator without a C++ compiler (provisioning).
Attempt 3: the baseline clone lacked the `dispat/*/v24.0.0` tags. Attempt 6:
interrupted by the fixture change. Attempt 7: the bundle refused `polly`
because dispat captured outputs with `git add`, which applied polly's
`.gitattributes` text conversion and rewrote CRLF pairs inside three
libraries; a dispat defect, fixed on main at `9f649f88`. The worker-nodes
session records that its first diagnosis of attempt 4 (directory records) was
wrong: its byte-faithfulness check compared captured blobs with installed
files, never with built files. `pair4.out`'s compare after attempt 8 ran
against attempt 7's incomplete products; its NO PARITY line is meaningless.

**Coordination costs observed.** Probe 1 to 4 s; claim 3 to 6 s warm and about
37 s cold; result noticed within 5 s. A cold worker's first claim comes minutes
after a warm one's because its poll fetches the snapshot branch first (about
10 min for the 3.6 GB history). The first push of a repository's prepared state
to a mailbox sharing no objects carries the whole history (7.3 million objects
for LLVM, 17 to 20 min from a small orchestrator) and repeats per run unless
the mailbox is the origin. Placement is first-free, so a pool of unequal nodes
waits for its slowest.

## Layout

| Path | Contents | Origin |
|---|---|---|
| `llvm-gce/logs/` | 26 raw files: orchestrator `release-*.{log,start,time}` per attempt, cumulative `worker-lb-w{1,2}-dist*.log`, `polly-{local,dist}.records` | worker-nodes session scratchpad |
| `llvm-gce/drivers/` | the `llvm-*.sh` drivers, `pair4.out`, `gce-llvm-run*.txt`, `fp-records.py`, `rootconfig.py`, three fork patches | same |
| `llvm-gce/upstream-runs/` | helpers that listed public upstream workflow runs | same |
| `llvm-gce/fork-dispat-gce-952c2de4/` | `git archive` of `.ci/dispat` at `952c2de4`: `gce/REPORT.md`, `build.py`, `compare.py`, node and package configs, README, VALIDATION, readiness | llvm-project fork |
| `kernel-gce/first-run/` | the first real run (00:03 to 01:13 UTC, fork `dispat-prototype` `f7691276`): `gce-logs/release-run{1,2,3}.log`, worker logs and 20-second cell timelines, `gce-timings.py`, `forecast.py`, `guenter-v7.3-rc4.json`, `gce-cells.json` | worker-nodes session |
| `kernel-gce/kerneltests-scrapes/` | public kerneltests.org pages fetched 21 September for the reference farm | same |
| `kernel-gce/round2-raw/` | raw round-2 node captures (`evidence/{calibration,par-c3,par-t2d,solo-c3}` and their `.tgz`), `configure-round2.sh`, `configure-solo.sh`, `linux-parity-brief.md`, calibration plans, the harness export manifest | same |
| `kernel-gce/fork-codex-kernel-parity-c699bf3d/` | `git archive` of `dispat/` at `c699bf3d`: `gce/PARITY-20260922.md`, `gce/PARITY-20260922-round2.md`, `gce/REPORT.md`, `gce/parity-20260922-reference.json`, `gce/round2/` (curated results, `verdicts.txt`, `timing.txt`, per-cell `result.json`), the harness and its tests | linux-build-test fork |
| `kernel-gce/round1-codex/` | `curated-linux-parity-evidence.tar.gz` (145 members, SHA-256 `2fcc02ec…`), its sums file and `baseline.json`, unaltered | ChatGPT/Codex agent run at `~/.codex/artifacts/linux-parity-20260922/` |
| `product-gates/` | the gate briefs given to the review agents, sharded integration-suite logs and summaries per commit, TinyGo gate runs, coverage shard logs, the release-candidate final report draft | worker-nodes session |
| `product-gates/coverage/` | per-function coverage summaries of the 94.0 % integration-only measurement | `/tmp/dispat-cov-*` |
| `spec-validation/` | `mindiam.py`, `relation.py`, `proceed.py` (brute-force checks behind the §13.11 and §19.2a text), the stale-tag republish reproduction before and after the fix (tarred with nested Git metadata) | validation session and worker-nodes session |

## Binaries

No experiment binary is stored here. `MANIFEST.json` records the hashes:

| Binary | SHA-256 | Used for |
|---|---|---|
| `f0c9e959`, unstamped, static linux/amd64 | `63441cc66f68d07b5efbf9a42edd5559304d153d48b82b1dfb037349e20606ed` | kernel round 2, LLVM attempts 1 to 8; rebuilds byte-identically |
| `272772cb`, stamped `1.11.0-rc.4+main.272772cb`, as deployed | `feba0210d13c90fa…` (full hash in the manifest) | LLVM attempt 9; built in a dirty checkout, so not byte-reproducible |
| `272772cb`, stamped, clean rebuild | `46bc2cf821dd57479c27bf2a4b7eee63b69e01db6f18fbd6e663ad66e6812ba8` | differs from the deployed one only by Go's `vcs.modified` stamp |
| kernel round-1 binary (Codex agent) | `a7172a7feb21e27ce882050120b9e04df1e6d4b4ee5f3341ab8a99ba155ba70a` | matches the hash stated in `PARITY-20260922.md` |

## Not copied, and why

Listed with hashes in `MANIFEST.json` under `not_copied`: the 22 MB public
upstream GitHub Actions job log, Go coverage profiles and counters, the
binaries above, the 1.4 GB kernel Git bundle and other working copies, the
Codex run's files outside its curated archive, and the worker-nodes session's
development fixtures. Never read and never copied: the HMAC execution secrets
and ssh private keys of the deleted machines (`/tmp/dispat-gce/secret.txt`,
`/tmp/dispat-gce/mailbox_key`, and the Codex run's `mailbox_key` and
`secret.env`). Mailbox URLs in the logs are redacted at the source as
`ssh://REDACTED@10.128.0.9/…`; the driver scripts read the secret from a file
at run time and contain no literal value. The narrative ledger of the
worker-nodes session is at `~/.claude/plans/buzzing-marinating-cat.md` and is
cited, not copied. The product repository stays where it is.

## Verification

`MANIFEST.json` was produced by copying with `shutil.copy2` and hashing both
sides; the Codex tarball was extracted into a temporary directory and all 145
members matched `EVIDENCE-SHA256SUMS.txt`, which also matches the copy outside
the tarball. A pattern scan of every copied text file found no private key,
token or literal secret. To recheck the copies:

```sh
python3 - <<'EOF'
import hashlib, json, pathlib
root = pathlib.Path('.')
m = json.load(open('experiments/distributed-20260922/evidence/MANIFEST.json'))
bad = [e['path'] for e in m['files'] if hashlib.sha256((root / e['path']).read_bytes()).hexdigest() != e['sha256']]
print('mismatches:', bad)
EOF
```

These are integrity checks on the copies. They do not replicate the
experiments, and structural agreement with the reports is not independent
scientific validation. The reproduction kit in the parent directory is the
route to a new run; a new run gets a new directory, never an edit here.
