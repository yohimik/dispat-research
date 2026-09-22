#!/bin/bash
# Corrected single-node baseline of the LLVM parity pair on lb-w2: waits for
# the distributed repeat on lb-orch to finish (its time file), stops w2's
# worker, refreshes the clone with the v24.0.0 baseline tags from origin.git,
# runs the same recipe without workers under /usr/bin/time, waits, copies logs.
#   llvm-baseline2.sh <commit the baseline releases from>
set -u
COMMIT=$1
S=$(cat /tmp/dispat-gce/secret.txt)
D=/private/tmp/claude-501/-Users-yohimik-Projects-dispat/aba20193-908a-4dbf-a0ef-363528c9fa79/scratchpad/llvm-logs
mkdir -p "$D"
ssh_() { local host=$1; shift; perl -e 'alarm 900; exec @ARGV' -- gcloud compute ssh "$host" --project dispat --zone us-central1-a --command "$*" 2>&1; }
scp_() { perl -e 'alarm 900; exec @ARGV' -- gcloud compute scp --project dispat --zone us-central1-a "$@" 2>&1 | grep -v '^$'; }
timeline() { grep -o '"time":"[^"]*",[^}]*"message":"\(release plan ready\|stage started\|stage succeeded\|stage failed\|build script failed\|package published\|done\)"' "$1" | sed -E 's/"time":"([^"]+)".*"package":"([^"]+)".*"stage":"([^"]+)".*"message":"([^"]+)"/\1 \2:\3 \4/; s/"time":"([^"]+)".*"message":"([^"]+)"/\1 \2/'; }

for i in $(seq 1 120); do
    n=$(ssh_ lb-orch "if [ -f ~/release-dist3.time ] && [ \$(pgrep -x dispat | wc -l) = 0 ]; then echo over; else echo running; fi" | tail -1)
    case "$n" in over) break ;; esac
    sleep 60
done
echo "$(date -u +%T) the distributed repeat is over ($n)"

echo "$(date -u +%T) refreshing the baseline clone on lb-w2"
ssh_ lb-w2 "pkill -x dispat; sleep 2; cd ~/llvm-src && git remote set-url origin ssh://yohimik@10.128.0.9/home/yohimik/origin.git && git fetch -q origin 'refs/tags/dispat/*/v24.0.0:refs/tags/dispat/*/v24.0.0' && git tag -l 'dispat/*/v24.1.0' 'dispat-release-lock*' | xargs -r git tag -d >/dev/null; git checkout -q -B dispat-gce $COMMIT && rm -rf ~/origin-local.git && git clone -q --bare ~/llvm-src ~/origin-local.git && git remote set-url origin ~/origin-local.git && git fetch -q origin && rm -rf llvm/_dispat lld/_dispat polly/_dispat .ci/dispat/bundle/_dispat && echo tags: \$(git tag | sort | tr '\n' ' ') && git log --oneline -1 | cat && dispat status --config dispat.local.yaml 2>&1 | grep -v '\"level\":\"debug\"' | grep -c '24.0.0 -> 24.1.0'" | tail -4

echo "$(date -u +%T) starting the baseline on lb-w2"
ssh_ lb-w2 "cd ~/llvm-src && rm -f ~/release-local.time && date -u +%FT%TZ > ~/release-local.start && nohup env DISPAT_EXECUTION_SECRET=$S /usr/bin/time -v -o ~/release-local.time dispat release --config dispat.local.yaml --log-format json --log-level debug > ~/release-local.log 2>&1 < /dev/null & sleep 30; grep -o '\"time\":\"[^\"]*\",[^}]*\"message\":\"\(release plan ready\|stage started\)\"' ~/release-local.log | sed -E 's/\"time\":\"([^\"]+)\".*\"message\":\"([^\"]+)\"/\1 \2/' | head -3" | tail -4

for i in $(seq 1 120); do
    n=$(ssh_ lb-w2 "if [ -f ~/release-local.time ]; then echo over; else echo running; fi" | tail -1)
    case "$n" in over) break ;; esac
    sleep 60
done
echo "$(date -u +%T) baseline exited ($n)"
scp_ lb-w2:release-local.log "$D/release-local.log"
scp_ lb-w2:release-local.time "$D/release-local.time"
scp_ lb-w2:release-local.start "$D/release-local.start"
cat "$D/release-local.start"; grep -E 'Elapsed|Maximum resident|Exit status' "$D/release-local.time"
timeline "$D/release-local.log" | tail -30
ssh_ lb-w2 "cd ~/llvm-src && git tag | grep v24.1 | tr '\n' ' '; echo; du -sh llvm/_dispat/install lld/_dispat/install polly/_dispat/install .ci/dispat/bundle/_dispat/dist 2>&1" | tail -6
echo "$(date -u +%T) BASELINE 2 DONE"
