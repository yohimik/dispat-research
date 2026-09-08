# Mixed npm → Docker → Docker release experiment

Retained result: `run-20260909-022316/`, 9 September 2026. See `metadata.json`, `results.json`, each case's logs/events/tags, and `verification.json`. Five configurations ran twice: mixed availability, serialized availability, missing base-publication barrier, failed base publication, and failed app build. The verifier passes 106 assertions; four repaired failures complete, and eight completed configurations perform no stage work on unchanged reruns.

## Recheck saved evidence

```sh
python3 verify.py run-20260909-022316
```

This rechecks records; it does not execute releases. `SHA256SUMS.json` fingerprints the retained files. The saved `harness-at-run.py` is the exact executed source. The current `run-buildkit.py` only adds Python/version preconditions and an explicit binary override; stage behavior is unchanged.

## Execute a new campaign

Requires Python 3.12+, the official Dispat 1.8.2 binary, Git, Node/npm, and a running Docker engine with Buildx. The retained host used Python 3.12.14, Node 24.18.0, npm 12.0.1, Docker 29.6.1, and Buildx 0.35.0. Binary SHA-256 and resolved version are in the retained metadata. Supply the pinned binary explicitly:

```sh
DISPAT_BIN=/absolute/path/to/dispat-1.8.2 python3.12 run-buildkit.py
python3 verify.py run-YYYYMMDD-HHMMSS
```

The harness creates disposable Git repositories, a loopback npm registry, a private Docker-network registry, and an isolated BuildKit builder. Publication stays in those private registries. It pulls registry/builder images if needed; no Docker daemon configuration is changed. Cleanup removes its containers, builder, and network; image cache may remain. Never use production registry credentials or destinations in these fixtures.

npm produces a local file used by the base Docker image; the app image obtains its base from the registry. OCI archives separate build from publication. Controlled delays make overlap and barriers observable; measured overlap is not a throughput benchmark. Image digests captured from the local image cache after the run are recorded separately, with that provenance stated.

## Excluded attempts

- `run-20260909-014421`: missing Git origin during setup.
- `run-20260909-014511`: Docker daemon could not reach the host-loopback registry.
- `run-20260909-022052`: Apple Python 3.9 monotonic clocks had different origins between processes. Cross-process intervals from this run are invalid and excluded.
- `run.py`: earlier host-loopback registry harness, retained as setup history, not the reported harness.

These attempts are not successful protocol observations. Do not combine them with the retained campaign or conceal the reasons for exclusion.

This directory contains local paths, Git metadata, and identifying binary output. It needs curation and anonymity review before being supplied to reviewers.
