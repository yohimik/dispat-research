# CCME distributed task and release execution

21 September 2026. Specification proposal for integration by the Dispat product
agent; not an implementation or experimental result. No parser change is
proposed. The full technical report remains unchanged until implementation.

Integration status: completed by the product owner in canonical SPEC.md §28,
with nine subsections and 26 unexecuted conformance cases. This file retains
the research proposal; the integrated canonical text includes further precision.
See `paper/saner/ADAPTATION-2026-09-21.md` and
`output/saner-2027/distributed-execution-20260921/spec-integration.json` for
the final snapshot and validation boundaries.

Reviewed source: `/Users/yohimik/Projects/dispat/specs/ccme-spec/SPEC.md`, stamped
`3.1.0-rc.1`, product HEAD `784a4971dfc3936be824469b6a7156383ebb7534`, working-file
SHA-256 `0a752f0edd5449989b0b572180abd787c386be30fb1d3d4b05084ba5546acde7`.
The stamp alone does not identify this uncommitted snapshot. A copy is retained
in `output/saner-2027/distributed-execution-20260921/SPEC-before.md`.

## Integration map

Add optional §28, **Distributed task and release execution**, independently of
the three history-selection modes in §27. Add it to the contents, summary,
implementation boundary, configuration and conformance sections. Update §27.11's
CI-entry paragraph to distinguish a repository peer from an execution node:
any peer can supply the entry checkout, but a node configured as a worker cannot
initiate a release. Preserve repository ownership, ancestry and evidence rules.
In §§27.2 and 27.7, distinguish isolated worker transport commits from admitted
native release/settlement commits and preserve serialized publication/recording
within each owner. Add diagnostic categories without inventing conflicting
numeric codes. Keep examples explicitly prospective, not current CLI syntax.

The following is proposed normative text. MUST, SHOULD and MAY retain the
specification's existing meanings.

## 28. Distributed task and release execution

### 28.1 Scope and roles

An execution node is a machine or runner executing the same release engine and
configuration schema. It is distinct from a repository peer. One repository
may have work on several nodes; one node may work on several repositories.

Every node MUST support both roles. The default role is **orchestrator**; an
explicit **worker** role MUST refuse release initiation, including indirect
initiation from a delegated hook. A worker executes authorized tasks in an
existing run and MUST NOT create a second plan, acquire competing release
ownership, dispatch to another pool, or independently finalize a release.
An orchestrator-capable node MAY accept delegated tasks; for that assignment it
has only worker authority. Role changes MUST NOT transfer a live run's ownership.

The node on which CI starts is the run's orchestrator. It owns repository lock
acquisition, the fixed planning input, task allocation, result admission, and
release finalization. It MAY execute tasks locally under the same rules.
There is one orchestrator per run, not a permanent leader of the repositories.

Workers MAY be added to **every history mode**: single history (including a
large monorepo), specified histories, or discovered histories. They MUST NOT
require a control repository, a particular peer topology, or polyrepo activation.
Worker endpoint links are execution links, not Git submodule/fleet links, and
MUST NOT alter source discovery, repository identity or release scope.

### 28.2 Configuration and concurrency

The same configuration format MUST serve both roles. Node settings select the
role (default orchestrator) and execution concurrency. Orchestrators additionally
list worker-node links. A worker needs no worker-specific release graph, package
policy, version rules or workflow; it receives the run's resolved configuration.
Transport credentials and node authentication are deployment prerequisites,
not a second release-policy format.

Worker concurrency is a positive local upper bound on simultaneous assigned
tasks. Effective capacity is the intersection of that bound and the run's
existing stage limits and resource exclusions. Existing build/publish limits
MUST be respected across the whole run, not multiplied by the number of workers.
The implementation MUST define which task classes consume each limit. Shared
workspace writes MUST serialize or use separate task worktrees.

The orchestrator MUST validate the effective configuration, protocol/toolchain
compatibility and output-transfer capability before dispatch. Worker-local
settings MUST NOT override package policy, planned versions, commands or inputs.
An empty worker list preserves local execution. Malformed links, an invalid
role or nonpositive concurrency MUST be configuration errors. Concrete key
spellings and transport selection belong to the integrating product spec.

### 28.3 Lock, snapshot, plan, assign

