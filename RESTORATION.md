# Restoring the research environment

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
