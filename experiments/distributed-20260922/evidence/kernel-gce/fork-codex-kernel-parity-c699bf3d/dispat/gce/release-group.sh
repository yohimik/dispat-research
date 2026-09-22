#!/bin/bash
# One timed candidate: GNU `time` elapsed of one `dispat release` for one
# architecture group, from invocation to exit.
#
#   dispat/gce/release-group.sh <group> <trial> <config file>
#
# Writes ~/round2/<group>-<trial>.{release.log,time,elapsed}. Every cell builds
# in a directory of its own that it creates and removes, so a candidate's
# compiled output is always cold; the kernel source is warm, as it is on the
# reference farm. Expects DISPAT_EXECUTION_SECRET in the environment and the
# farm repository at ~/farm.
set -u
group=$1
trial=$2
config=$3
: "${DISPAT_EXECUTION_SECRET:?the signing secret}"
# A cell reads these from the environment of the process that runs it: dispat
# reserves the DISPAT_ prefix inside a package's own env.
export DISPAT_FARM_SOURCE_POOL=${DISPAT_FARM_SOURCE_POOL:-/srv/farm/src}
export DISPAT_FARM_RESULTS=${DISPAT_FARM_RESULTS:-/srv/farm/results}
out=~/round2
mkdir -p "${out}"
name="${group}-${trial}"

cd ~/farm
/usr/bin/time -o "${out}/${name}.time" -f 'elapsed=%e user=%U system=%S maxrss=%MkB' \
    dispat release --config "${config}" --log-format json --log-level debug \
    > "${out}/${name}.release.log" 2>&1
status=$?
grep -oE 'elapsed=[0-9.]+' "${out}/${name}.time" | cut -d= -f2 > "${out}/${name}.elapsed"
echo "${name}: status ${status}, elapsed $(cat "${out}/${name}.elapsed") s"
exit "${status}"