Before creating a write-capable run, the orchestrator MUST identify every
participating repository, including any control repository, and acquire all
release locks in one stable total order. It MUST verify ownership before
planning or dispatch; failure releases acquired locks in reverse order and
dispatches no write-capable task. It MUST revalidate discovery under those
locks; a changed participant set requires reacquisition, not silent expansion.
Distributed release execution MUST refuse an unsafe lock bypass. Read-only
planning remains lock-free and does not dispatch side effects.

Let `I` be the fixed repository heads and release records, graph, effective
configuration and explicit release options. The semantic release plan is the
pure function `P = Plan(I)`. Worker count, placement, completion order,
wall-clock time and transport branch names MUST NOT change `P`. Native records
and peer settlement retain their narrowly defined admission under §27; they
do not authorize replacing the original planning input with an arbitrary ref.

The orchestrator derives a task DAG from `P`, including required preparation,
tests, builds, transfers, publications and recording gates. A task can be placed
only on a compatible node and only when its exact prerequisites are available.
Independent ready tasks MAY run concurrently. The assignment schedule need not
be deterministic; selected packages, versions, commands and dependency semantics
MUST remain those of the same fixed plan.

Shared manifest/lockfile reconciliation MUST be an explicit preparation task
before the affected builds fan out, producing one admitted prepared input state.
Workers MUST NOT each regenerate and race to merge a workspace-wide lockfile
as an implicit part of otherwise independent package builds. A later required
shared mutation creates a new dependency gate and invalidates affected outputs;
it MUST NOT force all builds in the repository onto one node when their prepared
inputs and output write sets allow independent execution.

Each assignment MUST identify the run, plan digest, task, attempt, ownership
generation, repository-qualified source object IDs, effective configuration,
toolchain/platform requirements, input receipts, permitted writes and outputs.
Duplicate delivery MUST be recognized. Only one attempt may be authorized to
perform a given external side effect; an uncertain previous attempt is reconciled
before another is authorized. A task receipt is execution evidence, never a
package release record.

### 28.4 Git synchronization branches

The orchestrator MUST provision isolated task worktrees and temporary branches
named `worker-<date>-<random>`, with a collision-resistant random suffix and
atomic creation. The date is a diagnostic label only. A branch is bound to one
run, repository and task attempt; parallel attempts MUST NOT share a mutable
branch. The manifest, rather than the branch name, identifies node and task.

Workers synchronize declared source changes and result manifests through these
branches. Each acknowledged checkpoint MUST identify an exact full object ID;
consumers fetch that object and validate its manifest rather than following a
moving branch tip. Ref updates MUST check the expected previous object ID.
Where concurrency permits several tasks at once, use separate branches/worktrees
and admit their results independently as their dependencies become ready.
Concurrency one still supports the same protocol in sequence.

Transport commits MUST NOT be treated as release intent, a pending-window
boundary, a successful release, or a §27 native-head admission. They MUST NOT
be merged wholesale into a release branch or made ancestors of release tags.
The orchestrator validates declared changes against the task's exact base and
write set, detects overlapping/conflicting writes, and admits only authorized
release-file changes through the ordinary native release transaction. Build
outputs remain transport data. Hooks needing to change release-relevant inputs
beyond the admitted writes require a new plan under the existing rules.

A package's recorded source revision MUST match the source and admitted release
files actually used for its artifact. Integrating one task MUST NOT silently
alter another task's inputs; overlapping writes require explicit ordering,
revalidation and rebuilding when necessary. This is not an automatic merge
policy for arbitrary generated files.

### 28.5 Dependent build outputs are first-class inputs

**Source synchronization alone is insufficient.** A provider's Git revision or
worker branch does not make its ignored/untracked `dist` files, generated
types, assets or package bundle available to a consumer on another machine.
A conforming implementation MUST transport the outputs needed by a local-output
dependency, including declared ignored/generated files. It MUST NOT satisfy
distributed execution merely by recloning sources and rebuilding the provider
closure on every consumer node, or by pinning the entire connected JS graph
to one worker.

