# SANER 2027 mechanism campaign

This campaign evaluates controlled recovery mechanisms in released Dispat 1.10.0. `PROTOCOL.md` defines the prospective 140-case matrix and finite projection. `PILOT-FREEZE.json` preserves the historical pre-pilot input hashes. After the pilot passed, non-mutating provenance, offline verification, and archive helpers were added and frozen in `FULL-FREEZE.json`; the original execution harness and publisher hashes remained unchanged.

The completed results and limitations are in `RESULTS.md`. Raw command records and observations remain expanded under `runs/`; fixture working trees, local registries, publisher event streams, and complete Git metadata are stored in each run's verified `expanded-fixtures.tar.gz`.

## Fresh-machine prerequisite and runner recovery

The exact `full-01` environment requires the locally available runner image ID `sha256:6f92932fbba5d33d61d777073f5fc155133063f4c3d4b2f950e3e5b9ed9a263e`. Check it before running:

```sh
docker image inspect \
  sha256:6f92932fbba5d33d61d777073f5fc155133063f4c3d4b2f950e3e5b9ed9a263e \
  --format '{{.Id}} {{.Os}}/{{.Architecture}}'
```

No OCI layout or `docker save` export of that runner is retained in this repository, and the `dispat-saner@sha256:6f92932…` repository digest is local evidence rather than a documented public pull location. A fresh machine therefore cannot reconstruct the exact measured runner from this campaign alone.

The runner recipe is retained in the baseline campaign at [`../campaign-1.10.0-20260909/docker/Dockerfile`](../campaign-1.10.0-20260909/docker/Dockerfile), with its exact APK package list in [`../campaign-1.10.0-20260909/docker/apk.lock`](../campaign-1.10.0-20260909/docker/apk.lock). From this campaign directory, the closest rebuild is:

```sh
baseline=../campaign-1.10.0-20260909
docker buildx build \
  --platform linux/arm64 \
  --file "$baseline/docker/Dockerfile" \
  --build-arg 'DISPAT_IMAGE=yohimik/dispat-alpine@sha256:f2a49c21eca0a3e30af1396eca538920b2faa475b50f12d4aae99236e2fe2955' \
  --load \
  --tag dispat-saner:rebuild \
  "$baseline/docker"
docker image inspect dispat-saner:rebuild --format '{{.Id}}'
docker run --rm --network none --platform linux/arm64 dispat-saner:rebuild \
  sh -c 'dispat --version; sha256sum /usr/local/bin/dispat; cat /toolchain-apk.txt'
```

Both parent images are digest-pinned in that recipe, but `apk add` consults an external package repository during the rebuild. Exact package availability and image construction metadata are not archived, so the rebuild may fail or produce a different image ID even when the Dispat binary still has the expected SHA-256. If the image ID differs from `6f92932…`, do not substitute it into `full-01` or describe the result as an exact rerun. Record the rebuilt image inspection and binary hash, use a new release lock and run name, and treat it as a separate provenance run. `FULL-PROVENANCE.json` documents that `full-01` used the pre-existing exact image.

## Run a new complete matrix

Run from this directory. The wrapper records the exact Docker command and start/end times, creates a new run directory, uses the pinned image by immutable ID, and refuses to overwrite any existing run, log, or execution record.

```sh
python3 run.py full-02
```

The wrapper launches the equivalent of:

```sh
docker run --rm \
  --network none \
  --cpus 2 \
  --memory 4g \
  --platform linux/arm64 \
  -v "$PWD:/campaign" \
  -w /campaign \
  sha256:6f92932fbba5d33d61d777073f5fc155133063f4c3d4b2f950e3e5b9ed9a263e \
  python3 execute.py runs/full-02
```

Do not reuse `full-01`, rerun the frozen pilot, or merge a new run with prior observations. A nonzero case is retained as a failed observation; the harness continues through the matrix and exits nonzero after writing its summary.

## Offline consistency check

Run the independently implemented checker in Docker while the new fixture trees are expanded. It writes a new output with exclusive creation and does not change the executor's `summary.json`.

```sh
docker run --rm \
  --network none \
  --cpus 2 \
  --memory 4g \
  --platform linux/arm64 \
  -v "$PWD:/campaign" \
  -w /campaign \
  sha256:6f92932fbba5d33d61d777073f5fc155133063f4c3d4b2f950e3e5b9ed9a263e \
  python3 verify.py runs/full-02 runs/full-02/verifier.json
```

The checker reconstructs plans from raw JSON command output, verifies tags, events, local artifact identities, case inventory, summaries, and the complete finite enumeration. This is an offline evidence consistency check, not an independent replication.

## Archive the fixture trees

After verification, archive and hash the expanded work trees and bare origins. The command verifies every regular file from the archive before removing expanded copies and refuses to overwrite existing archive evidence.

```sh
python3 archive.py runs/full-02 --remove-expanded
python3 postprocess.py runs/full-02 summary-full-02.json
```

To audit `full-01` from its archive, first copy the retained run into a new temporary directory, extract `expanded-fixtures.tar.gz` there, and point the Docker command above at that extracted run with a new verifier-output filename. Never extract over retained evidence.

## Integrity and provenance

`FULL-PROVENANCE.json` records the GitHub release response, newest CLI selection, Docker client/server versions, host OS, research Git identity and status, image inspections, frozen script hashes, and a binary identity probe from the network-disabled runner. `release-lock.json` pins the released source and runner images and the binary SHA-256. `SHA256SUMS.json` covers all retained campaign files except itself.

To check one retained file against the manifest:

```sh
python3 -c 'import hashlib,json,pathlib; m=json.load(open("SHA256SUMS.json")); p=pathlib.Path("summary.json"); print(hashlib.sha256(p.read_bytes()).hexdigest()==m["files"][str(p)]["sha256"])'
```
