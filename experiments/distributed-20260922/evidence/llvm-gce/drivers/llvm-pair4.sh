#!/bin/bash
# Fourth LLVM parity pair (matrix fixture: llvm X86 + llvm AArch64 + lld + polly + cheap bundle), one script: applies the recipe patch on the
# orchestrator, resets the records, runs the distributed release (workers w1,
# w2) under /usr/bin/time, then the single-node baseline on lb-w2 from the same
# commit, copies every log off, brings the distributed products to lb-w2 and
# runs the comparison. Remote daemons are started with setsid so gcloud's ssh
# session is not held open by them.
#   llvm-pair3.sh <patch file> <tag of the run: e.g. dist4/local3>
set -u
PATCH=$1
S=$(cat /tmp/dispat-gce/secret.txt)
D=/private/tmp/claude-501/-Users-yohimik-Projects-dispat/aba20193-908a-4dbf-a0ef-363528c9fa79/scratchpad/llvm-logs
mkdir -p "$D"
ssh_() { local host=$1; shift; perl -e 'alarm 900; exec @ARGV' -- gcloud compute ssh "$host" --project dispat --zone us-central1-a --command "$*" 2>&1; }
scp_() { perl -e 'alarm 900; exec @ARGV' -- gcloud compute scp --project dispat --zone us-central1-a "$@" 2>&1 | grep -v '^$'; }
timeline() { grep -o '"time":"[^"]*",[^}]*"message":"\(release plan ready\|task assigned\|task finished\|outputs admitted\|publication authorized\|build started\|build succeeded\|build script failed\|package published\|done\)"' "$1" | sed -E 's/"time":"([^"]+)".*"task":"([^"]+)".*"message":"([^"]+)"/\1 \2 \3/; s/"time":"([^"]+)".*"package":"([^"]+)".*"message":"([^"]+)"/\1 \2 \3/; s/"time":"([^"]+)".*"message":"([^"]+)"/\1 \2/'; }
waitfor() { local host=$1; for i in $(seq 1 120); do n=$(ssh_ "$host" "pgrep -x dispat | wc -l" | tail -1); case "$n" in 0) return 0 ;; esac; sleep 60; done; return 1; }

echo "$(date -u +%T) applying the recipe patch on lb-orch"
scp_ "$PATCH" lb-orch:~/recipe.patch
scp_ /private/tmp/claude-501/-Users-yohimik-Projects-dispat/aba20193-908a-4dbf-a0ef-363528c9fa79/scratchpad/rootconfig.py lb-orch:~/rootconfig.py
ssh_ lb-orch "cd ~/llvm && git am -q ~/recipe.patch && python3 ~/rootconfig.py && git tag -f dispat/llvm-aarch64/v24.0.0 a9f4d3ff >/dev/null && git push -q -f origin refs/tags/dispat/llvm-aarch64/v24.0.0 && git tag -l 'dispat/*/v24.1.0' 'dispat-release-lock*' | xargs -r git tag -d >/dev/null; for t in \$(git --git-dir ~/origin.git tag | grep -v v24.0.0); do git --git-dir ~/origin.git tag -d \$t >/dev/null; done; git --git-dir ~/origin.git for-each-ref --format='%(refname)' refs/heads | grep dispat-worker | xargs -r -n1 git --git-dir ~/origin.git update-ref -d; git push -q -f origin dispat-gce; rm -rf llvm/_dispat .ci/dispat/llvm-aarch64/_dispat lld/_dispat polly/_dispat .ci/dispat/bundle/_dispat; echo tip: \$(git rev-parse --short HEAD) origin-tip: \$(git --git-dir ~/origin.git rev-parse --short dispat-gce) origin-tags: \$(git --git-dir ~/origin.git tag | tr '\n' ' '); dispat status --config dispat.gce.yaml 2>&1 | grep -c '24.0.0 -> 24.1.0'" | tail -3
COMMIT=$(ssh_ lb-orch "cd ~/llvm && git rev-parse HEAD" | tail -1)
echo "commit under test: $COMMIT"

echo "$(date -u +%T) making sure both workers serve"
ssh_ lb-w2 "pkill -x dispat; sleep 2; cd ~ && rm -rf ~/state/tasks; setsid -f env DISPAT_EXECUTION_SECRET=$S dispat worker --root ~/node --state-dir ~/state --idle-timeout 0 --log-level debug > ~/worker.log 2>&1 < /dev/null; sleep 3; pgrep -x dispat | wc -l" | tail -1
ssh_ lb-w1 "pgrep -x dispat | wc -l || true; [ \$(pgrep -x dispat | wc -l) = 0 ] && setsid -f env DISPAT_EXECUTION_SECRET=$S dispat worker --root ~/node --state-dir ~/state --idle-timeout 0 --log-level debug > ~/worker.log 2>&1 < /dev/null; sleep 3; pgrep -x dispat | wc -l" | tail -1

