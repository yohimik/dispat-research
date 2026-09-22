#!/bin/bash
# Runs on the orchestrator VM: clones this fork, records the baseline tags the plan
# starts from, applies the experiment files carried in gce.tar, commits the
# change that puts every package into the plan, creates the mailbox and
# writes the run's configuration.
# Arguments: <fork url> <branch>
#
#   .ci/dispat/gce/orchestrator.sh https://github.com/yohimik/llvm-project.git main
#
# Expects in the current folder: dispat (the binary), gce.tar (the experiment
# files: .ci/dispat/gce, the patched .ci/dispat/build.py) and mailbox_key.pub.
set -eu
fork=$1
branch=$2

sudo apt-get install -y -q git python3 >/dev/null
sudo install -m 0755 dispat /usr/local/bin/dispat
mkdir -p ~/.ssh
cat mailbox_key.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys
git config --global user.email orchestrator@dispat.invalid
git config --global user.name "dispat orchestrator"

# A full clone: the release lock and the branch are pushed to a local bare
# copy of it, and a push has to carry every object its commits reach, which a
# partial clone does not hold. That bare copy is also the mailbox: a snapshot
# pushed there finds its ancestor and carries only the working tree's changes,
# where a separate empty mailbox would receive the whole history on every run.
if [ ! -d ~/llvm ]; then
    git clone -q -b "${branch}" "${fork}" ~/llvm
fi
[ -d ~/origin.git ] || git clone -q --bare ~/llvm ~/origin.git
cd ~/llvm
git checkout -q -B dispat-gce
# The plan starts after these: the window it reads is the experiment's own
# commits, not the fork's history. The baseline major is the source's own,
# because build.py refuses a release whose major differs from LLVMVersion.cmake.
major=$(grep -o 'LLVM_VERSION_MAJOR [0-9]*' cmake/Modules/LLVMVersion.cmake | grep -o '[0-9]*$')
for p in llvm clang lld polly toolchain; do
    git tag -f "dispat/${p}/v${major}.0.0" HEAD >/dev/null
done
tar -xf ~/gce.tar
git remote set-url origin ~/origin.git
git add .ci/dispat .gitignore
git commit -q -m "chore: carry the Compute Engine experiment files"
# The change that carries every package into the plan.
printf '\n// dispat timing experiment %s\n' "$(date -u +%FT%TZ)" >> llvm/lib/Support/Unix/Unix.h.experiment
git add llvm/lib/Support/Unix/Unix.h.experiment
git commit -q -m "feat(llvm)^^: time a distributed build on Compute Engine workers"
git push -q origin dispat-gce
source=$(git rev-parse HEAD)
# The template lives three folders down; its references are written for the
# repository root, where the run reads the filled copy.
sed -e "s#@SOURCE@#${source}#" -e "s#@MAILBOX@#${HOME}/origin.git#" .ci/dispat/gce/dispat.gce.yaml > dispat.gce.yaml
sed -e "s#@SOURCE@#${source}#" .ci/dispat/gce/dispat.local.yaml > dispat.local.yaml
echo "source ${source}"
dispat status --config dispat.gce.yaml --log-format json 2>&1 | grep -E '"message":"(release plan ready|refusing|plan fixed)"|"level":"error"' | cut -c1-240
echo "distributed: cd ~/llvm && DISPAT_EXECUTION_SECRET=... dispat release --config dispat.gce.yaml --log-format json --log-level debug > ~/release.log 2>&1 < /dev/null &"
echo "baseline:    cd ~/llvm && dispat release --config dispat.local.yaml --log-format json --log-level debug > ~/release-local.log 2>&1 < /dev/null &"
