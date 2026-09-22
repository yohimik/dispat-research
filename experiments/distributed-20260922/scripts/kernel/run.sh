#!/bin/bash
# Drive the kernel parity runs on the nodes terraform/kernel created: prepare
# the image-only farm harness and the mailbox on the orchestrator, start the
# worker, run the paired groups (and the solo node when present), collect
# every log and result, and judge each run with the fork's own oracle.
#
#   scripts/kernel/run.sh            # after `terraform apply` in terraform/kernel
#
# Environment: TF_DIR (default terraform/kernel), RUNS_DIR (default
# runs/kernel-<utc>), TRIALS (default 2), SOLO_TRIALS (default 1), FORK_COMMIT.
# The run needs: terraform, jq, ssh, scp, rsync, python3, git.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
kit=$(cd "${here}/../.." && pwd)
tf=${TF_DIR:-${kit}/terraform/kernel}
runs=${RUNS_DIR:-${kit}/runs/kernel-$(date -u +%Y%m%dT%H%M%SZ)}
fork=${FORK:-https://github.com/yohimik/linux-build-test.git}
fork_commit=${FORK_COMMIT:-c699bf3da78c6cf95ec347e24c996076d8895258}
trials=${TRIALS:-2}
solo_trials=${SOLO_TRIALS:-1}
groups=${GROUPS_UNDER_TEST:-"hexagon m68k_nommu"}
kernel_ref=${KERNEL_REF:-v7.3-rc4}

nodes=$(terraform -chdir="${tf}" output -json nodes)
user=$(terraform -chdir="${tf}" output -raw node_user)
key=${tf}/.secrets/operator
mailbox_key=${tf}/.secrets/mailbox_key
secret_file=${tf}/.secrets/execution_secret
orch_ext=$(jq -r .orchestrator.external_ip <<<"${nodes}")
orch_int=$(jq -r .orchestrator.internal_ip <<<"${nodes}")
worker_ext=$(jq -r .worker.external_ip <<<"${nodes}")
solo_ext=$(jq -r '.solo.external_ip // empty' <<<"${nodes}")
mailbox_url="ssh://${user}@${orch_int}/home/${user}/mailbox.git"
mkdir -p "${runs}"
echo "run directory ${runs}"
terraform -chdir="${tf}" output -json > "${runs}/terraform-outputs.json"

ssh_opts=(-i "${key}" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 -o ServerAliveInterval=30)
remote() { # remote <host> <<'SCRIPT'
    ssh "${ssh_opts[@]}" "${user}@$1" bash -s
}
put() { scp -q "${ssh_opts[@]}" "$2" "${user}@$1:$3"; }
fetch() { rsync -a -e "ssh ${ssh_opts[*]}" "${user}@$1:$2" "$3"; }

wait_ready() {
    echo "waiting for $1 to finish its startup script"
    until ssh "${ssh_opts[@]}" "${user}@$1" test -e /var/lib/dispat-node-ready 2>/dev/null; do sleep 15; done
    echo "$1 ready"
}
wait_ready "${orch_ext}"
wait_ready "${worker_ext}"
[ -n "${solo_ext}" ] && wait_ready "${solo_ext}"

for host in "${orch_ext}" "${worker_ext}" ${solo_ext}; do
    put "${host}" "${secret_file}" "~/.execution_secret"
    remote "${host}" <<'SCRIPT'
set -eu
chmod 0600 ~/.execution_secret
SCRIPT
done

# --- the orchestrator: the farm harness, its repository and the mailbox --------
put "${orch_ext}" "${here}/prepare-farm.sh" "~/prepare-farm.sh"
remote "${orch_ext}" <<SCRIPT
set -eu
FORK='${fork}' FORK_COMMIT='${fork_commit}' KERNEL_REF='${kernel_ref}' \
  MAILBOX="/home/${user}/mailbox.git" bash ~/prepare-farm.sh
SCRIPT

# --- the worker: its node file, the mailbox key, the worker process -----------
put "${worker_ext}" "${mailbox_key}" "~/.ssh/mailbox_key"
remote "${worker_ext}" <<SCRIPT
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
    "name": "w1",
    "endpoint": "${mailbox_url}",
    "secretEnv": "DISPAT_EXECUTION_SECRET",
    "concurrency": 1
  },
  "logFormat": "json"
}
EOC
export DISPAT_EXECUTION_SECRET=\$(cat ~/.execution_secret)
export DISPAT_FARM_SOURCE_POOL=/srv/farm/src DISPAT_FARM_RESULTS=/srv/farm/results
docker rm -f dispat-worker >/dev/null 2>&1 || true
NODE_RUN_ARGS='-d --name dispat-worker' node-run \
  dispat worker --root ~/node --state-dir ~/state --idle-timeout 0 --log-level debug
echo "worker started"
SCRIPT

