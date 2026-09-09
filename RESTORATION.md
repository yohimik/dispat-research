# Restoring the research environment

## Current campaign archives and paper drafts

Completed and failed release-campaign `work/` trees are preserved in their adjacent `work.tar.gz` archives, including fixture Git metadata. On 10 September the three extracted copies were removed only after archive checksums and every file's content matched. `provenance/cleanup-2026-09-10.json` records this verification; campaign manifests and observations were not changed.

To recompute the current campaign summary directly from its archive, run from the repository root:

```sh
python3 tools/summarize-saner-campaign.py experiments/saner-2027/campaign-1.10.0-20260909/runs/run-v1.10.0-linux-arm64-20260909
```

The tool checks the archive checksum, extracts into a temporary directory, and removes that temporary copy on completion. For manual inspection, check `ARCHIVE.json` and extract the archive into an empty disposable directory. Historical campaign documentation describes the state when evidence was collected; mentions of retained local `work/` trees predate cleanup.

The active manuscript is `paper/saner/`. See `paper/archives/README.md` to restore the obsolete ICSE draft for historical script replay. The separate technical report remains in `paper/main.tex`, with its saved PDF at `output/pdf/technical-report.pdf`. Build products and page previews can be regenerated; the current conference build and visual-review records are retained under `paper/saner/evidence/`.

`provenance/migration.json` and `tools/verify-migration.py` describe the original imported snapshot. The snapshot verifier is intended for that revision, not for validating later manuscript edits or cleanup.

## September 10 mechanism campaign

The separate [mechanism campaign](experiments/saner-2027/campaign-mechanisms-20260910/README.md) records the Docker runner, append-only execution commands, 140-case protocol, offline verifier, and archive restoration procedure. Its pilot and full run remain separate. Each run retains raw command records and a verified archive containing fixture working trees and Git metadata. Use a fresh run name or a disposable archive extraction; never overwrite completed evidence.

## Replay repositories

`python3 tools/restore-replay-fixtures.py` restores the external repositories under `experiments/e3a/repos/`, using the exact heads and tag object IDs in `experiments/fixture-locks/`. It refuses to overwrite existing checkouts. Network access and upstream availability are required; missing objects are errors, never replaced with newer revisions. The lock records the original sparse-checkout setting; the restoration uses a full checkout with the same content and revisions.

Generated fixture working files are retained. Nested `.git` directories and generated bare origins are stored in `provenance/generated-fixture-git.tar.gz` to prevent Git from treating them as submodules. To restore them in a disposable clone, inspect and extract that archive from the repository root. They contain synthetic histories and local origin paths; do not execute old publish commands against external destinations.

## September 9 Docker campaign

Build from the pinned Dockerfile and package lock:

```sh
cd experiments/saner-2027/campaign-20260909
docker build -t dispat-saner:research ./docker
```

The archived `docker/runner-image.json` identifies the image actually measured. A fresh build can have a different image ID even with identical packages. Before a new run, capture its identity into a *new run directory* rather than overwriting the archived measurement's metadata:

```sh
docker image inspect dispat-saner:research --format '{{json .}}' > NEW_RUN/docker/runner-image.json
```

Copy the campaign's `harness/`, Docker pins, `run-canonical.py`, `recovery-holdout.py`, and `mixed-docker/` scripts into that new directory; create empty `core/` and `recovery/` directories. Run `python3 NEW_RUN/run-canonical.py`. Preserve the resulting logs and compare them using the verifier. The driver requires Docker; it uses Linux containers with 2 CPUs and 4 GiB RAM. The mixed-chain experiment additionally mounts the Docker socket to create temporary local registries and BuildKit containers. Use a disposable Docker environment: socket access grants control over that daemon.

Base images, auxiliary registry images, BuildKit and Alpine packages are pinned. Network access is required to acquire them; the artifact does not promise that external registries or package mirrors retain them forever. npm registry and image-publish targets during the mixed experiment are disposable local registries, not public accounts.

The integration fixture is a separate runner in `integration/run.py`; its observations and verification are in `integration/results/`. Review `CAMPAIGN-STATUS.md` for completed checks and known setup failures before reusing the campaign.

## Historical campaigns

Read `experiments/README.md` and the campaign-specific scripts. They preserve the original Dispat versions, generators, acceptance restrictions, and container images. Do not substitute the newest CLI and label that run a reproduction of an older binary.

Third-party downloaded paper PDFs and regenerable caches are excluded. Citation metadata is retained under `output/saner-2027/research/`. The old curated artifact has its own verification script and hash manifest under `output/conference-submission-2026-09-09/artifact-draft/`.
