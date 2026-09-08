#!/bin/bash
# Prepared only: no work is possible without --released.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
MAIN=${DISPAT_SOURCE_REPO:-/Users/yohimik/Projects/dispat}
VERSION=1.8.1; TAG=services/dispat/v$VERSION
OUT=; RELEASED=0; ONLY=all
while [ $# -gt 0 ]; do case "$1" in
  --released) RELEASED=1;; --out) OUT=${2:?}; shift;; --stage) ONLY=${2:?}; shift;; *) echo "unknown argument: $1" >&2; exit 2;; esac; shift; done
[ "$RELEASED" = 1 ] || { echo "refusing before official release (pass --released)" >&2; exit 2; }
case "$ONLY" in all|provenance|images|e1|e2|e3|e4|e5|finalize);; *) exit 2;; esac
[ -n "$OUT" ] || { echo "--out required" >&2; exit 2; }
RESULTS=$(cd "$ROOT/results" && pwd -P)
case "$OUT" in /*) requested=$OUT;; *) requested=$ROOT/$OUT;; esac
parent=$(cd "$(dirname "$requested")" 2>/dev/null && pwd -P) || { echo "output parent does not exist" >&2; exit 2; }
base=$(basename "$requested")
[ "$parent" = "$RESULTS" ] && [[ $base =~ ^v181-[0-9]{8}(-[A-Za-z0-9._-]+)?$ ]] || { echo "output must be a direct results/v181-YYYYMMDD child" >&2; exit 2; }
OUT=$RESULTS/$base
[ ! -L "$OUT" ] || { echo "output may not be a symlink" >&2; exit 2; }
[[ ${DISPAT_RELEASE_COMMIT:-} =~ ^[0-9a-f]{40}$ ]] || { echo "full DISPAT_RELEASE_COMMIT required" >&2; exit 2; }

manifest() { python3 - "$@" <<'PY'
import hashlib,os,sys
fs=[]
for a in sys.argv[1:]:
 if os.path.isfile(a): fs.append(os.path.abspath(a))
 else:
  for r,ds,ns in os.walk(a):
   ds[:]=sorted(d for d in ds if d!='__pycache__')
   fs += [os.path.abspath(os.path.join(r,n)) for n in ns]
for p in sorted(set(fs)):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 print(h.hexdigest(),p)
PY
}

if [ -e "$OUT" ] && [ ! -f "$OUT/campaign.identity" ]; then
  echo "refusing pre-existing output without a campaign identity: $OUT" >&2; exit 2
fi
mkdir -p "$OUT/.complete" "$OUT/.staging"
[ -d "$OUT/.complete" ] && [ -d "$OUT/.staging" ] || exit 2
remote=$(git -C "$MAIN" remote get-url origin)
got=$(git ls-remote "$remote" "refs/tags/$TAG^{}" | awk '{print $1}')
[ -n "$got" ] || got=$(git ls-remote "$remote" "refs/tags/$TAG" | awk '{print $1}')
[ "$got" = "$DISPAT_RELEASE_COMMIT" ] || { echo "tag/commit mismatch" >&2; exit 1; }
docker pull "docker.io/yohimik/dispat-alpine:$VERSION" >/dev/null
PIN=$(docker image inspect "docker.io/yohimik/dispat-alpine:$VERSION" --format '{{range .RepoDigests}}{{println .}}{{end}}' | awk '/yohimik\/dispat-alpine@sha256:/{print;exit}')
[ -n "$PIN" ] || { echo "published image has no digest" >&2; exit 1; }
PINARG="$VERSION@${PIN#*@}"
# Hash only harness-owned files. e3a's multi-gigabyte fixture clones are bound
# separately by HEAD below and never traversed.
hh=$(manifest "$ROOT/e1" "$ROOT/e2" "$ROOT/e3a/replay.py" "$ROOT/e4" "$ROOT/shared" "$ROOT/docker/Dockerfile" "$MAIN/tests/experiments" "$ROOT/prepare-v181/campaign.sh" "$ROOT/prepare-v181/README.md" | shasum -a 256 | awk '{print $1}')
gcn=$(git -C "$ROOT/e3a/repos/google-cloud-node" rev-parse HEAD)
cc=$(git -C "$ROOT/e3a/repos/conventional-changelog" rev-parse HEAD)
[ "$gcn" = 54e244b4980e362ac9194d29c299b949ff778fda ] || { echo "unexpected google-cloud-node fixture HEAD" >&2; exit 1; }
[ "$cc" = 340ad83ee93939fc4a8c8f2da1bf728111299941 ] || { echo "unexpected conventional-changelog fixture HEAD" >&2; exit 1; }
[ -z "$(git -C "$ROOT/e3a/repos/google-cloud-node" status --porcelain=v1 --untracked-files=all)" ] || { echo "google-cloud-node fixture is dirty" >&2; exit 1; }
[ -z "$(git -C "$ROOT/e3a/repos/conventional-changelog" status --porcelain=v1 --untracked-files=all)" ] || { echo "conventional-changelog fixture is dirty" >&2; exit 1; }
printf 'version=%s\ntag=%s\ncommit=%s\nimage=%s\nharness=%s\ngcn=%s\ncc=%s\n' "$VERSION" "$TAG" "$DISPAT_RELEASE_COMMIT" "$PIN" "$hh" "$gcn" "$cc" > "$OUT/.identity.new"
if [ -f "$OUT/campaign.identity" ]; then cmp -s "$OUT/campaign.identity" "$OUT/.identity.new" || { echo "refusing mixed resume: identity changed" >&2; diff -u "$OUT/campaign.identity" "$OUT/.identity.new" || true; exit 1; }; else mv "$OUT/.identity.new" "$OUT/campaign.identity"; fi
[ ! -f "$OUT/.identity.new" ] || rm "$OUT/.identity.new"
MARK=$OUT/.complete
need(){
 [ -f "$MARK/$1" ] && cmp -s "$MARK/$1" "$OUT/campaign.identity" || { echo "$1 is not complete for this identity" >&2; exit 2; }
 if [ "$1" = images ]; then
  # Tags are only build-time labels. All campaign executions use recorded IDs.
  . "$OUT/images/image-ids.sh"
  for id in "$RUNTIME_IMAGE" "$NODE_IMAGE" "$E5_IMAGE"; do docker image inspect "$id" >/dev/null; done
 fi
}
stage(){
 n=$1; shift
 if [ "$ONLY" != all ] && [ "$ONLY" != "$n" ]; then return 0; fi
 if [ -f "$MARK/$n" ]; then need "$n"; echo "skip $n"; return 0; fi
 STAGE=$OUT/.staging/$n
 [ ! -e "$STAGE" ] && [ ! -e "$OUT/$n" ] || { echo "partial/unmarked $n exists; inspect and move it aside" >&2; exit 1; }
 mkdir "$STAGE"; "$@"; mv "$STAGE" "$OUT/$n"; cp "$OUT/campaign.identity" "$MARK/$n"
}

provenance(){
 docker image inspect "$PIN" > "$STAGE/published-image.json"; docker run --rm "$PIN" dispat --version > "$STAGE/binary-version.txt"; rg -q "dispat $VERSION" "$STAGE/binary-version.txt"
 cid=$(docker create "$PIN"); docker cp "$cid:/usr/local/bin/dispat" "$STAGE/dispat"; docker rm "$cid" >/dev/null; shasum -a 256 "$STAGE/dispat" > "$STAGE/binary-sha256.txt"
 cp "$OUT/campaign.identity" "$STAGE/"; git -C "$MAIN" rev-parse HEAD > "$STAGE/source-head.txt"; git -C "$MAIN" status --porcelain=v1 > "$STAGE/source-dirty.txt"
 manifest "$ROOT/e1" "$ROOT/e2" "$ROOT/e3a/replay.py" "$ROOT/e4" "$ROOT/shared" "$ROOT/docker/Dockerfile" > "$STAGE/harness-sha256.txt"; manifest "$MAIN/tests/experiments" > "$STAGE/e5-source-sha256.txt"
}
images(){
 need provenance
 docker build -t dispat-exp:v181-runtime --target runtime --build-arg "DISPAT_VERSION=$PINARG" "$ROOT/docker"
 docker build -t dispat-exp:v181-node --target node --build-arg "DISPAT_VERSION=$PINARG" "$ROOT/docker"
 docker buildx build -f "$MAIN/tests/experiments/Dockerfile" --build-arg "DISPAT_VERSION=$PINARG" --load -t dispat-experiments:v181 "$MAIN/tests/experiments"
 RUNTIME_IMAGE=$(docker image inspect dispat-exp:v181-runtime --format '{{.Id}}')
 NODE_IMAGE=$(docker image inspect dispat-exp:v181-node --format '{{.Id}}')
 E5_IMAGE=$(docker image inspect dispat-experiments:v181 --format '{{.Id}}')
 printf 'RUNTIME_IMAGE=%q\nNODE_IMAGE=%q\nE5_IMAGE=%q\n' "$RUNTIME_IMAGE" "$NODE_IMAGE" "$E5_IMAGE" > "$STAGE/image-ids.sh"
 docker image inspect "$RUNTIME_IMAGE" "$NODE_IMAGE" "$E5_IMAGE" > "$STAGE/images.json"
 for i in "$RUNTIME_IMAGE" "$NODE_IMAGE" "$E5_IMAGE"; do docker run --rm --entrypoint dispat "$i" --version; done > "$STAGE/versions.txt"
 [ "$(rg -c "dispat $VERSION" "$STAGE/versions.txt")" = 3 ]
}
e1(){
 need images
 docker run --rm --cpus 2 --memory 4g -v "$ROOT:/exp:ro" -w /exp "$RUNTIME_IMAGE" sh e1/gate0.sh > "$STAGE/golden.log"
 for x in 'core 1 1000' 'core 5001 500' 'full 1 1000' 'full 5001 500'; do
  set -- $x
  shard="$1-$2-$3"
  mkdir "$STAGE/$shard"
  docker run --rm --cpus 2 --memory 4g -v "$ROOT:/exp:ro" -v "$STAGE:/results" -w /exp "$RUNTIME_IMAGE" \
    python3 e1/run.py --profile "$1" --seed0 "$2" --n "$3" --workers 2 --out "/results/$shard"
 done
 docker run --rm --cpus 2 --memory 4g -v "$ROOT:/exp:ro" -v "$STAGE:/results" -w /exp "$RUNTIME_IMAGE" \
  python3 e1/ccme2_vectors.py /results/ccme2-vectors.json
 python3 - "$STAGE" "$ROOT/shared/planjson.py" <<'PY'
import hashlib,json,os,sys
root=sys.argv[1]
specs=[('core',1,1000),('core',5001,500),('full',1,1000),('full',5001,500)]
rows=[]
for profile,first,count in specs:
 rel=f'{profile}-{first}-{count}/e1-{profile}-{first}-{count}.json'
 path=os.path.join(root,rel)
 with open(path,'rb') as f: digest=hashlib.sha256(f.read()).hexdigest()
 data=json.load(open(path))
 assert data['summary']['profile']==profile and data['summary']['instances']==count
 assert 'dispat 1.8.1 ' in data['summary']['dispat'] or data['summary']['dispat'].startswith('dispat 1.8.1')
 assert len(data['rows'])==count
 assert [data['rows'][0]['seed'],data['rows'][-1]['seed']]==[first,first+count-1]
 rows.append({'profile':profile,'first':first,'count':count,'path':rel,'sha256':digest})
extractor=sys.argv[2]
with open(extractor,'rb') as f: extractor_hash=hashlib.sha256(f.read()).hexdigest()
json.dump({'canonical':True,'dispat':'1.8.1','extractor_sha256':extractor_hash,'shards':rows},open(os.path.join(root,'canonical-manifest.json'),'w'),indent=1)
PY
}
e2(){ need images; DISPAT_EXPERIMENT_IMAGE=$NODE_IMAGE "$ROOT/e2/run.sh" dispat "$STAGE/dispat-rep1"; DISPAT_EXPERIMENT_IMAGE=$NODE_IMAGE "$ROOT/e2/run.sh" dispat "$STAGE/dispat-rep2"; }
e3(){ need images; docker run --rm --cpus 2 --memory 4g -v "$ROOT:/exp" -v "$STAGE:/results" -w /exp "$RUNTIME_IMAGE" python3 e3a/replay.py /exp/e3a/repos/google-cloud-node gcn 5 /results/gcn.json; docker run --rm --cpus 2 --memory 4g -v "$ROOT:/exp" -v "$STAGE:/results" -w /exp "$RUNTIME_IMAGE" python3 e3a/replay.py /exp/e3a/repos/conventional-changelog cc 5 /results/cc.json; }
e4(){ need images; mkdir "$STAGE/rep1" "$STAGE/rep2" "$STAGE/fixture" "$STAGE/cells" "$STAGE/failures"; for r in rep1 rep2; do docker run --rm --cpus 2 --memory 4g -v "$ROOT:/exp:ro" -v "$STAGE/$r:/results" -w /exp "$RUNTIME_IMAGE" python3 e4/recovery.py /results | tee "$STAGE/$r/recovery.log"; done; docker run --rm --cpus 2 --memory 4g -v "$ROOT:/exp:ro" -v "$STAGE/fixture:/results" -w /exp "$RUNTIME_IMAGE" sh e4/verify_fixture_provenance.sh /results; for i in 0 1 2 3 4 5 6 7; do docker run --rm --cpus 2 --memory 4g -e E4_FAILURE_DIR=/failures -v "$ROOT:/exp:ro" -v "$STAGE/failures:/failures" -w /exp "$RUNTIME_IMAGE" python3 e4/timing.py "$i" > "$STAGE/cells/$i.csv"; done; head -1 "$STAGE/cells/0.csv" > "$STAGE/timing.csv"; for i in 0 1 2 3 4 5 6 7; do tail -n +2 "$STAGE/cells/$i.csv" >> "$STAGE/timing.csv"; done; [ "$(wc -l < "$STAGE/timing.csv" | tr -d ' ')" = 9 ]; }
e5(){ need images; for x in 'orphan dispat' 'midrelease dispat clean' 'midrelease dispat conflict'; do set -- $x; docker run --rm --cpus 2 --memory 4g -v "$MAIN/tests/experiments:/exp:ro" -v "$STAGE:/results" "$E5_IMAGE" "$@"; done; python3 - "$STAGE" <<'PY'
import glob,json,os,sys
paths=glob.glob(os.path.join(sys.argv[1],'*','verdict.json'))
assert len(paths)==3, paths
for p in paths:
 d=json.load(open(p)); assert d.get('tool')=='dispat' and d.get('passed') is True,(p,d)
PY
}
finalize(){ for s in provenance images e1 e2 e3 e4 e5; do need "$s"; done; manifest "$OUT/provenance" "$OUT/images" "$OUT/e1" "$OUT/e2" "$OUT/e3" "$OUT/e4" "$OUT/e5" > "$STAGE/SHA256SUMS"; cp "$OUT/campaign.identity" "$STAGE/"; }
stage provenance provenance; stage images images; stage e1 e1; stage e2 e2; stage e3 e3; stage e4 e4; stage e5 e5; stage finalize finalize