echo "$(date -u +%T) starting the distributed release on lb-orch"
ssh_ lb-orch "cd ~/llvm && rm -f ~/release-dist5.time && date -u +%FT%TZ > ~/release-dist5.start && setsid -f env DISPAT_EXECUTION_SECRET=$S /usr/bin/time -v -o ~/release-dist5.time dispat release --config dispat.gce.yaml --log-format json --log-level debug > ~/release-dist5.log 2>&1 < /dev/null; sleep 30; grep -o '\"time\":\"[^\"]*\",[^}]*\"message\":\"\(release plan ready\|worker ready\|task assigned\)\"' ~/release-dist5.log | sed -E 's/\"time\":\"([^\"]+)\".*\"message\":\"([^\"]+)\"/\1 \2/'" | tail -5
waitfor lb-orch
echo "$(date -u +%T) distributed release exited"
for f in release-dist5.log release-dist5.time release-dist5.start; do scp_ lb-orch:$f "$D/$f"; done
scp_ lb-w1:worker.log "$D/worker-lb-w1-dist4.log"; scp_ lb-w2:worker.log "$D/worker-lb-w2-dist4.log"
cat "$D/release-dist5.start"; grep -E 'Elapsed|Exit status' "$D/release-dist5.time"
timeline "$D/release-dist5.log" | tail -30
grep -o '"published":[0-9]*,"failed":[0-9]*[^}]*"took":[0-9.]*' "$D/release-dist5.log" | tail -1

echo "$(date -u +%T) refreshing the baseline clone on lb-w2 to $COMMIT"
ssh_ lb-w2 "pkill -x dispat; sleep 2; cd ~/llvm-src && git remote set-url origin ssh://yohimik@10.128.0.9/home/yohimik/origin.git && git fetch -q origin dispat-gce 'refs/tags/dispat/*/v24.0.0:refs/tags/dispat/*/v24.0.0' && git tag -l 'dispat/*/v24.1.0' 'dispat-release-lock*' | xargs -r git tag -d >/dev/null; git checkout -q -B dispat-gce $COMMIT && rm -rf ~/origin-local.git && git clone -q --bare ~/llvm-src ~/origin-local.git && git remote set-url origin ~/origin-local.git && git fetch -q origin && rm -rf llvm/_dispat .ci/dispat/llvm-aarch64/_dispat lld/_dispat polly/_dispat .ci/dispat/bundle/_dispat && scp -q yohimik@10.128.0.9:llvm/dispat.yaml yohimik@10.128.0.9:llvm/dispat.local.yaml ~/llvm-src/ && git log --oneline -1 | cat && dispat status --config dispat.local.yaml 2>&1 | grep -c '24.0.0 -> 24.1.0'" | tail -3

echo "$(date -u +%T) starting the baseline on lb-w2"
ssh_ lb-w2 "cd ~/llvm-src && rm -f ~/release-local3.time && date -u +%FT%TZ > ~/release-local3.start && setsid -f env DISPAT_EXECUTION_SECRET=$S /usr/bin/time -v -o ~/release-local3.time dispat release --config dispat.local.yaml --log-format json --log-level debug > ~/release-local3.log 2>&1 < /dev/null; sleep 20; grep -c 'release plan ready' ~/release-local3.log" | tail -1
waitfor lb-w2
echo "$(date -u +%T) baseline exited"
for f in release-local3.log release-local3.time release-local3.start; do scp_ lb-w2:$f "$D/$f"; done
cat "$D/release-local3.start"; grep -E 'Elapsed|Exit status' "$D/release-local3.time"
timeline "$D/release-local3.log" | tail -24
grep -o '"published":[0-9]*,"failed":[0-9]*[^}]*"took":[0-9.]*' "$D/release-local3.log" | tail -1

echo "$(date -u +%T) bringing the distributed products to lb-w2 and comparing"
ssh_ lb-w2 "rm -rf ~/llvm-dist && mkdir -p ~/llvm-dist && ssh yohimik@10.128.0.9 'cd ~/llvm && tar cf - llvm/_dispat .ci/dispat/llvm-aarch64/_dispat lld/_dispat polly/_dispat .ci/dispat/bundle/_dispat' | tar xf - -C ~/llvm-dist && du -sh ~/llvm-dist && cd ~/llvm-src && python3 .ci/dispat/gce/compare.py ~/llvm-src ~/llvm-dist" | tail -20
echo "$(date -u +%T) PAIR 3 DONE"
