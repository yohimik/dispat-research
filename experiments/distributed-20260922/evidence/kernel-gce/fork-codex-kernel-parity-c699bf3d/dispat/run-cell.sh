#!/bin/bash
# One cell of the matrix, run as the build stage of a dispat package.
#
# The package name says what to run: build-<arch> runs the image builds
# buildbot's "<proj>-<arch>-<branch>" builder runs, qemu-<target> the boot
# tests of "qemu-<target>-<branch>". The farm's own scripts are called
# unchanged, from inside a checkout of the kernel revision ref.env names, and
# their pass/fail lines are counted the way master/shellcommands.py counts
# them, so a cell reports the numbers the buildbot pages show.
set -u

farm=$(cd "$(dirname "$0")/.." && pwd)
. "${farm}/dispat/kernel/ref.env"
# Dry runs only: another place to fetch the same ref from. On a real farm it
# stays unset, so the revision under test comes from the file the run signed.
KERNEL_REPO=${DISPAT_FARM_KERNEL_REPO:-${KERNEL_REPO}}

cell=${DISPAT_PACKAGE:?run-cell.sh is a dispat build stage}
kind=${cell%%-*}
target=${FARM_ARCH:-${cell#*-}}

# One bare clone per machine, shared by every cell and every run. A cell works
# in a kernel tree of its own, so two cells never share one, which is what
# buildbot's one-directory-per-builder rule was protecting.
#
# A machine prepared by dispat/gce/node-startup.sh keeps one pristine tree per
# build slot, checked out once during setup. DISPAT_FARM_SOURCE_POOL names that
# folder; a cell leases a tree from it under a lock instead of creating a
# worktree, which takes the kernel checkout out of the release's measured
# interval. Without the pool a cell creates its own worktree, as before.
cache=${DISPAT_FARM_LINUX:-${HOME}/.cache/dispat-farm/linux.git}
pool=${DISPAT_FARM_SOURCE_POOL:-}
work=$(mktemp -d "${TMPDIR:-/tmp}/dispat-farm.XXXXXX")
log="${work}/cell.log"
started=${SECONDS}
leased=""

cleanup() {
    if [ -z "${leased}" ]; then
        git -C "${cache}" worktree remove --force "${work}/linux" >/dev/null 2>&1
    fi
    rm -rf "${work}"
}
trap cleanup EXIT

if [ -n "${pool}" ]; then
    # Hold the lock on an open descriptor: the lease lasts as long as this
    # cell, and the kernel releases it even if the cell is killed.
    lease_started=${SECONDS}
    for candidate in "${pool}"/slot*; do
        [ -d "${candidate}" ] || continue
        exec {lock}>"${candidate}.lock" || exit 1
        if flock -n "${lock}"; then
            leased="${candidate}"
            break
        fi
        exec {lock}>&-
    done
    if [ -z "${leased}" ]; then
        echo "run-cell.sh: no free source tree in ${pool}" >&2
        exit 1
    fi
    # The farm script cleans the tree itself, at its start and at its end. Only
    # refuse a tree that is not the revision under test or has modified tracked
    # files, the state a fresh worktree would have been in.
    tag=$(git -C "${leased}" describe --exact-match --match 'v*' HEAD 2>/dev/null || true)
    if [ "${tag}" != "${KERNEL_REF}" ]; then
        echo "run-cell.sh: ${leased} is at '${tag}', not ${KERNEL_REF}" >&2
        exit 1
    fi
    if ! git -C "${leased}" diff --quiet HEAD; then
        echo "run-cell.sh: ${leased} has modified tracked files" >&2
        exit 1
    fi
    rev=$(git -C "${leased}" rev-parse HEAD) || exit 1
    printf '{"source_lease_seconds": %d, "source": "%s"}\n' \
        "$((SECONDS - lease_started))" "${leased}" > "${work}/checkout.json"
    cd "${leased}" || exit 1
else
    # Tags travel too: the farm's scripts name the build with `git describe`.
    # One commit deep: the scripts name the build with `git describe`, which
    # answers the tag itself when the tag is the checkout, and nothing here reads
    # history. A full kernel history is gigabytes nobody needs for a build.
    # Split cells can start simultaneously on one node. Protect the bare repository's
    # initialization, shallow file, refs and worktree registration from concurrent Git.
    rev=$(python3 "${farm}/dispat/checkout.py" "${cache}" "${KERNEL_REPO}" \
        "${KERNEL_REF}" "${work}/linux" "${work}/checkout.json") || exit 1
    cd "${work}/linux" || exit 1
fi

export PATH="${farm}/bin:${PATH}"
# Dry runs only: a folder of stand-in scripts searched before the farm's own,
# so the wiring can be exercised on a machine with no cross toolchains.
scripts=${DISPAT_FARM_SCRIPTS:-}
# stable-build-arch.sh builds into one fixed folder, which is why buildbot
# gives an image build a machine to itself. With a folder per cell two image
# builds can share a machine when its owner allows two slots.
export BUILDDIR="${work}/build"
export LOG="${work}/buildlog"

script_started=${SECONDS}
case "${kind}" in
build)
    PATH="${scripts:+${scripts}:}${PATH}" stable-build-arch.sh "${target}" "${KERNEL_BRANCH}" "${FARM_CONFIG:-}" 2>&1 | tee "${log}"
    status=${PIPESTATUS[0]}
    ;;
qemu)
    PATH="${scripts:+${scripts}:}${farm}/rootfs/${target}:${PATH}" "run-qemu-${target}.sh" 2>&1 | tee "${log}"
    status=${PIPESTATUS[0]}
    ;;
*)
    echo "run-cell.sh: ${cell} is neither build-<arch> nor qemu-<target>" >&2
    exit 2
    ;;
esac
script_seconds=$((SECONDS - script_started))

# Image-build scripts communicate failures in their log, not their exit code.
# Keep the evidence outside the disposable worktree before judging the cell.
results=${DISPAT_FARM_RESULTS:-${HOME}/.local/state/dispat-farm/results}
mkdir -p "${results}" || exit 1
result=$(mktemp -d "${results}/${cell}.XXXXXX") || exit 1
cp "${log}" "${result}/cell.log" || exit 1
reference=$(git describe --match 'v*' 2>/dev/null || echo "${rev}")
output_args=()
if [ -n "${DISPAT_OUTPUT:-}" ]; then
    output_args=(--output "${DISPAT_OUTPUT}")
fi
echo "Cell evidence: ${result}"
python3 "${farm}/dispat/results.py" "${kind}" "${result}/cell.log" \
    --command-status "${status}" --ref "${reference}" --cell "${cell}" \
    --revision "${rev}" --script-seconds "${script_seconds}" \
    --seconds "$((SECONDS - started))" --json "${result}/result.json" \
    --checkout-timings "${work}/checkout.json" \
    "${output_args[@]}"
exit "$?"
