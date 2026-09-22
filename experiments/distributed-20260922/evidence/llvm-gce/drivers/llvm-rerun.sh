#!/bin/bash
# Third distributed attempt of the LLVM parity pair, run once the baseline on
# lb-w2 has exited: resets the records run 4 wrote, restarts w2's worker, starts
# the distributed release on lb-orch (release-dist3.log), waits for it, copies
# every log off and prints the timeline.
#   llvm-rerun.sh <commit the run releases from>
set -u
COMMIT=$1
S=$(cat /tmp/dispat-gce/secret.txt)
D=/private/tmp/claude-501/-Users-yohimik-Projects-dispat/aba20193-908a-4dbf-a0ef-363528c9fa79/scratchpad/llvm-logs
mkdir -p "$D"
ssh_() { local host=$1; shift; perl -e 'alarm 900; exec @ARGV' -- gcloud compute ssh "$host" --project dispat --zone us-central1-a --command "$*" 2>&1; }
scp_() { perl -e 'alarm 900; exec @ARGV' -- gcloud compute scp --project dispat --zone us-central1-a "$@" 2>&1 | grep -v '^$'; }
timeline() { grep -o '"time":"[^"]*",[^}]*"message":"\(release plan ready\|task assigned\|task finished\|outputs admitted\|publication authorized\|build script failed\|stage started\|stage succeeded\|stage failed\|package published\|done\)"' "$1" | sed -E 's/"time":"([^"]+)".*"task":"([^"]+)".*"message":"([^"]+)"/\1 \2 \3/; s/"time":"([^"]+)".*"package":"([^"]+)".*"stage":"([^"]+)".*"message":"([^"]+)"/\1 \2:\3 \4/; s/"time":"([^"]+)".*"message":"([^"]+)"/\1 \2/'; }

for i in $(seq 1 90); do
    n=$(ssh_ lb-w2 "if [ -f ~/release-local.time ] && [ \$(pgrep -x dispat | wc -l) = 0 ]; then echo over; else echo running; fi" | tail -1)
    case "$n" in over) break ;; esac
    sleep 60
done
echo "$(date -u +%T) the baseline on lb-w2 is over ($n)"

echo "$(date -u +%T) resetting the orchestrator's records to $COMMIT"
ssh_ lb-orch "cd ~/llvm && git reset -q --hard $COMMIT && git tag -l 'dispat/*/v24.1.0' 'dispat-release-lock*' | xargs -r git tag -d >/dev/null; for t in \$(git --git-dir ~/origin.git tag); do git --git-dir ~/origin.git tag -d \$t >/dev/null; done; git --git-dir ~/origin.git for-each-ref --format='%(refname)' refs/heads | grep dispat-worker | xargs -r -n1 git --git-dir ~/origin.git update-ref -d; git push -q -f origin dispat-gce; echo origin-tip: \$(git --git-dir ~/origin.git rev-parse --short dispat-gce) tags: \$(git --git-dir ~/origin.git tag | wc -l); rm -rf llvm/_dispat lld/_dispat polly/_dispat .ci/dispat/bundle/_dispat; dispat status --config dispat.gce.yaml 2>&1 | grep -c 'changed'" | tail -3

echo "$(date -u +%T) restarting the worker on lb-w2"
ssh_ lb-w2 "cd ~ && nohup env DISPAT_EXECUTION_SECRET=$S dispat worker --root ~/node --state-dir ~/state --idle-timeout 0 --log-level debug > ~/worker.log 2>&1 < /dev/null & sleep 5; pgrep -x dispat | wc -l" | tail -1
ssh_ lb-w1 "pgrep -x dispat | wc -l" | tail -1

echo "$(date -u +%T) starting the distributed release on lb-orch"
ssh_ lb-orch "cd ~/llvm && date -u +%FT%TZ > ~/release-dist3.start && nohup env DISPAT_EXECUTION_SECRET=$S /usr/bin/time -v -o ~/release-dist3.time dispat release --config dispat.gce.yaml --log-format json --log-level debug > ~/release-dist3.log 2>&1 < /dev/null & sleep 30; grep -o '\"time\":\"[^\"]*\",[^}]*\"message\":\"\(release plan ready\|worker ready\|task assigned\)\"' ~/release-dist3.log | sed -E 's/\"time\":\"([^\"]+)\".*\"message\":\"([^\"]+)\"/\1 \2/'" | tail -5

for i in $(seq 1 120); do
    n=$(ssh_ lb-orch "pgrep -x dispat | wc -l" | tail -1)
    case "$n" in 0) break ;; esac
    sleep 60
done
echo "$(date -u +%T) distributed release exited (pgrep=$n)"
scp_ lb-orch:release-dist3.log "$D/release-dist3.log"
scp_ lb-orch:release-dist3.time "$D/release-dist3.time"
scp_ lb-orch:release-dist3.start "$D/release-dist3.start"
scp_ lb-w1:worker.log "$D/worker-lb-w1-dist3.log"
scp_ lb-w2:worker.log "$D/worker-lb-w2-dist3.log"
cat "$D/release-dist3.start"; grep -E 'Elapsed|Exit status' "$D/release-dist3.time"
timeline "$D/release-dist3.log" | tail -40
ssh_ lb-orch "cd ~/llvm && git log --oneline -2 | cat; git tag | grep v24.1 | tr '\n' ' '; echo; du -sh llvm/_dispat/install lld/_dispat/install polly/_dispat/install .ci/dispat/bundle/_dispat/dist 2>&1" | tail -8
echo "$(date -u +%T) DISTRIBUTED RUN 3 DONE"
