#!/bin/bash
# Sixth distributed attempt (recipe with fingerprint records), then the comparison against the baseline products already on lb-w2: applies the recipe patch on the
# orchestrator, resets the records, runs the distributed release (workers w1,
# w2) under /usr/bin/time, then the single-node baseline on lb-w2 from the same
# commit, copies every log off, brings the distributed products to lb-w2 and
# runs the comparison. Remote daemons are started with setsid so gcloud's ssh
# session is not held open by them.
#   llvm-pair3.sh <patch file> <tag of the run: e.g. dist4/local3>
set -u
S=$(cat /tmp/dispat-gce/secret.txt)
D=/private/tmp/claude-501/-Users-yohimik-Projects-dispat/aba20193-908a-4dbf-a0ef-363528c9fa79/scratchpad/llvm-logs
mkdir -p "$D"
ssh_() { local host=$1; shift; perl -e 'alarm 900; exec @ARGV' -- gcloud compute ssh "$host" --project dispat --zone us-central1-a --command "$*" 2>&1; }
scp_() { perl -e 'alarm 900; exec @ARGV' -- gcloud compute scp --project dispat --zone us-central1-a "$@" 2>&1 | grep -v '^$'; }
timeline() { grep -o '"time":"[^"]*",[^}]*"message":"\(release plan ready\|task assigned\|task finished\|outputs admitted\|publication authorized\|build started\|build succeeded\|build script failed\|package published\|done\)"' "$1" | sed -E 's/"time":"([^"]+)".*"task":"([^"]+)".*"message":"([^"]+)"/\1 \2 \3/; s/"time":"([^"]+)".*"package":"([^"]+)".*"message":"([^"]+)"/\1 \2 \3/; s/"time":"([^"]+)".*"message":"([^"]+)"/\1 \2/'; }
waitfor() { local host=$1; for i in $(seq 1 120); do n=$(ssh_ "$host" "pgrep -x dispat | wc -l" | tail -1); case "$n" in 0) return 0 ;; esac; sleep 60; done; return 1; }

echo "$(date -u +%T) resetting the records of the failed run on lb-orch"
ssh_ lb-orch "cd ~/llvm && git tag -l 'dispat/*/v24.1.0' 'dispat-release-lock*' | xargs -r git tag -d >/dev/null; for t in \$(git --git-dir ~/origin.git tag | grep -v v24.0.0); do git --git-dir ~/origin.git tag -d \$t >/dev/null; done; git --git-dir ~/origin.git for-each-ref --format='%(refname)' refs/heads | grep dispat-worker | xargs -r -n1 git --git-dir ~/origin.git update-ref -d; git reset -q --hard \$(git rev-parse HEAD); git push -q -f origin dispat-gce; rm -rf llvm/_dispat .ci/dispat/llvm-aarch64/_dispat lld/_dispat polly/_dispat .ci/dispat/bundle/_dispat; echo tip: \$(git rev-parse --short HEAD) origin-tags: \$(git --git-dir ~/origin.git tag | wc -l); dispat status --config dispat.gce.yaml 2>&1 | grep -c '24.0.0 -> 24.1.0'; dispat version 2>/dev/null | head -1" | tail -3
COMMIT=$(ssh_ lb-orch "cd ~/llvm && git rev-parse HEAD" | tail -1)
echo "commit under test: $COMMIT"

echo "$(date -u +%T) making sure both workers serve"
ssh_ lb-w2 "pkill -x dispat; sleep 2; cd ~ && rm -rf ~/state/tasks; setsid -f env DISPAT_EXECUTION_SECRET=$S dispat worker --root ~/node --state-dir ~/state --idle-timeout 0 --log-level debug > ~/worker.log 2>&1 < /dev/null; sleep 3; pgrep -x dispat | wc -l" | tail -1
ssh_ lb-w1 "pgrep -x dispat | wc -l || true; [ \$(pgrep -x dispat | wc -l) = 0 ] && setsid -f env DISPAT_EXECUTION_SECRET=$S dispat worker --root ~/node --state-dir ~/state --idle-timeout 0 --log-level debug > ~/worker.log 2>&1 < /dev/null; sleep 3; pgrep -x dispat | wc -l" | tail -1

echo "$(date -u +%T) starting the distributed release on lb-orch"
ssh_ lb-orch "cd ~/llvm && rm -f ~/release-dist6.time && date -u +%FT%TZ > ~/release-dist6.start && setsid -f env DISPAT_EXECUTION_SECRET=$S /usr/bin/time -v -o ~/release-dist6.time dispat release --config dispat.gce.yaml --log-format json --log-level debug > ~/release-dist6.log 2>&1 < /dev/null; sleep 30; grep -o '\"time\":\"[^\"]*\",[^}]*\"message\":\"\(release plan ready\|worker ready\|task assigned\)\"' ~/release-dist6.log | sed -E 's/\"time\":\"([^\"]+)\".*\"message\":\"([^\"]+)\"/\1 \2/'" | tail -5
waitfor lb-orch
echo "$(date -u +%T) distributed release exited"
for f in release-dist6.log release-dist6.time release-dist6.start; do scp_ lb-orch:$f "$D/$f"; done
scp_ lb-w1:worker.log "$D/worker-lb-w1-dist4.log"; scp_ lb-w2:worker.log "$D/worker-lb-w2-dist4.log"
cat "$D/release-dist6.start"; grep -E 'Elapsed|Exit status' "$D/release-dist6.time"
timeline "$D/release-dist6.log" | tail -30
grep -o '"published":[0-9]*,"failed":[0-9]*[^}]*"took":[0-9.]*' "$D/release-dist6.log" | tail -1

echo "$(date -u +%T) bringing the distributed products to lb-w2 and comparing (baseline products of the matrix run stay in ~/llvm-src)"
scp_ /Users/yohimik/Projects/llvm-project/.ci/dispat/gce/compare.py lb-w2:~/compare.py
ssh_ lb-w2 "rm -rf ~/llvm-dist && mkdir -p ~/llvm-dist && ssh yohimik@10.128.0.9 'cd ~/llvm && tar cf - llvm/_dispat .ci/dispat/llvm-aarch64/_dispat lld/_dispat polly/_dispat .ci/dispat/bundle/_dispat' | tar xf - -C ~/llvm-dist && du -sh ~/llvm-dist && python3 ~/compare.py ~/llvm-src ~/llvm-dist" | tail -24
echo "$(date -u +%T) DISTRIBUTED RUN 8 DONE"
