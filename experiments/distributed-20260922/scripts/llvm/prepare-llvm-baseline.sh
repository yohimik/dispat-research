#!/bin/bash
# Runs on the worker that becomes the single node of the baseline: a clone of
# the orchestrator's origin at the trigger commit, with no release tag of the
# distributed run, and a bare origin of its own for the release lock.
set -eu
: "${MAILBOX_URL:?}" "${FORK_BRANCH:?}" "${SOURCE_COMMIT:?}"
rm -rf ~/llvm-src ~/origin-local.git
node-run git clone -q --branch "${FORK_BRANCH}" "${MAILBOX_URL}" ~/llvm-src
cd ~/llvm-src
git checkout -q -B "${FORK_BRANCH}" "${SOURCE_COMMIT}"
# Only the baselines may exist: a tag the distributed run wrote would empty the plan.
for tag in $(git tag -l 'dispat/*' | grep -v '/v[0-9]*\.0\.0$'); do git tag -d "${tag}" >/dev/null; done
git clone -q --bare ~/llvm-src ~/origin-local.git
git remote set-url origin ~/origin-local.git
git push -q origin "${FORK_BRANCH}" --tags
sed -e "s#@SOURCE@#${SOURCE_COMMIT}#" .ci/dispat/gce/dispat.local.yaml > dispat.local.yaml
echo "baseline checkout at ~/llvm-src, origin ~/origin-local.git"
