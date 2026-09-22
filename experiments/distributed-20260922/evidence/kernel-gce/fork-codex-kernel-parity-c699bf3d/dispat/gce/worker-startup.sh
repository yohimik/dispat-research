#!/bin/bash
# Startup script of a worker VM: what a kernel image build needs, the
# kernel.org cross toolchains the farm's scripts expect under /opt/kernel,
# and a marker the operator waits for. The worker process itself is started
# by worker.sh over ssh, so its output can be watched.
#
# The gcc version is the one stable-build-arch.sh selects for v6.12 and later
# (CV14): the crosstool tarball is named after gcc alone, the script's folder
# after gcc and binutils, so the folder is linked under the second name.
set -eu
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y -q build-essential flex bison libssl-dev libelf-dev bc git \
    python3 kmod cpio rsync libncurses-dev dwarves zstd lz4 xz-utils clang lld llvm \
    curl ca-certificates

CV=14.3.0
CVDIR="gcc-${CV}-2.44-nolibc"
BASE="https://mirrors.edge.kernel.org/pub/tools/crosstool/files/bin/x86_64/${CV}"
mkdir -p /opt/kernel
cd /opt/kernel
arches=$(curl -sf -H 'Metadata-Flavor: Google' \
    'http://metadata.google.internal/computeMetadata/v1/instance/attributes/toolchains' || true)
for target in ${arches:-x86_64-linux}; do
    tarball="x86_64-gcc-${CV}-nolibc-${target}.tar.xz"
    curl -sfL -o "/tmp/${tarball}" "${BASE}/${tarball}"
    tar -xJf "/tmp/${tarball}" -C /opt/kernel
    rm -f "/tmp/${tarball}"
done
# The tarballs extract to gcc-<CV>-nolibc/<target>; the scripts look for
# gcc-<CV>-<binutils>-nolibc/<target>.
ln -sfn "/opt/kernel/gcc-${CV}-nolibc" "/opt/kernel/${CVDIR}"
# stable-build-arch.sh names an llvm folder for the clang builds; the distro's
# clang stands in for it.
mkdir -p /opt/kernel/llvm-16.0.6-x86_64
ln -sfn /usr/bin /opt/kernel/llvm-16.0.6-x86_64/bin
touch /var/lib/dispat-worker-ready
