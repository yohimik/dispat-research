#!/bin/bash
# Waits for the distributed LLVM parity run on lb-orch to exit, copies every
# log off the three machines, then sets up and starts the single-node baseline
# of the same recipe on lb-w2 and waits for it too. Prints what it did.
set -u
S=$(cat /tmp/dispat-gce/secret.txt)
D=/private/tmp/claude-501/-Users-yohimik-Projects-dispat/aba20193-908a-4dbf-a0ef-363528c9fa79/scratchpad/llvm-logs
mkdir -p "$D"
ssh_() { local host=$1; shift; perl -e 'alarm 900; exec @ARGV' -- gcloud compute ssh "$host" --project dispat --zone us-central1-a --command "$*" 2>&1; }
scp_() { perl -e 'alarm 900; exec @ARGV' -- gcloud compute scp --project dispat --zone us-central1-a "$@" 2>&1 | grep -v '^$'; }

echo "$(date -u +%T) waiting for the distributed release on lb-orch"
for i in $(seq 1 150); do
    n=$(ssh_ lb-orch "pgrep -x dispat | wc -l" | tail -1)
    case "$n" in 0) break ;; esac
    sleep 60
done
echo "$(date -u +%T) distributed release exited (pgrep=$n)"
scp_ lb-orch:release-dist.log "$D/release-dist.log"
scp_ lb-w1:worker.log "$D/worker-lb-w1-dist.log"
scp_ lb-w2:worker.log "$D/worker-lb-w2-dist.log"
ssh_ lb-orch "cd ~/llvm && git log --oneline -3 | cat; git tag | grep v24.1 | tr '\n' ' '; echo; ls llvm/_dispat lld/_dispat polly/_dispat .ci/dispat/bundle/_dispat 2>&1 | head -20; du -sh llvm/_dispat/install lld/_dispat/install polly/_dispat/install .ci/dispat/bundle/_dispat/dist 2>&1" | tail -30
grep -o '"time":"[^"]*",[^}]*"message":"\(release plan ready\|task assigned\|task claimed\|task finished\|outputs admitted\|publication authorized\|release finished\|release failed\)"' "$D/release-dist.log" | sed -E 's/"time":"([^"]+)".*"task":"([^"]+)".*"message":"([^"]+)"/\1 \2 \3/; s/"time":"([^"]+)".*"message":"([^"]+)"/\1 \2/' | tail -40

echo "$(date -u +%T) preparing the baseline on lb-w2"
ssh_ lb-w2 "pkill -x dispat; sleep 2; rm -rf ~/llvm-src ~/origin-local.git; git clone -q ssh://yohimik@10.128.0.9/home/yohimik/origin.git ~/llvm-src && cd ~/llvm-src && git checkout -q -B dispat-gce 674b30e9a69a19621db73de867593e2ca13a9aa6 && git tag -l 'dispat/*/v24.1.0' 'dispat-release-lock*' | xargs -r git tag -d >/dev/null; git clone -q --bare ~/llvm-src ~/origin-local.git && git remote set-url origin ~/origin-local.git && git fetch -q origin && echo tags: \$(git tag | sort | tr '\n' ' ') && dispat status --config dispat.local.yaml 2>&1 | tail -8" | tail -14

echo "$(date -u +%T) starting the baseline on lb-w2"
ssh_ lb-w2 "cd ~/llvm-src && date -u +%FT%TZ > ~/release-local.start && nohup env DISPAT_EXECUTION_SECRET=$S /usr/bin/time -v -o ~/release-local.time dispat release --config dispat.local.yaml --log-format json --log-level debug > ~/release-local.log 2>&1 < /dev/null & sleep 30; grep -o '\"time\":\"[^\"]*\",\"message\":\"[^\"]*\"' ~/release-local.log | head -6" | tail -8

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
grep -o '"time":"[^"]*",[^}]*"message":"\(release plan ready\|stage started\|stage succeeded\|package published\|release finished\|release failed\)"' "$D/release-local.log" | sed -E 's/"time":"([^"]+)".*"package":"([^"]+)".*"stage":"([^"]+)".*"message":"([^"]+)"/\1 \2 \3 \4/; s/"time":"([^"]+)".*"message":"([^"]+)"/\1 \2/' | tail -30
echo "$(date -u +%T) BASELINE DONE"
