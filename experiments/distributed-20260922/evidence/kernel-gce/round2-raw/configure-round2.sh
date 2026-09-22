#!/bin/bash
# Writes the two round-2 release configurations the calibration justified and
# commits them with the cell folders, so the source snapshot the release
# transports carries them.
set -eu
cd ~/farm
common=(--workers w1 --mailbox "${HOME}/mailbox.git" --qemu '' --task-timeout 7200
        --split-configs --publish-on-orchestrator
        --env FARM_GCC_CURRENT=16.2.0-2.47)
# DISPAT_FARM_SOURCE_POOL and DISPAT_FARM_RESULTS say where this node keeps its
# prepared trees and its evidence. They are node settings, and dispat reserves
# the DISPAT_ prefix in a package's env, so they reach a cell from the
# environment of the worker or of the release that runs it.

# hexagon, reference 111 s. defconfig is the long pole and stays on the fast
# machine with most of its jobs; tinyconfig shares that machine's second slot;
# allnoconfig is the one cell a t2d-standard-8 can finish inside the budget.
python3 dispat/generate.py "${common[@]}" \
    --arches hexagon --jobs 12 --concurrency 2 \
    --orchestrator hexagon:defconfig,hexagon:tinyconfig \
    --cell-jobs hexagon:defconfig=24 --cell-jobs hexagon:tinyconfig=9 \
    > dispat.hexagon.yaml

# m68k_nommu, reference 128 s. Five equal configurations: four run at once on
# the fast machine, which the calibration shows is fastest when it is
# oversubscribed, and the cheapest one goes to the worker.
python3 dispat/generate.py "${common[@]}" \
    --arches m68k_nommu --jobs 12 --concurrency 4 \
    --orchestrator m68k_nommu:m5272c3_defconfig,m68k_nommu:m5307c3_defconfig \
    --orchestrator m68k_nommu:m5249evb_defconfig,m68k_nommu:m5407c3_defconfig \
    --cell-jobs m68k_nommu:m5272c3_defconfig=8,m68k_nommu:m5307c3_defconfig=8 \
    --cell-jobs m68k_nommu:m5249evb_defconfig=8,m68k_nommu:m5407c3_defconfig=8 \
    > dispat.m68k_nommu.yaml

git add -A
git commit -q -m 'chore: place the round-2 cells the calibration justified' \
    -m 'One package per configuration, the heavy ones on the machine that starts
the release and the rest on the worker, with the make jobs the measured
script bodies asked for.'
grep -c '^  build-' dispat.hexagon.yaml dispat.m68k_nommu.yaml
