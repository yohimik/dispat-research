#!/bin/bash
# Startup script of a kernel parity node (every role). It reads its
# instructions from instance metadata, builds the two pinned images from the
# Dockerfiles carried in that metadata, prepares the kernel source pool and
# marks the node ready. Nothing here is specific to the run: the run itself is
# driven over ssh by scripts/kernel/run.sh.
set -eux
exec > >(tee -a /var/log/dispat-node-startup.log) 2>&1
export DEBIAN_FRONTEND=noninteractive

meta() {
    curl -sf -H 'Metadata-Flavor: Google' \
        "http://metadata.google.internal/computeMetadata/v1/instance/attributes/$1" || true
}

apt-get update -q
apt-get install -y -q docker.io git curl ca-certificates
systemctl enable --now docker

user=$(meta node-user); user=${user:-dispat}
# The guest agent creates the login user from the ssh-keys metadata; wait for it.
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
targets=$(meta crosstool-targets); targets=${targets:-alpha-linux m68k-linux}

export DOCKER_BUILDKIT=1
docker build -f "${work}/dispat.Dockerfile" --target export \
    --build-arg "DISPAT_COMMIT=${commit}" --build-arg "DISPAT_VERSION=${version}" \
    -t dispat-experiment:pinned "${work}"
docker build -f "${work}/node.Dockerfile" \
    --build-arg DISPAT_IMAGE=dispat-experiment:pinned \
    --build-arg "APT_SNAPSHOT=${snapshot}" --build-arg "CROSSTOOL_TARGETS=${targets}" \
    -t dispat-kernel-node:pinned "${work}"

# node-run: a command inside the node image as the login user, with that
# user's home, the farm pool and the host network. run.sh uses it for
# everything a node does.
cat > /usr/local/bin/node-run <<'SH'
#!/bin/bash
exec docker run --rm --network host --init \
    --user "$(id -u):$(id -g)" -e HOME="${HOME}" -e USER="${USER}" \
    -e DISPAT_EXECUTION_SECRET -e DISPAT_FARM_SOURCE_POOL -e DISPAT_FARM_RESULTS \
    -v "${HOME}:${HOME}" -v /srv/farm:/srv/farm -w "${PWD}" \
    ${NODE_RUN_ARGS:-} dispat-kernel-node:pinned "$@"
SH
chmod 0755 /usr/local/bin/node-run

install -d -m 0777 -o "${user}" -g "${user}" /srv/farm
ref=$(meta kernel-ref); ref=${ref:-v7.3-rc4}
repo=$(meta kernel-repo)
repo=${repo:-https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git}
slots=$(meta source-slots); slots=${slots:-5}
sudo -u "${user}" -H env HOME="/home/${user}" node-run node-prepare "${ref}" "${repo}" "${slots}"
sudo -u "${user}" -H env HOME="/home/${user}" node-run node-identity | tee "${work}/identity.txt"
docker image inspect dispat-kernel-node:pinned --format '{{.Id}}' > "${work}/node-image-id"
touch /var/lib/dispat-node-ready
