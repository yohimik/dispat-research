#!/bin/bash
# E2 host runner: one phase per invocation with a FRESH registry
# (gotcha 7: never share one registry between two tools' runs).
#
#   ./e2/run.sh lerna|nx|turbo|dispat [outdir]
#
# Creates uniquely named verdaccio + failproxy containers on an isolated
# network, clears the deny list, waits
# for the registry, then runs the phase inside dispat-exp:node and tees
# the transcript into the result directory.
set -eu
cd "$(dirname "$0")/.."
PHASE=$1
OUT=${2:-$PWD/results/e2-$PHASE-$(date +%Y%m%d-%H%M%S)}
IMAGE=${DISPAT_EXPERIMENT_IMAGE:-dispat-exp:node}
mkdir -p "$OUT"
DENY="$OUT/deny"
mkdir -p "$DENY"
RUN_ID="e2-${PHASE}-$$-$(date +%s)"
NETWORK="${RUN_ID}-net"
VERDACCIO="${RUN_ID}-verdaccio"
FAILPROXY="${RUN_ID}-failproxy"

cleanup() {
  docker rm -f "$FAILPROXY" "$VERDACCIO" >/dev/null 2>&1 || true
  docker network rm "$NETWORK" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

docker network create "$NETWORK" >/dev/null
docker run -d --name "$VERDACCIO" --network "$NETWORK" --network-alias verdaccio \
  --cpus 0.25 --memory 512m \
  -v "$PWD/e2/verdaccio.yaml":/verdaccio/conf/config.yaml \
  verdaccio/verdaccio:6 >/dev/null
docker run -d --name "$FAILPROXY" --network "$NETWORK" --network-alias failproxy \
  --cpus 0.25 --memory 512m -e UPSTREAM=verdaccio:4873 \
  -v "$PWD/e2/failproxy.py":/fp.py:ro -v "$DENY":/deny \
  python:3.12-alpine python3 /fp.py >/dev/null

for i in $(seq 30); do
  docker run --rm --network "$NETWORK" --cpus 0.25 --memory 256m \
    python:3.12-alpine python3 -c \
    "import urllib.request;urllib.request.urlopen('http://verdaccio:4873/-/ping',timeout=2)" \
    >/dev/null 2>&1 && break
  sleep 1
done

docker run --rm --network "$NETWORK" --cpus 1.5 --memory 3g \
  -v "$PWD":/exp -v "$OUT":/results -v "$DENY":/deny \
  "$IMAGE" bash /exp/e2/orphan.sh "$PHASE" | tee "$OUT/transcript.txt"
