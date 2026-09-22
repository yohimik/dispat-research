# syntax=docker/dockerfile:1.7
# The experiment binary, rebuilt from a pinned commit of github.com/yohimik/dispat
# with the recipe the experiment binaries were built with on 2026-09-22:
# go1.26.5, CGO_ENABLED=0, -trimpath, -buildvcs=false, the version stamped
# through -X cli.Version (unstamped builds report "dev"), built from
# services/dispat inside the repository's go.work workspace so the pkg/*
# modules resolve to the checkout and not to published modules.
#
# Go builds are reproducible across host platforms for a fixed toolchain and
# flags, so the build stage runs on the builder's own platform and cross
# compiles; the bytes are the same whether built on arm64 or amd64.
#
#   docker buildx build --platform linux/amd64 \
#     --build-arg DISPAT_COMMIT=272772cb62a874289e97c5efbfab1a5c33b03efc \
#     --build-arg DISPAT_VERSION=1.11.0-rc.4+main.272772cb \
#     --output type=local,dest=out .
#   sha256sum out/dispat
ARG GO_IMAGE=golang:1.26.5-alpine@sha256:0178a641fbb4858c5f1b48e34bdaabe0350a330a1b1149aabd498d0699ff5fb2
FROM --platform=$BUILDPLATFORM ${GO_IMAGE} AS build
RUN apk add --no-cache git
ARG DISPAT_REPO=https://github.com/yohimik/dispat.git
ARG DISPAT_COMMIT=272772cb62a874289e97c5efbfab1a5c33b03efc
# Empty means an unstamped build that reports "dev".
ARG DISPAT_VERSION=1.11.0-rc.4+main.272772cb
# Filled by BuildKit from --platform; do not give them defaults, a default shadows the value.
ARG TARGETOS
ARG TARGETARCH
RUN git clone --quiet "${DISPAT_REPO}" /src && git -C /src checkout --quiet --detach "${DISPAT_COMMIT}" \
    && git -C /src rev-parse HEAD > /src-commit
WORKDIR /src/services/dispat
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    set -eu; \
    ldflags="-s -w"; \
    if [ -n "${DISPAT_VERSION}" ]; then \
      ldflags="${ldflags} -X github.com/yohimik/dispat/services/dispat/internal/cli.Version=${DISPAT_VERSION}"; \
    fi; \
    mkdir -p /out; \
    GOOS="${TARGETOS}" GOARCH="${TARGETARCH}" CGO_ENABLED=0 \
      go build -trimpath -buildvcs=false -ldflags "${ldflags}" -o /out/dispat .; \
    go version > /out/dispat.toolchain; \
    go version -m /out/dispat > /out/dispat.buildinfo; \
    cp /src-commit /out/dispat.commit; \
    sha256sum /out/dispat | tee /out/dispat.sha256

FROM scratch AS export
COPY --from=build /out/ /
