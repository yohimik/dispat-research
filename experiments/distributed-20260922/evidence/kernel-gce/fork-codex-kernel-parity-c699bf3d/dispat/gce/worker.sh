#!/bin/bash
# Runs on a worker VM after worker-startup.sh has finished: installs the
# dispat binary and the key that reaches the mailbox, writes this node's
# configuration and starts serving.
# Arguments: <node name> <mailbox url> [build slots, default 1].
#
#   dispat/gce/worker.sh w1 ssh://user@10.0.0.2/home/user/mailbox.git 3
#
# Expects in the current folder: dispat (the binary), mailbox_key (the private
# key the orchestrator VM authorises), and DISPAT_EXECUTION_SECRET in the
# environment.
set -eu
name=$1
mailbox=$2
# One slot per cell this node may build at once. Budget make jobs across them.
slots=${3:-1}
: "${DISPAT_EXECUTION_SECRET:?the signing secret}"

until [ -e /var/lib/dispat-worker-ready ]; do sleep 5; done

sudo install -m 0755 dispat /usr/local/bin/dispat
mkdir -p ~/.ssh ~/node ~/state
install -m 0600 mailbox_key ~/.ssh/mailbox_key
host=$(echo "${mailbox}" | sed -E 's#^ssh://[^@]*@([^/:]+).*#\1#')
ssh-keyscan -H "${host}" >> ~/.ssh/known_hosts 2>/dev/null
cat > ~/.ssh/config <<EOF
Host ${host}
  IdentityFile ~/.ssh/mailbox_key
  IdentitiesOnly yes
EOF
cat > ~/node/dispat.json <<EOF
{
  "execution": {
    "role": "worker",
    "name": "${name}",
    "endpoint": "${mailbox}",
    "secretEnv": "DISPAT_EXECUTION_SECRET",
    "concurrency": ${slots}
  },
  "logFormat": "json"
}
EOF
# The kernel scripts read the checkout's own git identity for nothing, but
# git itself refuses a worktree add without one on some versions.
git config --global user.email worker@dispat.invalid
git config --global user.name "dispat worker"
# A cell reads these from the worker's own environment: dispat reserves the
# DISPAT_ prefix inside a package's env, and they say where this node keeps its
# prepared source trees and the evidence a cell leaves behind.
export DISPAT_FARM_SOURCE_POOL=${DISPAT_FARM_SOURCE_POOL:-/srv/farm/src}
export DISPAT_FARM_RESULTS=${DISPAT_FARM_RESULTS:-/srv/farm/results}
# The measured engine can stop accepting work during a long build when its
# idle timer fires. VM lifetime controls cleanup until that defect is fixed.
nohup dispat worker --root ~/node --state-dir ~/state --idle-timeout 0 --log-level debug \
    > ~/worker.log 2>&1 &
echo "worker ${name} started, pid $!"