A successful build MUST emit a manifest binding its outputs to the run, plan,
task and attempt, repository-qualified source revision, admitted release-file
state, target package/version, toolchain and platform, and input/output digests.
Required metadata includes relative paths, file types, modes and link targets
where relevant. The transfer MUST preserve the package's required layout while
rejecting paths or links escaping the destination. Consumers MUST verify the
manifest, content integrity and compatibility before their stage becomes ready.
Missing, stale, incomplete or incompatible outputs fail that prerequisite;
they MUST NOT be silently substituted with registry contents or a new build
under a different input.

Required output bytes MUST be available through the temporary Git transport
branch (for example a task result tree containing explicitly added outputs),
or through immutable content-addressed bundles whose references and digests are
in that branch. Such bundle transfer is a transient data service, not an
additional authoritative release-state database. References alone are not a
transfer: every receiving node MUST be able to retrieve and verify the bytes.
If no bundle service is configured, Git transport MUST still support the
declared outputs. Ordinary source checkout rules ignoring build output MUST
NOT exclude it from the output manifest.

On the receiving node the engine materializes the consumer's pinned source,
applies its admitted release-file state, restores the provider outputs, and
links/installs them according to the declared workspace integration. The
integration MUST prevent an install lifecycle from rebuilding already supplied
providers implicitly. A raw `node_modules` copy is neither required nor a
portable default; native outputs require compatible platforms/toolchains.
Task inputs MUST include all required build dependencies, including dependencies
whose packages need no new release. Required preparation tasks do not create
new release obligations or change `P`.

For a local-output edge `A -> B`, readiness is:

`build(A) -> export(A) -> verify/materialize(A at B's node) -> build(B)`.

For a registry-availability edge, readiness still requires the provider's
publication and all applicable recording gates; transferring local bytes MUST
NOT replace that condition. Transfers to different ready consumers MAY overlap
and identical immutable blobs SHOULD be reused. Implementations SHOULD retain
incremental Git objects and verified outputs between assignments, but any cache
MUST be dispensable and validated against the complete input identity.

### 28.6 Publication, recording and recovery

Build, test and publish commands MAY execute on workers. Repository ownership
does not change: publication uses the owning package's checkout and policy.
The orchestrator alone admits results and authorizes publication after all
ordinary test, dependency, settlement and relevant-input checks. It serializes
publication and recording within one owner as §27.2 requires; isolated builds
within that owner may still run concurrently. Independent owners retain allowed
publication concurrency. A worker MUST NOT independently move release branches,
create release tags, settle peer links or finalize the fleet. The orchestrator
performs those native transactions under the existing ownership/locking rules.

The orchestrator MUST retain and verify lock ownership for the lifetime of all
authorized effects. Assignments and results are bound to its ownership
generation; stale results cannot authorize publication or native recording.
After lock loss, no new effect may start. A timed-out worker is not proof its
publisher stopped: cancellation must be acknowledged, a fencing mechanism must
be enforced where the effect occurs, or the outcome must be reconciled before
ownership is safely handed over. A generation field alone does not fence an
arbitrary registry command. No automatic takeover may simply expire ownership
and republish while the previous process can still act.

If a worker fails before publication, retry eligible computation under a new
attempt without discharging the package. If publication may have succeeded,
use §19.4 identity reconciliation or a safely repeatable publisher before a
new attempt; neither a missing reply nor a missing tag proves failure. Only the
ordinary durable source release record discharges the release obligation.
Preserve prior successes, block affected dependents, and continue unrelated
safe work under the ordinary failure rules. Worker completion order does not
alter the consumer-owned release boundaries.

Fresh invocations reconstruct pending releases from authoritative repository
records. Verified task outputs MAY be reused when their full input identity
still matches, but loss of a worker, branch, bundle or cache cannot erase
pending work or successful release records. Synchronization state is not a
second recovery ledger. Cleanup removes only owned temporary refs and bundles,
after all consumers and uncertain operations are settled. Failed attempts and
receipts retain diagnostic provenance. Cleanup failure is reported without
rewriting successful package outcomes; borrowed nodes' unrelated data is never
deleted. Repository locks are released only after authorized operations have
quiesced or been safely fenced, then in reverse acquisition order.

### 28.7 Required example and performance boundary

