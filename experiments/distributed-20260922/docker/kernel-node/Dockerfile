# syntax=docker/dockerfile:1.7
# A kernel farm node, as dispat/gce/node-startup.sh of yohimik/linux-build-test
# (branch codex/kernel-parity, c699bf3d) provisioned it on 2026-09-22, made
# reproducible: the Ubuntu 24.04 base image is pinned by digest, the apt
# packages come from the Ubuntu archive snapshot of the day the parity runs
# were measured, the kernel.org cross toolchains are pinned by version and
# checksum, and the dispat binary is the one docker/dispat/Dockerfile rebuilds.
#
# The reference farm (kerneltests.org) builds hexagon with Ubuntu's clang and
# alpha/m68k with the kernel.org crosstool gcc; both identities are checked by
# the fork's dispat/compare.py against the reference JSON, so the versions
# here are not free to change.
#
# Self-contained: no build context is needed (docker build -f - / from stdin
# works), which is how a VM builds it from instance metadata.
#
#   docker buildx build --platform linux/amd64 \
#     --build-arg DISPAT_IMAGE=dispat-experiment:272772cb \
#     -t dispat-kernel-node:272772cb -f docker/kernel-node/Dockerfile .
ARG UBUNTU_IMAGE=ubuntu:24.04@sha256:008173c23f95b170204355c12626cb5a965d779a7e1283b09e9cffbb1bf33ca3
ARG DISPAT_IMAGE=dispat-experiment:pinned
FROM ${DISPAT_IMAGE} AS dispat

