#!/bin/bash
# Put the farm repository back into the state a first release sees.
#
#   dispat/gce/reset-release-tags.sh
#
# A release tags every package it completed, and a package whose content has
# not changed since its tag is not planned again. A benchmark needs the same
# plan in every trial, so the trials that measure one topology start from no
# release tags. Nothing else about the repository changes, and no tag of the
# kernel under test is touched: those live in the kernel cache, not here.
set -eu
cd ~/farm
tags=$(git tag -l | grep -E '^(kernel|build-)' || true)
if [ -n "${tags}" ]; then
    # shellcheck disable=SC2086
    git tag -d ${tags} > /dev/null
fi
echo "release tags removed: $(printf '%s' "${tags}" | grep -c . || true)"