In one large JS repository, let `assets -> {ui, docs} -> app` be local build
dependencies. Worker A builds `assets` once and exports its required outputs.
Workers B and C receive verified outputs and build `ui` and `docs` concurrently.
The assigned app worker receives both output sets and builds `app`. Publication
and source recording then obey the existing stage/owner constraints; an isolated
registry-based image consumer still waits for image publication when required.
Neither B nor C rebuilds `assets`, and the app worker does not rebuild their
closures. This example MUST work without converting the monorepo to a polyrepo
or publishing private intermediate JS packages solely for transport.

The required gain is actual distribution and reuse of dependent builds with
parallel ready branches, including large local JS workspaces. Git provides
source/result transport; it does not itself schedule tasks, transfer omitted
build products, guarantee compatible environments, or make effects exactly-once.
A strictly serial dependency chain retains its critical path. Transfer and
setup overhead can outweigh saved compute on small jobs, so universal speedup
is not a semantic guarantee. Before making an implementation performance claim,
compare the same pinned large-JS fixture locally and on multiple nodes, including
cold/warm setup, transfer bytes/time, task execution counts, total work, wall
time and artifact equivalence. Require demonstrated wall-time benefit on a
declared representative parallel fixture; do not call source-only dispatch or
duplicate prerequisite compilation a distributed-build success.

### 28.8 Conformance vectors (specification cases, not executed results)

1. No role or worker list: local orchestrator behavior remains unchanged.
2. A worker receives direct or nested release initiation: refuse before locks
   or side effects. An orchestrator-capable node accepts a delegated task with
   worker authority and does not initiate another run.
3. Add workers independently to each of the three history modes: same fixed
   inputs produce identical package/version plans and source owners.
4. Two CI entry nodes target overlapping repository sets: at most one acquires
   the complete lock set and dispatches effects; failure releases its partial
   set. An unsafe lock bypass refuses distributed execution.
5. Vary worker count, date, randomness and completion order: `Plan(I)` is
   unchanged. Concurrency limits hold locally and across the run.
6. Two ready tasks share a repository: use isolated worktrees and branches;
   conflicting declared release-file writes are detected before admission.
7. Branch tips move after dispatch or a stale receipt arrives: use only the
   assigned full object ID and matching plan/attempt/ownership generation.
8. Ignored JS outputs from `assets` reach `ui` and `docs` on separate workers:
   both builds use those bytes, overlap when ready and never rebuild `assets`.
   The app consumes both output sets without rebuilding either provider.
9. An unselected provider is needed by a selected consumer: supply or prepare
   its verified output without adding a package release to the semantic plan.
10. An output is absent, corrupt, incompatible, or path-escaping: fail the
    prerequisite before consumer execution; preserve its release obligation.
11. A registry-based consumer has local provider bytes but no required
    publication/record: remain blocked. Local transport does not weaken the edge.
12. A worker's Git transport commit is fetched: no new intent, release baseline,
    tag, or admitted native head arises. Temporary commits stay outside release
    ancestry; only validated release-file changes enter native recording.
13. A worker publishes and its reply is lost: reconcile artifact identity before
    reauthorization; never infer a failed publish from the timeout.
14. A worker disconnects or the orchestrator loses its lock with an in-flight
    publisher: no new effects, no unsafe handover, no unfenced duplicate attempt.
15. A source tag succeeds and later checkpoint/cleanup fails: preserve source
    success and report the specific failure; no source republication for cleanup.
16. Delete temporary branches/caches after a completed run and replan unchanged
    inputs: release debt remains discharged by source records. Delete them after
    a prepublication failure: unfinished work remains discoverable and rebuildable.
17. Repeat the JS fixture without a separate bundle service: branch-backed
    transport still carries every declared build output.
18. Shared JS manifest/lockfile preparation happens once before fan-out; workers
    consume the same admitted prepared state without competing lockfile writes.
19. Independent builds in one repository overlap, but its publication/recording
    transactions serialize; cross-owner publication remains dependency-safe.

## Abstract and report boundary

The conference abstract presents this as a proposed distributed execution
profile, including local-output transfer, while retaining the measured recovery
results and their single-history boundary. Only the abstract changes in the
manuscript; the body, proofs, results, bibliography and full technical report
are not rewritten. No current benchmark establishes distributed speedup. Broader
report revision and new evidence follow implementation with a pinned campaign.
