#!/bin/bash
# Installs the dispat binary built from main on the three LLVM machines and
# restarts both workers (detached with setsid). Prints each machine's binary
# digest afterwards. Usage: llvm-reinstall.sh
set -u
S=$(cat /tmp/dispat-gce/secret.txt)
ssh_() { local host=$1; shift; perl -e 'alarm 600; exec @ARGV' -- gcloud compute ssh "$host" --project dispat --zone us-central1-a --command "$*" 2>&1; }
scp_() { perl -e 'alarm 600; exec @ARGV' -- gcloud compute scp --project dispat --zone us-central1-a "$@" 2>&1 | grep -v '^$'; }
echo "local: $(shasum -a 256 /tmp/dispat-gce/dispat | cut -c1-16)"
HOSTS=${*:-lb-orch lb-w1 lb-w2}
for h in $HOSTS; do
    scp_ /tmp/dispat-gce/dispat $h:~/dispat.new
    ssh_ $h "sudo install -m 0755 ~/dispat.new /usr/local/bin/dispat && echo $h: \$(sha256sum /usr/local/bin/dispat | cut -c1-16)" | tail -1
done
for h in $HOSTS; do
    [ "$h" = lb-orch ] && continue
    ssh_ $h "pkill -x dispat; sleep 2; cd ~ && rm -rf ~/state/tasks; setsid -f env DISPAT_EXECUTION_SECRET=$S dispat worker --root ~/node --state-dir ~/state --idle-timeout 0 --log-level debug > ~/worker.log 2>&1 < /dev/null; sleep 3; echo $h workers: \$(pgrep -x dispat | wc -l)" | tail -1
done
