#!/bin/sh
# Gate 0: a hand-built 3-package instance; dump the JSON plan events so
# shared/planjson.py can be frozen against real field names.
set -eu
W=$(mktemp -d)
cd "$W"
git init -q .
mkdir -p packages/core packages/cli packages/ui
cat > packages/core/package.json <<'EOF'
{"name": "core", "version": "1.0.0"}
EOF
cat > packages/cli/package.json <<'EOF'
{"name": "cli", "version": "1.0.0", "dependencies": {"core": "^1.0.0"}}
EOF
cat > packages/ui/package.json <<'EOF'
{"name": "ui", "version": "1.0.0", "dependencies": {"core": "^1.0.0"}}
EOF
cat > dispat.yaml <<'EOF'
spaces:
  packages:
    path: packages
packages:
  cli:
    dependencies: [core]
  ui:
    dependencies: [core]
EOF
git add -A
git commit -qm "chore: baseline"
git tag core@1.0.0
git tag cli@1.0.0
git tag ui@1.0.0
git commit -q --allow-empty -m "feat(core)^: streaming reader"
echo "=== raw JSON events ==="
dispat status --log-format json 2>&1 | python3 /exp/shared/planjson.py
echo "=== full stream tail ==="
dispat status --log-format json 2>&1 | tail -8