FROM ${UBUNTU_IMAGE}
# The Ubuntu archive snapshot every package is taken from (snapshot.ubuntu.com,
# apt 2.8 `--snapshot`). The original VMs installed from the live archive on
# 2026-09-22; this is the archive as it stood at the start of that day.
ARG APT_SNAPSHOT=20260922T000000Z
# The crosstool release the reference farm used (FARM_GCC_CURRENT=16.2.0-2.47).
ARG CROSSTOOL_VERSION=16.2.0
ARG BINUTILS_VERSION=2.47
# Space separated crosstool targets; hexagon needs none (clang).
ARG CROSSTOOL_TARGETS="alpha-linux m68k-linux"
ARG TARGETARCH
ENV DEBIAN_FRONTEND=noninteractive
# The package list of node-startup.sh, plus what a node needs once its worker
# runs inside a container: an ssh client for the mailbox, flock (util-linux),
# GNU time for the measurement, gzip for the evidence.
RUN set -eux; \
    apt-get update --snapshot "${APT_SNAPSHOT}"; \
    apt-get install -o "Acquire::Snapshot=${APT_SNAPSHOT}" -y -q \
      build-essential flex bison libssl-dev libelf-dev bc git \
      python3 kmod cpio rsync libncurses-dev dwarves zstd lz4 xz-utils clang lld llvm \
      curl ca-certificates time openssh-client util-linux gzip; \
    dpkg-query -W -f='${Package}=${Version}\n' > /etc/apt-packages.lock; \
    rm -rf /var/lib/apt/lists/*
# kernel.org publishes the crosstool for x86_64 and arm64 hosts; the parity
# runs are x86_64, the arm64 half exists so the kit can be smoke tested on an
# Apple silicon laptop. Checksums are those of
# https://mirrors.edge.kernel.org/pub/tools/crosstool/files/bin/<host>/16.2.0/sha256sums.asc
RUN set -eux; \
    case "${TARGETARCH}" in \
      amd64) host=x86_64; \
             sum_alpha=0031e472c330e657925912958bc9d9f5f2879a45ecbaab9c34bc59e51aad69ca; \
             sum_m68k=7b00cafd56e3699055ca5df5c260be558332502a918df62cbe272ba3902e5b33 ;; \
      arm64) host=arm64; \
             sum_alpha=56b2c1a569d3fafac4d21d2effc85ebe07cf45e24160d74e3c98b198a92a6ea0; \
             sum_m68k=f58fc7fc39e0bc2ff830d2d1c94c603a8384833d1874591483cd23543d4deca8 ;; \
      *) echo "no crosstool for ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    base="https://mirrors.edge.kernel.org/pub/tools/crosstool/files/bin/${host}/${CROSSTOOL_VERSION}"; \
    mkdir -p /opt/kernel; \
    for target in ${CROSSTOOL_TARGETS}; do \
      case "${target}" in alpha-linux) sum=${sum_alpha};; m68k-linux) sum=${sum_m68k};; *) echo "no checksum for ${target}" >&2; exit 1;; esac; \
      tarball="${host}-gcc-${CROSSTOOL_VERSION}-nolibc-${target}.tar.xz"; \
      curl -sfL -o "/tmp/${tarball}" "${base}/${tarball}"; \
      echo "${sum}  /tmp/${tarball}" | sha256sum -c -; \
      tar -xJf "/tmp/${tarball}" -C /opt/kernel; \
      rm -f "/tmp/${tarball}"; \
    done; \
    ln -sfn "/opt/kernel/gcc-${CROSSTOOL_VERSION}-nolibc" "/opt/kernel/gcc-${CROSSTOOL_VERSION}-${BINUTILS_VERSION}-nolibc"; \
    mkdir -p /opt/kernel/llvm-16.0.6-x86_64; \
    ln -sfn /usr/bin /opt/kernel/llvm-16.0.6-x86_64/bin
COPY --from=dispat /dispat /usr/local/bin/dispat
COPY --from=dispat /dispat.sha256 /dispat.buildinfo /dispat.commit /etc/dispat/
# Any uid may run in this image (the VM maps the container to its login user).
RUN set -eux; \
    git config --system user.email node@dispat.invalid; \
    git config --system user.name "dispat node"; \
    git config --system --add safe.directory '*'; \
    install -d -m 0777 /srv/farm
# node-identity: the identities compare.py rejects a run for, and the binary.
# node-prepare: one bare kernel cache and a pool of pristine source trees, as
# node-startup.sh prepared them (the checkout leaves the measured interval).
RUN cat > /usr/local/bin/node-identity <<'SH'
#!/bin/bash
set -eu
CV=${CROSSTOOL_VERSION:-16.2.0}
dispat --version 2>/dev/null | tail -n 1
cat /etc/dispat/dispat.sha256
clang --version | head -n 1
for target in ${CROSSTOOL_TARGETS:-alpha-linux m68k-linux}; do
    prefix="${target%-linux}-linux-"
    gcc_bin="/opt/kernel/gcc-${CV}-nolibc/${target}/bin/${prefix}gcc"
    "${gcc_bin}" --version | head -n 1
    "${gcc_bin}" -Wa,--version -c -x assembler /dev/null -o /dev/null 2>/dev/null | head -n 1
done
SH
RUN cat > /usr/local/bin/node-prepare <<'SH'
#!/bin/bash
# node-prepare [ref] [repo] [slots]: the kernel cache and source pool under
# /srv/farm, exactly as dispat/gce/node-startup.sh prepared them.
set -eux
ref=${1:-${KERNEL_REF:-v7.3-rc4}}
repo=${2:-${KERNEL_REPO:-https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git}}
slots=${3:-${SOURCE_SLOTS:-4}}
install -d -m 0777 /srv/farm /srv/farm/src /srv/farm/build /srv/farm/results
cache=/srv/farm/linux.git
if [ ! -d "${cache}" ]; then
    git init -q --bare "${cache}"
    git -C "${cache}" fetch -q --depth 1 "${repo}" "refs/tags/${ref}:refs/tags/${ref}"
fi
rev=$(git -C "${cache}" rev-parse "refs/tags/${ref}^{commit}")
for i in $(seq 0 $((slots - 1))); do
    [ -d "/srv/farm/src/slot${i}" ] && continue
    git -C "${cache}" worktree add -q --detach "/srv/farm/src/slot${i}" "${rev}"
    # The freshness check a cell performs reads every tracked file's metadata,
    # which costs seconds on a tree nobody has touched; pay it here.
    git -C "/srv/farm/src/slot${i}" diff --quiet HEAD
done
printf '%s\n' "${rev}" > /srv/farm/revision
chmod -R a+rwX /srv/farm
echo "prepared ${slots} trees of ${ref} (${rev}) under /srv/farm"
SH
RUN chmod 0755 /usr/local/bin/node-identity /usr/local/bin/node-prepare
ENV CROSSTOOL_VERSION=${CROSSTOOL_VERSION} CROSSTOOL_TARGETS="${CROSSTOOL_TARGETS}"
WORKDIR /srv/farm
