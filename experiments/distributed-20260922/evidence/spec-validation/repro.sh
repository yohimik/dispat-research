#!/bin/sh
# Reproduce the release-records defect with the current binary.
set -eu
export PATH=/tmp/dispat-gate:$PATH
W=/private/tmp/claude-501/-Users-yohimik-Projects-dispat/aba20193-908a-4dbf-a0ef-363528c9fa79/scratchpad/repro
rm -rf "$W"
mkdir -p "$W"
cd "$W"

git init --bare -q remote.git
REGISTRY="$W/registry.log"
: > "$REGISTRY"

mk_config() {
  cat > "$1/dispat.yaml" <<YAML
changelog:
  enabled: false
commit:
  enabled: true
  push: true
spaces:
  libs:
    path: packages
    flow:
      build: build
      publish: publish
scripts:
  build: "echo building \$DISPAT_PACKAGE"
  publish: "sh -c 'echo \"\$DISPAT_PACKAGE@\$DISPAT_NEW_VERSION\" >> $REGISTRY'"
YAML
}

git clone -q remote.git a
cd a
git config user.email a@example.com
git config user.name a
mkdir -p packages/core
printf '{"name":"core","version":"0.0.0"}\n' > packages/core/package.json
mk_config "$W/a"
git add -A
git commit -qm 'feat(core): first'
git push -q origin HEAD:refs/heads/main
git branch -q -M main
git branch -q --set-upstream-to=origin/main main 2>/dev/null || true
cd "$W"

echo "=== clone b now (no tags yet) ==="
git clone -q remote.git b
cd b
git config user.email b@example.com
git config user.name b
cd "$W"

echo "=== release in a ==="
cd a
DISPAT_UNSAFE_DISABLE_LOCK=true dispat release --config dispat.yaml 2>&1 | tail -20
cd "$W"
echo "--- registry after a ---"; cat "$REGISTRY"
echo "--- remote tags after a ---"; git --git-dir=remote.git tag -l | sed 's/^/  /'
git --git-dir=remote.git rev-parse 'refs/tags/core@0.1.0^{}' | sed 's/^/  tag commit: /'

echo
echo "=== REPRODUCTION 1: release in b (stale clone, no tags) ==="
cd b
DISPAT_UNSAFE_DISABLE_LOCK=true dispat release --config dispat.yaml 2>&1 | tail -30 || echo "exit=$?"
echo "exit code: $?"
cd "$W"
echo "--- registry after b ---"; cat "$REGISTRY"
echo "--- remote tag after b ---"; git --git-dir=remote.git rev-parse 'refs/tags/core@0.1.0^{}'

echo
echo "=== REPRODUCTION 2: new commit in a, --no-tags clone c ==="
cd a
git pull -q --rebase origin main 2>/dev/null || true
printf '{"name":"core","version":"0.1.0","x":1}\n' > packages/core/package.json
git add -A
git commit -qm 'feat(core): second'
git push -q origin HEAD:refs/heads/main
cd "$W"
git clone -q --no-tags remote.git c
cd c
git config user.email c@example.com
git config user.name c
DISPAT_UNSAFE_DISABLE_LOCK=true dispat release --config dispat.yaml 2>&1 | tail -30 || echo "exit=$?"
cd "$W"
echo "--- registry after c ---"; cat "$REGISTRY"
echo "--- remote tag after c ---"; git --git-dir=remote.git rev-parse 'refs/tags/core@0.1.0^{}'
echo "--- remote log ---"; git --git-dir=remote.git log --oneline --all | sed 's/^/  /'
