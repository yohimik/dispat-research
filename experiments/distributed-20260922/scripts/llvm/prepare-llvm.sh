#!/bin/bash
# Runs on the orchestrator: the fork at its pinned commit, the baseline tags,
# the trigger commit, the bare origin that doubles as the mailbox, and the
# two run configurations filled from their templates. Compare
# .ci/dispat/gce/orchestrator.sh of the fork, whose steps these are.
set -eu
: "${FORK:?}" "${FORK_BRANCH:?}" "${FORK_COMMIT:?}" "${BASELINE_COMMIT:?}"
rm -rf ~/llvm ~/origin.git
# A full clone: the release pushes its lock and the branch to a local bare
# copy, and a push has to carry every object its commits reach.
node-run git clone -q --branch "${FORK_BRANCH}" "${FORK}" ~/llvm
cd ~/llvm
git checkout -q -B "${FORK_BRANCH}" "${FORK_COMMIT}"
major=$(grep -o 'LLVM_VERSION_MAJOR [0-9]*' cmake/Modules/LLVMVersion.cmake | grep -o '[0-9]*$')
# The plan starts after these: the window it reads is the fork's own commits
# above the LLVM main commit, plus the trigger below. The baseline major is
# the source's own, because build.py refuses a release whose major differs.
for p in llvm llvm-aarch64 clang lld polly toolchain; do
    git tag -f "dispat/${p}/v${major}.0.0" "${BASELINE_COMMIT}" >/dev/null
done
# The change that carries every package into the plan.
printf '\n// dispat timing experiment %s\n' "$(date -u +%FT%TZ)" >> llvm/lib/Support/Unix/Unix.h.experiment
git add llvm/lib/Support/Unix/Unix.h.experiment
git commit -q -m "feat(llvm)^^: time a distributed build on Compute Engine workers"
# The bare copy is the mailbox as well: a snapshot pushed there finds its
# ancestor and carries only the working tree's changes.
git clone -q --bare ~/llvm ~/origin.git
git -C ~/origin.git tag -l 'dispat/*' >/dev/null
git remote set-url origin ~/origin.git
git push -q origin "${FORK_BRANCH}" --tags
source=$(git rev-parse HEAD)
sed -e "s#@SOURCE@#${source}#" -e "s#@MAILBOX@#${HOME}/origin.git#" .ci/dispat/gce/dispat.gce.yaml > dispat.gce.yaml
sed -e "s#@SOURCE@#${source}#" .ci/dispat/gce/dispat.local.yaml > dispat.local.yaml
echo "source ${source}; origin and mailbox at ~/origin.git"
