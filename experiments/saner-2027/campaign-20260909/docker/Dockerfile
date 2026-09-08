FROM yohimik/dispat-alpine@sha256:4c0ad4b8268dd10dbb136008798c1b07ffc1c0c7c534b8465a9f5edcab0e7bfd AS official
FROM docker@sha256:eccaacfeed644c7de222ff047483568cb988dde95476fbaaf10ea2d04921bb66
COPY apk.lock /tmp/apk.lock
RUN apk add --no-cache $(cat /tmp/apk.lock)
COPY --from=official /usr/local/bin/dispat /usr/local/bin/dispat
RUN apk info -v | sort > /toolchain-apk.txt
ENV DISPAT_UPDATE_CHECK=0 NPM_CONFIG_UPDATE_NOTIFIER=false
ENTRYPOINT []
