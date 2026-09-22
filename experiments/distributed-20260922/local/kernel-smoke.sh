#!/bin/bash
# End-to-end smoke of the kernel kit on this machine (see kernel-compose.yaml):
# prepares one source tree per node, the harness and the mailbox, starts the
# worker, runs the hexagon group once through the pipeline and judges it with
# the fork's oracle. Expect "elapsed time exceeds reference" on a laptop; every
# other check (cases, revision, toolchain identities) must pass.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
compose=(docker compose -f "${here}/kernel-compose.yaml")
fork=${FORK:-https://github.com/yohimik/linux-build-test.git}
fork_commit=${FORK_COMMIT:-c699bf3da78c6cf95ec347e24c996076d8895258}
group=${GROUP:-hexagon}
slots=${SLOTS:-3}
secret=$(openssl rand -hex 32)
out=${OUT:-${here}/../runs/local-kernel-$(date -u +%Y%m%dT%H%M%SZ)}
mkdir -p "${out}"

exec_in() { "${compose[@]}" exec -T -e "DISPAT_EXECUTION_SECRET=${secret}" "$@"; }

for node in orchestrator worker; do
    exec_in "${node}" node-prepare v7.3-rc4 https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git "${slots}"
    exec_in "${node}" node-identity > "${out}/${node}-identity.txt"
done

# The orchestrator: the harness, its repository, the mailbox on the shared volume.
exec_in orchestrator bash -s <<SCRIPT
set -eu
cd /root
rm -rf fork farm /mailbox/mailbox.git
git clone -q '${fork}' fork && git -C fork checkout -q --detach '${fork_commit}'
python3 fork/dispat/export-build-harness.py farm
cd farm
common=(--qemu= --split-configs --task-timeout 7200 --workers w1 --mailbox /mailbox/mailbox.git --env FARM_GCC_CURRENT=16.2.0-2.47)
hexagon=(--arches hexagon --orchestrator hexagon:defconfig,hexagon:tinyconfig --cell-jobs hexagon:defconfig=24,hexagon:tinyconfig=9,hexagon:allnoconfig=12 --concurrency 2)
m68k=(--arches m68k_nommu --orchestrator m68k_nommu:m5272c3_defconfig,m68k_nommu:m5307c3_defconfig,m68k_nommu:m5249evb_defconfig,m68k_nommu:m5407c3_defconfig --jobs 8 --cell-jobs m68k_nommu:m5475evb_defconfig=12 --concurrency 4)
python3 dispat/generate.py "\${common[@]}" "\${hexagon[@]}" --publish-on-orchestrator > dispat.hexagon.yaml
python3 dispat/generate.py "\${common[@]}" "\${m68k[@]}" --publish-on-orchestrator > dispat.m68k_nommu.yaml
git init -q -b dispat-prototype && git add -A && git commit -q -m 'feat(kernel)^^: test v7.3-rc4'
git init -q --bare /mailbox/mailbox.git
git remote add origin /mailbox/mailbox.git && git push -q --set-upstream origin dispat-prototype
echo "farm at /root/farm, commit \$(git rev-parse --short HEAD)"
SCRIPT

# The worker: its node file and the worker process, polling the shared mailbox.
exec_in worker bash -s <<'SCRIPT'
set -eu
mkdir -p /root/node /root/state
cat > /root/node/dispat.json <<EOC
{"execution": {"role": "worker", "name": "w1", "endpoint": "/mailbox/mailbox.git",
  "secretEnv": "DISPAT_EXECUTION_SECRET", "concurrency": 1}, "logFormat": "json"}
EOC
nohup dispat worker --root /root/node --state-dir /root/state --idle-timeout 0 --log-level debug > /root/worker.log 2>&1 < /dev/null &
echo "worker pid $!"
SCRIPT

exec_in orchestrator bash -s <<SCRIPT
set -eu
cd /root/farm
rm -rf /srv/farm/results && mkdir -p /srv/farm/results
/usr/bin/time -o /root/${group}.time -f 'elapsed=%e user=%U system=%S maxrss=%MkB' \
  dispat release --config dispat.${group}.yaml --log-format json --log-level debug > /root/${group}.release.log 2>&1 || echo "release exited \$?"
cat /root/${group}.time
SCRIPT

"${compose[@]}" cp orchestrator:/root/${group}.release.log "${out}/${group}.release.log"
"${compose[@]}" cp orchestrator:/root/${group}.time "${out}/${group}.time"
"${compose[@]}" cp orchestrator:/srv/farm/results "${out}/orchestrator-results"
"${compose[@]}" cp worker:/srv/farm/results "${out}/worker-results"
"${compose[@]}" cp worker:/root/worker.log "${out}/worker.log"
git clone -q "${fork}" "${out}/fork" && git -C "${out}/fork" checkout -q --detach "${fork_commit}"
elapsed=$(grep -oE 'elapsed=[0-9.]+' "${out}/${group}.time" | cut -d= -f2)
python3 "${out}/fork/dispat/compare.py" --baseline "${out}/fork/dispat/gce/parity-20260922-reference.json" \
    --arch "${group}" --elapsed "${elapsed}" "${out}"/*-results/*/result.json | tee "${out}/verdict.json" || true
echo "evidence in ${out}"
