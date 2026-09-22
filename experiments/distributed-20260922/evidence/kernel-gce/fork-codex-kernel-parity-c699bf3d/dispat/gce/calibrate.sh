#!/bin/bash
# Time farm build-script bodies on this machine, outside dispat, so a topology
# is chosen from measurements rather than from guesses about per-core speed.
#
#   dispat/gce/calibrate.sh <farm folder> <plan file> <results file>
#
# The plan is a sequence of groups separated by blank lines. Every line of a
# group starts at the same moment, which is how a machine that runs several
# cells at once is measured:
#
#   <label> <arch> <comma-separated configs|-> <make jobs> <source slot>
#
# Lines starting with # are comments. The measured interval is exactly the
# interval run-cell.sh measures as the script body: one invocation of
# bin/stable-build-arch.sh in a pristine source tree with its own build folder.
set -u
farm=$1
plan=$2
out=$3
src_root=${FARM_SRC_ROOT:-/srv/farm/src}
build_root=${FARM_BUILD_ROOT:-/srv/farm/build}
log_root=${FARM_LOG_ROOT:-/srv/farm/results}
export PATH="${farm}/bin:${PATH}"
export FARM_GCC_CURRENT="${FARM_GCC_CURRENT:-16.2.0-2.47}"
mkdir -p "${build_root}" "${log_root}"
: > "${out}"

run_one() {
    local label=$1 arch=$2 configs=$3 jobs=$4 slot=$5
    local tree="${src_root}/slot${slot}"
    local build="${build_root}/${label}"
    local log="${log_root}/${label}.log"
    local started ended status
    rm -rf "${build}"
    started=$(date +%s.%N)
    (
        cd "${tree}" &&
        BUILDDIR="${build}" LOG="${log_root}/${label}.buildlog" \
        FARM_BUILD_JOBS="${jobs}" \
        stable-build-arch.sh "${arch}" master "${configs}"
    ) > "${log}" 2>&1
    status=$?
    ended=$(date +%s.%N)
    rm -rf "${build}"
    printf '%s arch=%s configs=%s jobs=%s slot=%s status=%s seconds=%.2f cases=%s\n' \
        "${label}" "${arch}" "${configs}" "${jobs}" "${slot}" "${status}" \
        "$(echo "${ended} ${started}" | awk '{printf "%.2f", $1 - $2}')" \
        "$(grep -c '^Building .* \.\.\. passed$' "${log}")" >> "${out}"
}

group=0
group_started=""
members=0
flush() {
    [ "${members}" -eq 0 ] && return 0
    wait
    printf '# group %d finished after %s s\n' "${group}" \
        "$(echo "$(date +%s.%N) ${group_started}" | awk '{printf "%.2f", $1 - $2}')" >> "${out}"
    group=$((group + 1))
    members=0
}

while IFS= read -r line || [ -n "${line}" ]; do
    case "${line}" in
    '#'*) continue ;;
    '')   flush; continue ;;
    esac
    if [ "${members}" -eq 0 ]; then
        group_started=$(date +%s.%N)
    fi
    members=$((members + 1))
    # shellcheck disable=SC2086
    run_one ${line} &
done < "${plan}"
flush
echo "calibration complete" >> "${out}"
