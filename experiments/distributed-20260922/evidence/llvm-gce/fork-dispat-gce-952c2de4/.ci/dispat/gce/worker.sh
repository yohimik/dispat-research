#!/bin/bash
# Runs on a worker VM after worker-startup.sh has finished: installs the
# dispat binary and the key that reaches the mailbox, writes this node's
# configuration and starts serving until it is signalled.
# Arguments: <node name> <mailbox url>. Expects in the current folder: dispat,
# mailbox_key, and DISPAT_EXECUTION_SECRET in the environment.
set -eu
name=$1
mailbox=$2
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
    "concurrency": 1,
    "transfer": {"maxFiles": 250000, "maxBytes": 68719476736,
                 "maxManifestBytes": 134217728, "timeout": 3600}
  },
  "logFormat": "json"
}
EOF
git config --global user.email worker@dispat.invalid
git config --global user.name "dispat worker"
nohup dispat worker --root ~/node --state-dir ~/state --idle-timeout 0 --log-level debug \
    > ~/worker.log 2>&1 < /dev/null &
echo "worker ${name} started, pid $!"
