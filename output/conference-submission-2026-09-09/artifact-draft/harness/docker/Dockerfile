# The experiments' runtime image: the pinned dispat binary plus python3,
# git and hyperfine, built entirely from the vendored source archive so the
# whole stack is reproducible from this directory alone.
#
#   docker build -t dispat-exp:runtime .
#
# The source under ./src is `git archive 342062d3` of github.com/anonymous-author/dispat.
ARG GO_VERSION=1.26
# Which stage supplies the binary under test:
#   relimg - the official released Docker image (docker.io/anonymous-author/dispat-alpine,
#            pinned by DISPAT_VERSION), whose binary is the published release
#            asset installed by the official install.sh. The default: every
#            experiment runs the exact shipped bytes via the shipped channel.
#   relbin - the GitHub-release asset dropped manually at docker/bin/dispat.
#   build  - compile from the vendored source archive (the original mode).
ARG BIN_STAGE=relimg
ARG DISPAT_VERSION=1.3.1

FROM golang:${GO_VERSION}-alpine AS build
RUN apk add --no-cache git
COPY src /src
WORKDIR /src/services/dispat
# The go.work at the archive root makes the pkg/ modules resolve locally,
# so the binary is built from the pinned tree, not from the module proxy.
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 go build -ldflags "-X github.com/anonymous-author/dispat/services/dispat/internal/cli.Version=exp-342062d3" \
      -o /out/dispat .

FROM alpine:3 AS relbin
COPY bin/dispat /out/dispat
RUN chmod +x /out/dispat

FROM docker.io/anonymous-author/dispat-alpine:${DISPAT_VERSION} AS official
FROM alpine:3 AS relimg
COPY --from=official /usr/local/bin/dispat /out/dispat

FROM ${BIN_STAGE} AS binsrc

FROM python:3.12-alpine AS runtime
RUN apk add --no-cache git bash hyperfine coreutils
COPY --from=binsrc /out/dispat /usr/local/bin/dispat
# git identity for the realized instance repositories
RUN git config --global user.email experiment@example.invalid && \
    git config --global user.name exp && \
    git config --global init.defaultBranch main
WORKDIR /work

# node-side image for E2: the same pinned binary beside npm toolchains.
FROM node:22-slim AS node
RUN apt-get update && apt-get install -y --no-install-recommends git python3 ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=binsrc /out/dispat /usr/local/bin/dispat
RUN git config --global user.email experiment@example.invalid && git config --global user.name exp && git config --global init.defaultBranch main
# Competitor toolchain, latest published as of 2026-08-30, installed once
# at image build so phases never install over the experiment registry.
# Fixtures symlink /opt/tools/node_modules to satisfy nx's local-install check.
RUN mkdir -p /opt/tools && cd /opt/tools && npm init -y >/dev/null && \
    npm i --no-audit --no-fund lerna@10.0.1 nx@23.1.2 @nx/js@23.1.2 turbo@2.10.12 @changesets/cli@3.0.1 && \
    npm cache clean --force >/dev/null 2>&1
ENV PATH=/opt/tools/node_modules/.bin:$PATH
WORKDIR /work
