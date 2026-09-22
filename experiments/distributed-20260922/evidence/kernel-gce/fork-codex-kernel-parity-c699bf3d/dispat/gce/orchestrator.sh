#!/bin/bash
# Runs on the orchestrator VM: unpacks the farm repository from its bundle,
# creates the mailbox repository the workers reach over ssh, authorises the
# workers' key and writes the run's configuration.
# Arguments: <worker names, comma-separated> <arches, comma-separated>.
#
#   dispat/gce/orchestrator.sh w1,w2,w3 x86_64,i386,arm64
#
# Expects in the current folder: dispat (the binary), farm.bundle, and
# mailbox_key.pub. The release itself is started by hand afterwards, so its
# log is the operator's to watch.
set -eu
workers=$1
arches=$2

sudo apt-get install -y -q git python3 >/dev/null
sudo install -m 0755 dispat /usr/local/bin/dispat
mkdir -p ~/.ssh
cat mailbox_key.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys
git config --global user.email orchestrator@dispat.invalid
git config --global user.name "dispat orchestrator"

git init -q --bare ~/mailbox.git
[ -d ~/farm ] || git clone -q -b dispat-prototype farm.bundle ~/farm
cd ~/farm
python3 dispat/generate.py --workers "${workers}" --mailbox "${HOME}/mailbox.git" \
    --arches "${arches}" --qemu '' --task-timeout 7200 > dispat.gce.yaml
echo "configured: $(grep -c '^  build-' dispat.gce.yaml) cells, workers ${workers}"
echo "run: cd ~/farm && DISPAT_EXECUTION_SECRET=... dispat release --config dispat.gce.yaml --log-format json --log-level debug > ~/release.log 2>&1"
