#!/bin/bash
# Drive the LLVM parity pair on the nodes terraform/llvm created, as
# .ci/dispat/gce/REPORT.md attempts 8 and 9 ran it: the matrix fixture
# distributed over two workers, then the same recipe on one worker alone, then
# the fork's compare.py over both product sets. Sources are warm on every
# node (the workers' object caches are seeded from the mailbox before the
# timed run), outputs cold on both sides.
#
#   scripts/llvm/run.sh              # after `terraform apply` in terraform/llvm
#
# Environment: TF_DIR, RUNS_DIR, FORK, FORK_COMMIT, BASELINE_COMMIT, PREWARM
# (1: seed the workers' caches from the mailbox, the default; 0: cold).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
kit=$(cd "${here}/../.." && pwd)
tf=${TF_DIR:-${kit}/terraform/llvm}
runs=${RUNS_DIR:-${kit}/runs/llvm-$(date -u +%Y%m%dT%H%M%SZ)}
fork=${FORK:-https://github.com/yohimik/llvm-project.git}
fork_branch=${FORK_BRANCH:-dispat-gce}
fork_commit=${FORK_COMMIT:-952c2de43cd663fa3dbc74130c8bc59925957490}
# The LLVM main commit the baselines dispat/<pkg>/v24.0.0 were tagged at, so
# that every fork commit above it and the trigger commit form the window.
baseline_commit=${BASELINE_COMMIT:-a9f4d3ff18c599d8be5a1f6ef4d8bc2417de8a34}
prewarm=${PREWARM:-1}

nodes=$(terraform -chdir="${tf}" output -json nodes)
user=$(terraform -chdir="${tf}" output -raw node_user)
key=${tf}/.secrets/operator
mailbox_key=${tf}/.secrets/mailbox_key
secret_file=${tf}/.secrets/execution_secret
orch_ext=$(jq -r .orchestrator.external_ip <<<"${nodes}")
orch_int=$(jq -r .orchestrator.internal_ip <<<"${nodes}")
w1_ext=$(jq -r .w1.external_ip <<<"${nodes}")
w2_ext=$(jq -r .w2.external_ip <<<"${nodes}")
mailbox_url="ssh://${user}@${orch_int}/home/${user}/origin.git"
mkdir -p "${runs}"
echo "run directory ${runs}"
terraform -chdir="${tf}" output -json > "${runs}/terraform-outputs.json"

ssh_opts=(-i "${key}" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 -o ServerAliveInterval=30)
remote() { ssh "${ssh_opts[@]}" "${user}@$1" bash -s; }
put() { scp -q "${ssh_opts[@]}" "$2" "${user}@$1:$3"; }
fetch() { rsync -a -e "ssh ${ssh_opts[*]}" "${user}@$1:$2" "$3"; }
wait_ready() {
    echo "waiting for $1 to finish its startup script"
    until ssh "${ssh_opts[@]}" "${user}@$1" test -e /var/lib/dispat-node-ready 2>/dev/null; do sleep 15; done
    echo "$1 ready"
}
for host in "${orch_ext}" "${w1_ext}" "${w2_ext}"; do wait_ready "${host}"; done
for host in "${orch_ext}" "${w1_ext}" "${w2_ext}"; do
    put "${host}" "${secret_file}" "~/.execution_secret"
    remote "${host}" <<'SCRIPT'
chmod 0600 ~/.execution_secret
SCRIPT
done

# --- the orchestrator: the fork, the baselines, the trigger, the mailbox -----
put "${orch_ext}" "${here}/prepare-llvm.sh" "~/prepare-llvm.sh"
remote "${orch_ext}" <<SCRIPT
set -eu
FORK='${fork}' FORK_BRANCH='${fork_branch}' FORK_COMMIT='${fork_commit}' \
  BASELINE_COMMIT='${baseline_commit}' bash ~/prepare-llvm.sh
SCRIPT
source_commit=$(remote "${orch_ext}" <<'SCRIPT'
git -C ~/llvm rev-parse HEAD
SCRIPT
)
echo "source commit ${source_commit}"

# --- the workers: mailbox key, node file, warm object cache, worker process --
start_worker() { # start_worker <host> <name>
    put "$1" "${mailbox_key}" "~/.ssh/mailbox_key"
    remote "$1" <<SCRIPT
set -eu
chmod 0600 ~/.ssh/mailbox_key
ssh-keyscan -H '${orch_int}' >> ~/.ssh/known_hosts 2>/dev/null
cat > ~/.ssh/config <<EOC
Host ${orch_int}
  IdentityFile ~/.ssh/mailbox_key
  IdentitiesOnly yes
EOC
mkdir -p ~/node ~/state
cat > ~/node/dispat.json <<EOC
{
  "execution": {
    "role": "worker",
    "name": "$2",
    "endpoint": "${mailbox_url}",
    "secretEnv": "DISPAT_EXECUTION_SECRET",
    "concurrency": 1,
    "transfer": {"maxFiles": 250000, "maxBytes": 68719476736,
                 "maxManifestBytes": 134217728, "timeout": 3600}
  },
  "logFormat": "json"
}
EOC
if [ '${prewarm}' = 1 ]; then
    # The worker keeps one bare object cache per endpoint at
    # <state>/<name>/cache/<first 16 hex of sha256(endpoint)>.git
    # (services/dispat/internal/execution/state.go). Seeding it with the
    # mailbox's objects is what "sources warm on every node" means: the
    # measured attempts 8 and 9 ran on workers that had fetched the same
    # history in earlier attempts.
    keyhex=\$(printf '%s' '${mailbox_url}' | sha256sum | cut -c1-16)
    cache=~/state/$2/cache/\${keyhex}.git
    if [ ! -d "\${cache}/objects" ]; then
        mkdir -p "\$(dirname "\${cache}")"
        node-run git clone -q --bare '${mailbox_url}' "\${cache}"
        node-run git -C "\${cache}" update-ref -d refs/heads/${fork_branch} || true
    fi
fi
export DISPAT_EXECUTION_SECRET=\$(cat ~/.execution_secret)
docker rm -f dispat-worker >/dev/null 2>&1 || true
NODE_RUN_ARGS='-d --name dispat-worker' node-run \
  dispat worker --root ~/node --state-dir ~/state --idle-timeout 0 --log-level debug
echo "worker $2 started"
SCRIPT
}
start_worker "${w1_ext}" w1
start_worker "${w2_ext}" w2

# --- the distributed run, timed on the orchestrator ---------------------------
remote "${orch_ext}" <<'SCRIPT'
set -eu
cd ~/llvm
mkdir -p ~/round
export DISPAT_EXECUTION_SECRET=$(cat ~/.execution_secret)
node-run dispat status --config dispat.gce.yaml --log-format json > ~/round/status-dist.log 2>&1 || true
date -u +%FT%TZ > ~/round/release-dist.start
set +e
node-run /usr/bin/time -o ~/round/release-dist.time -f 'elapsed=%e user=%U system=%S maxrss=%MkB' \
  dispat release --config dispat.gce.yaml --log-format json --log-level debug > ~/round/release-dist.log 2>&1
echo $? > ~/round/release-dist.status
set -e
echo "distributed: status $(cat ~/round/release-dist.status), $(cat ~/round/release-dist.time)"
SCRIPT

# --- the baseline: the same recipe on w2 alone, from its own clone ------------
remote "${w2_ext}" <<'SCRIPT'
docker rm -f dispat-worker >/dev/null 2>&1 || true
SCRIPT
put "${w2_ext}" "${here}/prepare-llvm-baseline.sh" "~/prepare-llvm-baseline.sh"
remote "${w2_ext}" <<SCRIPT
set -eu
MAILBOX_URL='${mailbox_url}' FORK_BRANCH='${fork_branch}' SOURCE_COMMIT='${source_commit}' bash ~/prepare-llvm-baseline.sh
cd ~/llvm-src
mkdir -p ~/round
node-run dispat status --config dispat.local.yaml --log-format json > ~/round/status-local.log 2>&1 || true
date -u +%FT%TZ > ~/round/release-local.start
set +e
node-run /usr/bin/time -o ~/round/release-local.time -f 'elapsed=%e user=%U system=%S maxrss=%MkB' \
  dispat release --config dispat.local.yaml --log-format json --log-level debug > ~/round/release-local.log 2>&1
echo \$? > ~/round/release-local.status
set -e
echo "baseline: status \$(cat ~/round/release-local.status), \$(cat ~/round/release-local.time)"
SCRIPT

# --- products: the orchestrator's trees beside the baseline's, compared on w2 -
remote "${w2_ext}" <<SCRIPT
set -eu
for folder in llvm lld polly .ci/dispat/llvm-aarch64 .ci/dispat/bundle; do
    mkdir -p ~/llvm-dist/\${folder}
    rsync -a -e 'ssh -i ~/.ssh/mailbox_key' "${user}@${orch_int}:~/llvm/\${folder}/_dispat/" ~/llvm-dist/\${folder}/_dispat/
done
node-run python3 ~/llvm-src/.ci/dispat/gce/compare.py ~/llvm-src ~/llvm-dist > ~/round/compare.txt 2>&1 || true
tail -n 1 ~/round/compare.txt
SCRIPT

# --- evidence -----------------------------------------------------------------
for pair in "w1:${w1_ext}" "w2:${w2_ext}"; do
    remote "${pair#*:}" <<'SCRIPT'
mkdir -p ~/round; docker logs dispat-worker > ~/round/worker.log 2>&1 || true
SCRIPT
done
for pair in "orchestrator:${orch_ext}" "w1:${w1_ext}" "w2:${w2_ext}"; do
    role=${pair%%:*}; host=${pair#*:}
    mkdir -p "${runs}/${role}"
    fetch "${host}" "~/round/" "${runs}/${role}/round/" || true
    fetch "${host}" "/srv/dispat/identity.txt" "${runs}/${role}/" || true
    fetch "${host}" "/srv/dispat/node-image-id" "${runs}/${role}/" || true
    fetch "${host}" "/var/log/dispat-node-startup.log" "${runs}/${role}/" || true
done
fetch "${orch_ext}" "~/llvm/dispat.gce.yaml" "${runs}/orchestrator/" || true
fetch "${w2_ext}" "~/llvm-src/dispat.local.yaml" "${runs}/w2/" || true
for pkg in llvm lld polly .ci/dispat/llvm-aarch64 .ci/dispat/bundle; do
    fetch "${orch_ext}" "~/llvm/${pkg}/_dispat/build-info.json" "${runs}/orchestrator/receipts/${pkg//\//_}.json" || true
    fetch "${w2_ext}" "~/llvm-src/${pkg}/_dispat/build-info.json" "${runs}/w2/receipts/${pkg//\//_}.json" || true
done
gzip -9 "${runs}"/*/round/*.log 2>/dev/null || true
echo "distributed: $(cat "${runs}/orchestrator/round/release-dist.time")"
echo "baseline:    $(cat "${runs}/w2/round/release-local.time")"
echo "products:    $(tail -n 1 "${runs}/w2/round/compare.txt")"
echo "evidence in ${runs}; destroy the nodes with: terraform -chdir=${tf} destroy"
