# Prepared SANER campaign for the next Dispat release

Status: **frozen and prepared, not executed**. This campaign targets published Dispat 1.9.0 on Linux ARM64. `release-lock.json` records the identities measured from the published artifact and the locally built pinned runner. Do not replace them with a branch, tag, dev binary, or prior campaign.

This is a new campaign and a separate population from `campaign-20260909`. It freezes the same protocol: parser and golden gates; core profile seeds 90001–90300 with all 300 declared cases; recovery episodes for both graph sizes, both failure probabilities, and seeds 100–104 (20 total); six repetitions of all five mixed-chain configurations (30 total); and three CI integration repetitions. Expected failed publications, the missing-barrier control, retries, invalid cases, and rejected cases are evidence. Do not remove or selectively rerun them to improve an outcome. The feature under release does not by itself alter any theorem or justify pooling results.

## Release lock and runner

After the release coordinator supplies the official values, copy `release-lock.example.json` to an untracked candidate file and fill in:

- the exact `dispat_version` printed by the released binary;
- the exact final `dispat --version` line in `dispat_version_output`;
- an immutable `repository@sha256:...` release-image reference;
- the SHA-256 of `/usr/local/bin/dispat` in that image;
- the immutable local image ID of the runner built below;
- runner OS `linux` and architecture `arm64`.

Measure the published artifact itself:

```sh
docker pull 'REPOSITORY@sha256:RELEASE_DIGEST'
docker run --rm --platform linux/arm64 --entrypoint dispat \
  'REPOSITORY@sha256:RELEASE_DIGEST' --version
docker run --rm --platform linux/arm64 --entrypoint sha256sum \
  'REPOSITORY@sha256:RELEASE_DIGEST' /usr/local/bin/dispat
```

Build the runner from the pinned Docker CLI base and pinned Alpine package lock:

```sh
docker build \
  --platform linux/arm64 \
  --build-arg DISPAT_IMAGE='REPOSITORY@sha256:RELEASE_DIGEST' \
  -t dispat-saner-next-release:candidate \
  ./docker
docker image inspect dispat-saner-next-release:candidate --format '{{.Id}}'
docker image inspect dispat-saner-next-release:candidate \
  --format '{{index .Config.Labels "org.dispat.research.source-image"}} {{.Os}}/{{.Architecture}}'
```

Put that `sha256:...` ID in the lock. The Dockerfile labels the runner with the exact release-image source. The driver requires the label, runner ID, and Linux/ARM64 inspection to match the lock, then checks the binary SHA-256 and exact version output inside the runner. `docker/dependency-images.json` records the unchanged Docker CLI, Verdaccio, registry, and BuildKit image pins. `docker/reference-toolchain.txt` is historical comparison material; each run captures the actual image inspection and binary/tool versions.

## Review and execute

The first command validates the lock and prints the proposed destination without Docker or filesystem changes:

```sh
python3 execute.py --release-lock /absolute/path/release-lock.json --run-id run-VERSION-UTC
```

Only after reviewing that output, execute exactly once:

```sh
python3 execute.py --release-lock /absolute/path/release-lock.json --run-id run-VERSION-UTC --execute
```

Add `--with-4node-extension` to run the separately reported assets (npm) → ui (npm) → base (Docker) → app (Docker) extension. This flag does not replace or modify the frozen three-node mixed protocol. UI declares a compatible npm dependency on assets, while its build reads the predecessor's local `dist` output and performs no registry install. The extension uses the same five configurations and six repetitions: mixed local-output scheduling, fully serialized npm controls, a missing base-publication barrier, injected base publication failure with repair, and injected app build failure with repair. Its verifier requires UI build to overlap the deliberately delayed assets publication as the fixture-controlled observation. It then checks that base build starts before UI publication completes; overlap and build-completed-before-publication-start are both admissible and recorded descriptively. The verifier also checks the exact seeded schedule and result order, local and published npm dependency manifests, artifact contents, both npm packages and Docker repositories, event ordering, exact injected failure codes and absent first-attempt tags, repairs, and final no-op behavior. The original three-node verifier checks its exact seeded schedule and result order too. Verifier predicates are repeated checks over 30 executions, not independent samples or scientific claims.

The first retained run exposed an invalid oracle requirement that the base-build and UI-publication intervals strictly overlap. Its traces showed the base build could validly complete before UI publication began. Before a fresh run, this frozen revision replaces that predicate with the dependency-relevant condition that base build starts before UI publication ends. It reports positive overlap and completed-before-publication-start as observations. This correction does not reinterpret the retained failed run as a formal outcome, and repetitions from the two runs must not be pooled.

Before creating an output directory, the driver compares every protocol file with `protocol-sha256.json`; missing, extra, or changed files stop the run. It then refuses an existing destination, copies the frozen protocol into `runs/RUN_ID/work`, records copied hashes in `provenance.json`, and records the runner inspection. Canonical containers are capped at two CPUs and 4 GiB; parser/core/recovery/integration have no network; mixed publication uses disposable local registries. The mixed phase requires the Docker socket and therefore a disposable daemon. Do not run two campaigns concurrently: the mixed runner uses a fixed container name and Docker daemon resources.

The core generator may exit nonzero when it retains invalid executions. The driver therefore accepts core exit codes zero and one, then requires `verify-core.py` to validate all 300 exact seeds, the core profile and locked measured version, recompute summary counts and divergence classes, and check invalid, rejection, and unknown-difference dossiers. Its verification report separately records accepted matching rows, semantic rejections, invalid executions, and rows with differences. Those scientific negative outcomes do not fail integrity verification or disappear from the sample. Missing rows, malformed accounting, missing required dossiers, or the wrong binary version do fail verification.

`provenance.json` is updated after every stage with start/completion times and exit status. A `finally` path records `completed_utc`, `FAILED`, and the exception even if setup or a later verifier stops the run. `COMPLETE` is written only after all requested stages and verifiers succeed.

A successful run ends with `COMPLETE`. Absence of that marker means partial evidence that must be retained and described. Verification rechecks recovery and every mixed-chain oracle predicate, reporting them as checks rather than independent observations. The integration script writes its 81 checks. Review every stage log and compare claims with the prior campaign without merging sample counts.

## Expected cost and limits

Budget about 45–90 minutes of wall time on a warm Docker Desktop ARM64 host, with two CPUs and 4 GiB per main container. Allow roughly 3–6 GiB of temporary disk for the copied fixtures, OCI outputs, BuildKit cache, local registry layers, and logs. A cold host also pays image-download and runner-build time and network transfer; external registries and Alpine mirrors may be unavailable even though all image and package identities are pinned. Docker socket access controls the selected daemon.

The optional four-node extension adds another 30 mixed executions. Budget roughly another 30–60 minutes and 2–4 GiB of peak temporary Docker/cache space when it is enabled; actual use depends on daemon cache retention.

The campaign proves behavior only for the locked released Linux ARM64 binary and these fixtures. It is not native Windows evidence or a production-throughput benchmark. Artificial delays expose overlap and are not timing measurements.
