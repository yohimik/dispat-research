#!/bin/bash
# The same two recipes as the winning trials, with no worker to place on: every
# cell runs on the machine that starts the release, at the same make jobs and
# the same build-slot count. Only the worker is gone.
set -eu
cd ~/farm
common=(--workers w1 --mailbox "${HOME}/mailbox.git" --qemu '' --task-timeout 7200
        --split-configs --no-workers
        --env FARM_GCC_CURRENT=16.2.0-2.47)

python3 dispat/generate.py "${common[@]}" \
    --arches hexagon --jobs 12 --concurrency 2 \
    --orchestrator hexagon:defconfig,hexagon:tinyconfig \
    --cell-jobs hexagon:defconfig=24 --cell-jobs hexagon:tinyconfig=9 \
    > dispat.hexagon.solo.yaml

python3 dispat/generate.py "${common[@]}" \
    --arches m68k_nommu --jobs 12 --concurrency 4 \
    --orchestrator m68k_nommu:m5272c3_defconfig,m68k_nommu:m5307c3_defconfig \
    --orchestrator m68k_nommu:m5249evb_defconfig,m68k_nommu:m5407c3_defconfig \
    --cell-jobs m68k_nommu:m5272c3_defconfig=8,m68k_nommu:m5307c3_defconfig=8 \
    --cell-jobs m68k_nommu:m5249evb_defconfig=8,m68k_nommu:m5407c3_defconfig=8 \
    > dispat.m68k_nommu.solo.yaml

git add -A
git commit -q -m 'chore: run the same cells on one node' \
    -m 'The same placement, make jobs and build slots as the paired trials, with
no worker: the comparison the specification owner asked for keeps the hardware
of the machine that starts the release fixed and removes the second machine.'
grep -c '^  build-' dispat.hexagon.solo.yaml dispat.m68k_nommu.solo.yaml
grep -h '^runOnly' dispat.hexagon.solo.yaml
grep -c 'workers:' dispat.hexagon.solo.yaml dispat.m68k_nommu.solo.yaml || true
