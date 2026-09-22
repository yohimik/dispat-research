#!/bin/bash
# Second parity pair: waits for the distributed LLVM run (release-dist2.log) on
# lb-orch to exit, copies every log off the three machines, then sets up and
# starts the single-node baseline of the same recipe on lb-w2 and waits for it.
#   llvm-monitor2.sh <commit the baseline builds from>
set -u
COMMIT=$1
S=$(cat /tmp/dispat-gce/secret.txt)
D=/private/tmp/claude-501/-Users-yohimik-Projects-dispat/aba20193-908a-4dbf-a0ef-363528c9fa79/scratchpad/llvm-logs
mkdir -p "$D"
ssh_() { local host=$1; shift; perl -e 'alarm 900; exec @ARGV' -- gcloud compute ssh "$host" --project dispat --zone us-central1-a --command "$*" 2>&1; }
scp_() { perl -e 'alarm 900; exec @ARGV' -- gcloud compute scp --project dispat --zone us-central1-a "$@" 2>&1 | grep -v '^$'; }
timeline() { grep -o '"time":"[^"]*",[^}]*"message":"\(release plan ready\|task assigned\|task finished\|outputs admitted\|publication authorized\|build script failed\|stage started\|stage succeeded\|stage failed\|package published\|done\)"' "$1" | sed -E 's/"time":"([^"]+)".*"task":"([^"]+)".*"message":"([^"]+)"/\1 \2 \3/; s/"time":"([^"]+)".*"package":"([^"]+)".*"stage":"([^"]+)".*"message":"([^"]+)"/\1 \2:\3 \4/; s/"time":"([^"]+)".*"message":"([^"]+)"/\1 \2/'; }

echo "$(date -u +%T) waiting for the distributed release on lb-orch"
for i in $(seq 1 150); do
    n=$(ssh_ lb-orch "pgrep -x dispat | wc -l" | tail -1)
    case "$n" in 0) break ;; esac
    sleep 60
done
echo "$(date -u +%T) distributed release exited (pgrep=$n)"
scp_ lb-orch:release-dist2.log "$D/release-dist2.log"
scp_ lb-orch:release-dist2.start "$D/release-dist2.start"
scp_ lb-w1:worker.log "$D/worker-lb-w1-dist2.log"
scp_ lb-w2:worker.log "$D/worker-lb-w2-dist2.log"
cat "$D/release-dist2.start"
timeline "$D/release-dist2.log" | tail -40
ssh_ lb-orch "cd ~/llvm && git log --oneline -2 | cat; git tag | grep v24.1 | tr '\n' ' '; echo; du -sh llvm/_dispat/install lld/_dispat/install polly/_dispat/install .ci/dispat/bundle/_dispat/dist 2>&1" | tail -8

echo "$(date -u +%T) preparing the baseline on lb-w2"
ssh_ lb-w2 "pkill -x dispat; sleep 2; rm -rf ~/llvm-src ~/origin-local.git; git clone -q ssh://yohimik@10.128.0.9/home/yohimik/origin.git ~/llvm-src && cd ~/llvm-src && git checkout -q -B dispat-gce $COMMIT && git tag -l 'dispat/*/v24.1.0' 'dispat-release-lock*' | xargs -r git tag -d >/dev/null; git clone -q --bare ~/llvm-src ~/origin-local.git && git remote set-url origin ~/origin-local.git && git fetch -q origin && scp -q yohimik@10.128.0.9:llvm/dispat.yaml yohimik@10.128.0.9:llvm/dispat.local.yaml ~/llvm-src/ && echo tags: \$(git tag | sort | tr '\n' ' ') && git log --oneline -1 | cat && dispat status --config dispat.local.yaml 2>&1 | grep -v '\"level\":\"debug\"' | tail -6" | tail -12

echo "$(date -u +%T) starting the baseline on lb-w2"
ssh_ lb-w2 "cd ~/llvm-src && date -u +%FT%TZ > ~/release-local.start && nohup env DISPAT_EXECUTION_SECRET=$S /usr/bin/time -v -o ~/release-local.time dispat release --config dispat.local.yaml --log-format json --log-level debug > ~/release-local.log 2>&1 < /dev/null & sleep 30; grep -o '\"time\":\"[^\"]*\",\"message\":\"[^\"]*\"' ~/release-local.log | head -4" | tail -6

for i in $(seq 1 120); do
    n=$(ssh_ lb-w2 "pgrep -x dispat | wc -l" | tail -1)
    case "$n" in 0) break ;; esac
    sleep 60
done
echo "$(date -u +%T) baseline exited (pgrep=$n)"
scp_ lb-w2:release-local.log "$D/release-local.log"
scp_ lb-w2:release-local.time "$D/release-local.time"
scp_ lb-w2:release-local.start "$D/release-local.start"
cat "$D/release-local.start"; grep -E 'Elapsed|Maximum resident|Exit status' "$D/release-local.time"
timeline "$D/release-local.log" | tail -30
echo "$(date -u +%T) BASELINE DONE"
