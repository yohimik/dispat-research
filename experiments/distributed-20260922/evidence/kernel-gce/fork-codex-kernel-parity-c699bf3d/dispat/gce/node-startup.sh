#!/bin/bash
# Startup script of a round-2 node: what a kernel image build needs, the
# kernel.org cross toolchains the reference farm used, one bare kernel cache
# and a pool of pristine source trees. A cell leases a tree from that pool
# instead of creating a worktree of its own, so the checkout leaves the
# measured interval and a cell starts compiling within a second of its claim.
#
# Metadata attributes, all optional:
#   gcc-version       crosstool release to install (default 16.2.0)
#   binutils-version  the binutils half of the folder name the farm script
#                     builds from FARM_GCC_CURRENT (default 2.47)
#   toolchains        space-separated crosstool targets (default alpha and m68k)
#   kernel-ref        the tag under test (default v7.3-rc4)
#   kernel-repo       where to fetch it from
#   source-slots      how many pristine trees to prepare (default 4)
set -eux
export DEBIAN_FRONTEND=noninteractive

meta() {
    curl -sf -H 'Metadata-Flavor: Google' \
        "http://metadata.google.internal/computeMetadata/v1/instance/attributes/$1" || true
}

apt-get update -q
apt-get install -y -q build-essential flex bison libssl-dev libelf-dev bc git \
    python3 kmod cpio rsync libncurses-dev dwarves zstd lz4 xz-utils clang lld llvm \
    curl ca-certificates time

CV=$(meta gcc-version); CV=${CV:-16.2.0}
BU=$(meta binutils-version); BU=${BU:-2.47}
targets=$(meta toolchains); targets=${targets:-alpha-linux m68k-linux}
BASE="https://mirrors.edge.kernel.org/pub/tools/crosstool/files/bin/x86_64/${CV}"
mkdir -p /opt/kernel
for target in ${targets}; do
    tarball="x86_64-gcc-${CV}-nolibc-${target}.tar.xz"
    curl -sfL -o "/tmp/${tarball}" "${BASE}/${tarball}"
    tar -xJf "/tmp/${tarball}" -C /opt/kernel
    rm -f "/tmp/${tarball}"
done
# The tarballs extract to gcc-<CV>-nolibc/<target>; the farm script looks for
# gcc-<CV>-<binutils>-nolibc/<target>, the name FARM_GCC_CURRENT carries.
ln -sfn "/opt/kernel/gcc-${CV}-nolibc" "/opt/kernel/gcc-${CV}-${BU}-nolibc"
# stable-build-arch.sh names an llvm folder for the clang builds; the distro's
# clang stands in for it, as it does on the reference farm.
mkdir -p /opt/kernel/llvm-16.0.6-x86_64
ln -sfn /usr/bin /opt/kernel/llvm-16.0.6-x86_64/bin

# The identities the comparison rejects a run for, in the startup log.
clang --version | head -n 1
for target in ${targets}; do
    prefix="${target%-linux}-linux-"
    gcc_bin="/opt/kernel/gcc-${CV}-nolibc/${target}/bin/${prefix}gcc"
    "${gcc_bin}" --version | head -n 1
    "${gcc_bin}" -Wa,--version -c -x assembler /dev/null -o /dev/null 2>/dev/null | head -n 1
done

ref=$(meta kernel-ref); ref=${ref:-v7.3-rc4}
repo=$(meta kernel-repo)
repo=${repo:-https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git}
slots=$(meta source-slots); slots=${slots:-4}

git config --system user.email node@dispat.invalid
git config --system user.name "dispat node"
git config --system --add safe.directory '*'
install -d -m 0777 /srv/farm /srv/farm/src /srv/farm/build /srv/farm/results
cache=/srv/farm/linux.git
git init -q --bare "${cache}"
git -C "${cache}" fetch -q --depth 1 "${repo}" "refs/tags/${ref}:refs/tags/${ref}"
rev=$(git -C "${cache}" rev-parse "refs/tags/${ref}^{commit}")
for i in $(seq 0 $((slots - 1))); do
    git -C "${cache}" worktree add -q --detach "/srv/farm/src/slot${i}" "${rev}"
    # A cell checks the tree is the revision under test and unmodified. That
    # check reads every tracked file's metadata, which costs seconds on a tree
    # no one has touched yet, so pay it here rather than inside a release.
    git -C "/srv/farm/src/slot${i}" diff --quiet HEAD
done
printf '%s\n' "${rev}" > /srv/farm/revision
chmod -R a+rwX /srv/farm
touch /var/lib/dispat-worker-ready
