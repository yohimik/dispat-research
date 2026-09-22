# dispat setup for this LLVM fork

**Prepared, not activated.** Native distributed builds and releases cannot run
with a published dispat binary yet. The latest published CCME specification is
[3.1.0-rc.2, section 28](https://github.com/yohimik/dispat/blob/specs/ccme-spec/v3.1.0-rc.2/specs/ccme-spec/SPEC.md#28-distributed-task-and-release-execution).
The specification still describes that profile as unimplemented. Its contents
match the inspected upstream revision
[`fb555ecf`](https://github.com/yohimik/dispat/blob/fb555ecf723f4a64598680d477ed4cc81e919bdf/specs/ccme-spec/SPEC.md).

The adjacent development checkout `../dispat-worker-nodes` at
`dc60b5bf54de6fc90e5f4e2f71a673f86c03c92f` defines the additional `buildOutputs`,
`buildPlatforms`, Git mailbox, timeout and transfer keys used here. These are
**development implementation settings**, not extra normative CCME keys or a
published stable CLI contract. That checkout had in-progress changes when
inspected; its worker answers preflight probes, but does not execute builds.
Neither that checkout nor dispat's source was changed for this setup.

`readiness.json` records the blockers. `build.py release-ready` refuses
unconditionally, and is called both by the release workflow and by the native
release's gating hook. Standalone artifact export has the same gate. A `ready`
field, environment variable or successful worker probe cannot enable publication.

## Package and task graph

```text
LLVM SDK build + check-llvm + install
                   |
           verified SDK outputs
              /          \
     Clang standalone    LLD standalone
       check-clang         check-lld
              \          /
             toolchain bundle
                   |
         GitHub assets + native records
```

The four packages share the complete `llvm-release` version. Two build tasks may
run concurrently across the whole run; publication is serialized. Each example
worker accepts one command task at a time. CMake compilation has a separate
`LLVM_BUILD_JOBS` limit (default 4) and `LLVM_LINK_JOBS` limit (default 1).

This initial distribution includes LLVM development libraries/tools, Clang, and
LLD, with X86 code generation by default. It is a host-compiler Release build
with assertions, without bootstrap, PGO or LTO. It does **not** include LLDB,
Flang, MLIR, clang-tools-extra, compiler-rt, libc++ or other runtimes. Those need
additional reviewed build recipes and prerequisite edges. This is a fork SDK
distribution, not LLVM's official full release process.

The SDK installs generated headers, CMake exports, TableGen, testing utilities
and GoogleTest. Consumers configure their own standalone source directory with
the restored `LLVM_DIR`; they never invoke an LLVM source build. A missing,
modified, wrong-version or incompatible SDK fails the consumer. Tests must pass
before installation and before a success receipt is written. Bundle assembly
rejects conflicting files and preserves relative symlinks and executable modes.

## Files

| File | Purpose |
| --- | --- |
| `dispat.yaml` | Published dispat 1.10-compatible local policy and release graph |
| `dispat.distributed.yaml` | Experimental node settings and declared output paths |
| `.ci/dispat/packages/*.yaml` | Shared package policy, referenced by both profiles |
| `.ci/dispat/nodes/worker-{a,b}.yaml` | Startup-only worker configuration, without release policy |
| `.ci/dispat/build.py` | CMake recipes, integrity checks, assembly and gated asset export |
| `.github/workflows/dispat.yml` | PR validation and a gated manual release job |

All generated build trees, installed products and local tools are ignored.
Provider outputs live in `<package>/_dispat/install` and
`<package>/_dispat/build-info.json`. The final archive, checksum and metadata
live in `.ci/dispat/bundle/_dispat/dist`.

## Validate and build locally

Use Python 3.9 or newer, CMake 3.31 or newer, Ninja, a C++17-capable compiler
supported by this LLVM revision, and Git. The setup was checked with dispat
1.10.0. Matching agent guidance is
[1.10.3](https://github.com/yohimik/dispat/blob/specs/agent-guide/v1.10.3/specs/agent-guide/README.md);
the latest published documentation patch on that line is 1.10.14.

From the LLVM checkout:

```sh
python3 -m venv .ci/dispat/.venv
.ci/dispat/.venv/bin/python -m pip install -r .ci/dispat/requirements.txt
# If CMake and Ninja are absent, install them in this same disposable environment.
.ci/dispat/.venv/bin/python -m pip install cmake ninja
export PATH="$PWD/.ci/dispat/.venv/bin:$PATH"
dispat exec validate --in root

# Configuration only: no compiler build, tags, remote writes or publication.
export LLVM_BUILD_VERSION=24.0.0-rc.0
dispat exec configure --for pkg:llvm --in pkg:llvm
```

Actual builds require committed tracked source changes, a fresh task output
directory and sufficient LLVM build resources. They run the full package test
targets and can take substantial time and disk space. The source is pinned by
its real Git commit. For a local build after committing this setup:

```sh
export LLVM_BUILD_VERSION=24.0.0-rc.0
export LLVM_BUILD_JOBS=4 LLVM_LINK_JOBS=1 LLVM_TARGETS_TO_BUILD=X86
dispat run build --since all
```

`run build --since all` uses dispat's local dependency scheduler and produces
artifacts only. It does not simulate remote scheduling and is not evidence of
CCME section 28 conformance. For another native architecture, choose appropriate
LLVM targets and keep that setting identical throughout the entire build.

If inputs change after configuration, remove only the affected package's
generated `_dispat` directory before starting a new build. An existing install
tree is deliberately refused to avoid stale files leaking into a new release.

## Release intent and history

The clone retains full commit history (with Git's partial blob transfer). CI
releases require full history and tags; never use a shallow release checkout.
Own tags use `dispat/{name}/v{version}` and do not reinterpret or overwrite
upstream's `llvmorg-*` releases. Only the `toolchain` package requests a GitHub
release in `yohimik/llvm-project`; the other packages retain native release tags.
Commit/push recording is enabled so dispat retains control of native records.

Most LLVM history is not CCME-authored. Configuration does not convert old
messages into release intent. When ready to start this fork's release line, a
pair of reviewed CCME commits, in this order, can explicitly start the group:

```text
chore(llvm,clang,lld,toolchain): clear inherited pending metadata

Deletes: *
```

```text
release(llvm): start fork toolchain releases

Release-As: 24.0.0-rc.0

---

release(clang): start fork toolchain releases

Release-As: 24.0.0-rc.0

---

release(lld): start fork toolchain releases

Release-As: 24.0.0-rc.0

---

release(toolchain): start fork toolchain releases

Release-As: 24.0.0-rc.0
```

`Deletes: *` deliberately discards accumulated pending release metadata for the
addressed group, not Git history or source changes. A `release` unit cannot carry
that correction footer, so the reset and release request are separate commits.
An exact `Release-As` accepts one package per unit; the second commit therefore
has four units, each entering the same prerelease version and channel.
This exact sequence is tested in a disposable fixture. No such commits or
baseline tags were created here.
Review the real plan before using it; the first scan has no fork-owned tag
boundary and must inspect LLVM's large history. `initials: 23.0.0` provides only
the numeric seed needed for CCME's default one-major exact-version advance limit
to accept the first 24.0.0 candidate. It does not claim this fork published 23.0.0,
create a release record, or establish a history boundary.

For subsequent work use scopes such as `fix(clang)` or `feat(llvm)`. Changes in
shared inputs such as `cmake/`, `third-party/`, the root config or these scripts
must explicitly name a package, for example `fix(llvm): update shared CMake
inputs`; the fixed group then moves all four packages. Group names are CLI
selectors, not package names in commit scopes. These shared paths are outside the
three source packages. An exact `Release-As` controls upstream version alignment.
The recipe refuses a release major that disagrees with `LLVMVersion.cmake`.

## Provisioning and activation checklist

The example deployment is one Linux/amd64 orchestrator and two Linux/amd64
workers with the same compiler, CMake, Ninja, libc/SDK, build environment and
target selection. Merely matching `linux/amd64` does not establish ABI
compatibility. Pin a common machine or container image when provisioning.

1. Finish and pin a dispat engine implementing the section 28 task scheduler,
   authenticated assignments, isolated task worktrees, verified output transfer,
   restoration, capacity accounting, fencing, reconciliation and cleanup. A
   version string or existence of the `worker` command is insufficient.
2. Replace the `.invalid` mailbox URLs in the orchestrator and matching worker
   settings. Use private Git storage able to transfer the declared LLVM output
   sizes. The examples are not GitHub repositories: ordinary GitHub blob size
   limits are unsuitable for large SDK archives. Do not place secrets in URLs.
3. Supply `LLVM_DISPAT_EXECUTION_SECRET` outside version control. Give workers
   source-read and mailbox-write credentials; native release branch/tag writes
   belong to the orchestrator. Provision the source/object transport and access
   needed by every consumer, not just references to unavailable bytes.
4. Run the same pinned engine on both workers using their node configuration and
   separate durable state directories. The development CLI shape is:

   ```sh
   /opt/dispat/bin/dispat worker --config /etc/dispat/worker-a.yaml \
     --state-dir /var/lib/dispat/llvm-a
   ```

   This currently serves probes only. Worker startup needs no package graph;
   assignments carry the orchestrator's resolved policy.
5. Implement and test the output integration contract below on the actual engine
   and deployment. Require a complete LLVM SDK -> parallel consumers -> bundle
   build, package test passes, missing/corrupt output failures and recovery from
   lost publication acknowledgement. No full LLVM build was executed here.
6. Pin that engine at `/opt/dispat/bin/dispat`, replace example endpoints in the
   reviewed config, provision the self-hosted `dispat-orchestrator` runner and
   `dispat-release` GitHub environment, and its signing secret. Validate remote
   lock and branch permissions. Leave unsafe locking bypasses disabled.
7. Replace the unconditional readiness refusal with a reviewed capability and
   deployment check only after the conformance evidence exists. Preserve its
   use in CI, the native release hook and artifact export. Dispatch the workflow
   on the intended `main` or `release/*` revision with `release: true`. The
   workflow checks the exact dispatched SHA and runs status, then native release.

Do not replace the gate with a local shell release or manually create tags and
GitHub assets. No workflow was dispatched and nothing was pushed or published
during setup.

## Output integration contract for the future engine

- Maintain one source repository and one native `dispat-release-lock`; execution
  workers do not make LLVM a polyrepo. Lock before semantic planning and any
  write-capable task. Worker placement must not change versions or release intent.
- Materialize one fixed source revision and admitted release-file state per
  isolated task. This recipe passes planned versions through CMake flags instead
  of racing to rewrite the shared `LLVMVersion.cmake` file.
- Export ignored `buildOutputs` with relative layout, content hashes, modes and
  symlink targets. Restore provider paths in the consumer's pinned checkout
  before calling its recipe, with no partial visibility. Never ship the CMake
  build tree as the installed SDK and never rebuild the SDK on consumer nodes.
- Apply the normative run/plan/task/attempt/ownership binding and authentication
  to engine output manifests. The recipe's `build-info.json` checks are additional
  local integrity checks, **not** engine receipts, authorization or release records.
- Use owned `worker-<UTC date>-<128-bit random>` transport branches and exact
  checkpoint OIDs. Keep transport commits out of release history and tags.
  Git must carry the actual bytes or verified content-addressed bundles, not
  merely a checksum. No separate bundle service is assumed by these configs.
- Bounds are 250,000 files, 64 GiB uncompressed outputs and 128 MiB manifest per
  task, with 2-hour transfers and 24-hour commands. These are deployment ceilings,
  not measured LLVM requirements. Every node must accept the declared limits.
- Retain original provenance and issue new current-run admission when reusing
  outputs. Unselected providers remain build prerequisites. Serialize native
  publication/recording, retain exclusion after uncertain effects and reconcile
  before retry. Ordinary source records remain the only release authority.
- The final `.tar.xz`, `SHA256SUMS` and `build-info.json` are exported through
  `DISPAT_OUTPUT` for the native GitHub recorder. Archives at or above 2 GiB are
  refused; add reviewed splitting if the actual distribution needs it.

No distributed performance benefit or full CCME conformance is claimed by this
setup. Demonstrate actual SDK reuse and concurrent Clang/LLD work on separate
machines before describing it as an operational distributed build.
