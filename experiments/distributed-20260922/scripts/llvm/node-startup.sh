#!/bin/bash
# Startup script of an LLVM node (orchestrator and workers alike): Docker, the
# two pinned images built from the Dockerfiles in instance metadata, the
# node-run helper, and the ready marker. The run is driven over ssh by
# scripts/llvm/run.sh.
set -eux
exec > >(tee -a /var/log/dispat-node-startup.log) 2>&1
export DEBIAN_FRONTEND=noninteractive

meta() {
    curl -sf -H 'Metadata-Flavor: Google' \
        "http://metadata.google.internal/computeMetadata/v1/instance/attributes/$1" || true
}

apt-get update -q
apt-get install -y -q docker.io git curl ca-certificates rsync
systemctl enable --now docker

user=$(meta node-user); user=${user:-dispat}
for i in $(seq 1 60); do id "${user}" >/dev/null 2>&1 && break; sleep 2; done
id "${user}"
usermod -aG docker "${user}"

work=/srv/dispat
mkdir -p "${work}"
meta dispat-dockerfile > "${work}/dispat.Dockerfile"
meta node-dockerfile > "${work}/node.Dockerfile"
commit=$(meta dispat-commit)
version=$(meta dispat-version)
snapshot=$(meta apt-snapshot); snapshot=${snapshot:-20260922T000000Z}

export DOCKER_BUILDKIT=1
docker build -f "${work}/dispat.Dockerfile" --target export \
    --build-arg "DISPAT_COMMIT=${commit}" --build-arg "DISPAT_VERSION=${version}" \
    -t dispat-experiment:pinned "${work}"
docker build -f "${work}/node.Dockerfile" \
    --build-arg DISPAT_IMAGE=dispat-experiment:pinned --build-arg "APT_SNAPSHOT=${snapshot}" \
    -t dispat-llvm-node:pinned "${work}"

cat > /usr/local/bin/node-run <<'SH'
#!/bin/bash
exec docker run --rm --network host --init \
    --user "$(id -u):$(id -g)" -e HOME="${HOME}" -e USER="${USER}" \
    -e DISPAT_EXECUTION_SECRET \
    -v "${HOME}:${HOME}" -w "${PWD}" \
    ${NODE_RUN_ARGS:-} dispat-llvm-node:pinned "$@"
SH
chmod 0755 /usr/local/bin/node-run
sudo -u "${user}" -H env HOME="/home/${user}" node-run node-identity | tee "${work}/identity.txt"
docker image inspect dispat-llvm-node:pinned --format '{{.Id}}' > "${work}/node-image-id"
touch /var/lib/dispat-node-ready
