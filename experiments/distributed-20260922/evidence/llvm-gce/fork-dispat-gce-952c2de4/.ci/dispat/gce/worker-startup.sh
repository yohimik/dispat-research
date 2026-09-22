#!/bin/bash
# Startup script of an LLVM worker VM: the toolchain an LLVM build needs and a
# marker the operator waits for. The worker process itself is started by
# worker.sh over ssh.
set -eu
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y -q build-essential cmake ninja-build python3 git lld \
    zlib1g-dev libzstd-dev libxml2-dev curl ca-certificates
touch /var/lib/dispat-worker-ready
