# syntax=docker/dockerfile:1.7
# An LLVM build node, as .ci/dispat/gce/worker-startup.sh of yohimik/llvm-project
# (branch dispat-gce, 952c2de4) provisioned it on 2026-09-22, made reproducible:
# the Ubuntu 24.04 base image pinned by digest, the apt packages from the archive
# snapshot of the measurement day (the runs used g++ 13.3.0, cmake 3.28.3 and
# ninja 1.11.1 from Ubuntu 24.04.5), and the dispat binary docker/dispat rebuilds.
# The orchestrator uses the same image: the bundle package needs the compiler
# for the recipe's identity record (REPORT.md, attempt 2).
#
# Self-contained: no build context is needed.
ARG UBUNTU_IMAGE=ubuntu:24.04@sha256:008173c23f95b170204355c12626cb5a965d779a7e1283b09e9cffbb1bf33ca3
ARG DISPAT_IMAGE=dispat-experiment:pinned
FROM ${DISPAT_IMAGE} AS dispat

FROM ${UBUNTU_IMAGE}
ARG APT_SNAPSHOT=20260922T000000Z
ENV DEBIAN_FRONTEND=noninteractive
RUN set -eux; \
    apt-get update --snapshot "${APT_SNAPSHOT}"; \
    apt-get install -o "Acquire::Snapshot=${APT_SNAPSHOT}" -y -q \
      build-essential cmake ninja-build python3 git lld \
      zlib1g-dev libzstd-dev libxml2-dev curl ca-certificates \
      time openssh-client rsync xz-utils; \
    dpkg-query -W -f='${Package}=${Version}\n' > /etc/apt-packages.lock; \
    rm -rf /var/lib/apt/lists/*
COPY --from=dispat /dispat /usr/local/bin/dispat
COPY --from=dispat /dispat.sha256 /dispat.buildinfo /dispat.commit /etc/dispat/
RUN set -eux; \
    git config --system user.email node@dispat.invalid; \
    git config --system user.name "dispat node"; \
    git config --system --add safe.directory '*'
RUN cat > /usr/local/bin/node-identity <<'SH'
#!/bin/bash
# The identities build.py records in every receipt.
set -eu
dispat --version 2>/dev/null | tail -n 1
cat /etc/dispat/dispat.sha256
c++ --version | head -n 1
cmake --version | head -n 1
echo "ninja $(ninja --version)"
SH
RUN chmod 0755 /usr/local/bin/node-identity
WORKDIR /home
