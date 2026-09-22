#!/bin/bash
# Runs on the round-2 orchestrator VM, which both coordinates the release and
# builds the cells pinned to it. It installs the binary, creates the mailbox
# repository the workers reach over ssh, authorises their key and makes a Git
# repository out of the image-only harness export.
#
#   dispat/gce/orchestrator-round2.sh
#
# Expects in the current folder: dispat (the binary), farm.tgz (the export
# dispat/export-build-harness.py writes, tarred) and mailbox_key.pub. Release
# configurations are generated afterwards, one per architecture group, so the
# topology can be chosen from the calibration.
set -eu
ref=${KERNEL_REF:-v7.3-rc4}

sudo install -m 0755 dispat /usr/local/bin/dispat
mkdir -p ~/.ssh
cat mailbox_key.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys
git config --global user.email orchestrator@dispat.invalid
git config --global user.name "dispat orchestrator"

rm -rf ~/mailbox.git ~/farm
git init -q --bare ~/mailbox.git
mkdir -p ~/farm
tar -xzf farm.tgz -C ~/farm
cd ~/farm
git init -q -b dispat-prototype
git add -A
git commit -q -m "feat(kernel)^^: test ${ref}" \
    -m 'Image-only export of the farm harness: the QEMU and rootfs assets no
cell of this run reads are left out, so the source snapshot the release
transports is kilobytes rather than gigabytes.'
# The release takes its lock as a tag on `origin` and pushes the source
# snapshot the workers read. Source and coordination refs share the mailbox, so
# a worker reaches both over the one ssh endpoint it is given.
git remote add origin "${HOME}/mailbox.git"
git push -q --set-upstream origin dispat-prototype
echo "farm repository at ~/farm, commit $(git rev-parse --short HEAD)"
echo "mailbox at ${HOME}/mailbox.git"
