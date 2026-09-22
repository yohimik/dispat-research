#!/bin/bash
# Runs on the orchestrator (and on the solo node): the image-only export of the
# farm harness as its own repository, the mailbox, and the four round-2
# configurations regenerated with the exact flags that reproduce the retained
# files dispat/gce/round2/{par-c3,solo-c3}/*.yaml of the fork byte for byte
# (only the mailbox path differs). Compare dispat/gce/orchestrator-round2.sh.
set -eu
: "${FORK:?}" "${FORK_COMMIT:?}" "${KERNEL_REF:?}" "${MAILBOX:?}"
rm -rf ~/fork ~/farm ~/mailbox.git
git clone -q "${FORK}" ~/fork
git -C ~/fork checkout -q --detach "${FORK_COMMIT}"
node-run python3 ~/fork/dispat/export-build-harness.py ~/farm
cd ~/farm
common=(--qemu= --split-configs --task-timeout 7200 --workers w1 --mailbox "${MAILBOX}"
        --env FARM_GCC_CURRENT=16.2.0-2.47)
hexagon=(--arches hexagon --orchestrator hexagon:defconfig,hexagon:tinyconfig
         --cell-jobs hexagon:defconfig=24,hexagon:tinyconfig=9,hexagon:allnoconfig=12 --concurrency 2)
m68k=(--arches m68k_nommu
      --orchestrator m68k_nommu:m5272c3_defconfig,m68k_nommu:m5307c3_defconfig,m68k_nommu:m5249evb_defconfig,m68k_nommu:m5407c3_defconfig
      --jobs 8 --cell-jobs m68k_nommu:m5475evb_defconfig=12 --concurrency 4)
python3 dispat/generate.py "${common[@]}" "${hexagon[@]}" --publish-on-orchestrator > dispat.hexagon.yaml
python3 dispat/generate.py "${common[@]}" "${m68k[@]}" --publish-on-orchestrator > dispat.m68k_nommu.yaml
python3 dispat/generate.py "${common[@]}" "${hexagon[@]}" --no-workers > dispat.hexagon.solo.yaml
python3 dispat/generate.py "${common[@]}" "${m68k[@]}" --no-workers > dispat.m68k_nommu.solo.yaml
git init -q -b dispat-prototype
git add -A
git commit -q -m "feat(kernel)^^: test ${KERNEL_REF}" \
    -m 'Image-only export of the farm harness: the QEMU and rootfs assets no
cell of this run reads are left out, so the source snapshot the release
transports is kilobytes rather than gigabytes.'
git init -q --bare "${MAILBOX}"
git remote add origin "${MAILBOX}"
git push -q --set-upstream origin dispat-prototype
echo "farm repository at ~/farm, commit $(git rev-parse --short HEAD); mailbox at ${MAILBOX}"
