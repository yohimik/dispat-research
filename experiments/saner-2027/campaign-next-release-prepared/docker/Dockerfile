ARG DISPAT_IMAGE
FROM ${DISPAT_IMAGE} AS official
FROM docker@sha256:eccaacfeed644c7de222ff047483568cb988dde95476fbaaf10ea2d04921bb66
ARG DISPAT_IMAGE
LABEL org.dispat.research.source-image="${DISPAT_IMAGE}"
COPY apk.lock /tmp/apk.lock
RUN apk add --no-cache $(cat /tmp/apk.lock)
COPY --from=official /usr/local/bin/dispat /usr/local/bin/dispat
RUN apk info -v | sort > /toolchain-apk.txt
ENV DISPAT_UPDATE_CHECK=0 NPM_CONFIG_UPDATE_NOTIFIER=false
ENTRYPOINT []