# --- the paired runs ----------------------------------------------------------
run_group() { # run_group <host> <config> <name>
    remote "$1" <<SCRIPT
set -eu
cd ~/farm
mkdir -p ~/round
# The trials of one topology start from no release tags, so every trial plans
# the same cells (dispat/gce/reset-release-tags.sh of the fork).
tags=\$(git tag -l | grep -E '^(kernel|build-)' || true)
[ -n "\${tags}" ] && git tag -d \${tags} > /dev/null
rm -rf /srv/farm/results && mkdir -p /srv/farm/results
export DISPAT_EXECUTION_SECRET=\$(cat ~/.execution_secret)
export DISPAT_FARM_SOURCE_POOL=/srv/farm/src DISPAT_FARM_RESULTS=/srv/farm/results
set +e
node-run /usr/bin/time -o ~/round/$3.time -f 'elapsed=%e user=%U system=%S maxrss=%MkB' \
  dispat release --config $2 --log-format json --log-level debug > ~/round/$3.release.log 2>&1
status=\$?
set -e
echo \${status} > ~/round/$3.status
grep -oE 'elapsed=[0-9.]+' ~/round/$3.time | cut -d= -f2 > ~/round/$3.elapsed
mv /srv/farm/results ~/round/$3.results
echo "$3: status \${status}, elapsed \$(cat ~/round/$3.elapsed) s"
SCRIPT
}
collect_worker_results() { # collect_worker_results <name>
    remote "${worker_ext}" <<SCRIPT
set -eu
mkdir -p ~/round
if [ -d /srv/farm/results ]; then mv /srv/farm/results ~/round/$1.results; else mkdir -p ~/round/$1.results; fi
mkdir -p /srv/farm/results
SCRIPT
}

for group in ${groups}; do
    for t in $(seq 1 "${trials}"); do
        name="${group}-t${t}"
        run_group "${orch_ext}" "dispat.${group}.yaml" "${name}"
        collect_worker_results "${name}"
    done
done

if [ -n "${solo_ext}" ]; then
    put "${solo_ext}" "${here}/prepare-farm.sh" "~/prepare-farm.sh"
    remote "${solo_ext}" <<SCRIPT
set -eu
FORK='${fork}' FORK_COMMIT='${fork_commit}' KERNEL_REF='${kernel_ref}' \
  MAILBOX="/home/${user}/mailbox.git" bash ~/prepare-farm.sh
SCRIPT
    for group in ${groups}; do
        for t in $(seq 1 "${solo_trials}"); do
            run_group "${solo_ext}" "dispat.${group}.solo.yaml" "${group}-solo${t}"
        done
    done
fi

# --- evidence -----------------------------------------------------------------
remote "${worker_ext}" <<'SCRIPT'
docker logs dispat-worker > ~/round/worker.log 2>&1 || true
SCRIPT
for pair in "orchestrator:${orch_ext}" "worker:${worker_ext}" ${solo_ext:+"solo:${solo_ext}"}; do
    role=${pair%%:*}; host=${pair#*:}
    mkdir -p "${runs}/${role}"
    fetch "${host}" "~/round/" "${runs}/${role}/round/"
    fetch "${host}" "/srv/dispat/identity.txt" "${runs}/${role}/"
    fetch "${host}" "/srv/dispat/node-image-id" "${runs}/${role}/"
    fetch "${host}" "/var/log/dispat-node-startup.log" "${runs}/${role}/" || true
    fetch "${host}" "~/farm/dispat.*.yaml" "${runs}/${role}/" || true
    fetch "${host}" "~/farm/source-manifest.json" "${runs}/${role}/" || true
done
gzip -9 "${runs}"/*/round/*.release.log "${runs}"/worker/round/worker.log 2>/dev/null || true

# --- the verdicts, by the fork's own oracle -----------------------------------
git clone -q "${fork}" "${runs}/fork" && git -C "${runs}/fork" checkout -q --detach "${fork_commit}"
: > "${runs}/verdicts.txt"
for group in ${groups}; do
    for name in $(cd "${runs}/orchestrator/round" && ls -d "${group}"-*.results | sed 's/\.results$//'); do
        elapsed=$(cat "${runs}/orchestrator/round/${name}.elapsed")
        reports=$(ls "${runs}"/*/round/"${name}".results/*/result.json 2>/dev/null || true)
        {
            echo "## ${name} (${group}, elapsed ${elapsed} s)"
            # shellcheck disable=SC2086
            python3 "${runs}/fork/dispat/compare.py" \
                --baseline "${runs}/fork/dispat/gce/parity-20260922-reference.json" \
                --arch "${group}" --elapsed "${elapsed}" ${reports} || true
            echo
        } >> "${runs}/verdicts.txt"
    done
done
cat "${runs}/verdicts.txt"
echo "evidence in ${runs}; destroy the nodes with: terraform -chdir=${tf} destroy"
