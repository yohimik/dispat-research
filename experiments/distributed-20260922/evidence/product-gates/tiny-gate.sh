#!/bin/sh
# Runs the TinyGo acceptance gate on one commit inside the link bracket (the
# Docker build compiles against the published pkg modules otherwise), then
# unlinks and verifies. Usage: tiny-gate.sh <commit>
set -u
TIP=$1
S=/private/tmp/claude-501/-Users-yohimik-Projects-dispat/aba20193-908a-4dbf-a0ef-363528c9fa79/scratchpad
export PATH=/tmp/dispat-verify:/Users/yohimik/sdk/go1.26.5/bin:$PATH
cd /tmp/dispat-tiny-wt || exit 1
git checkout -q -- . && git checkout -q --detach "$TIP" && git log --oneline -1 | cat
dispat autowriter --package dispat --since all --sync-lock=false --link-local 2>&1 | grep -v 'W131\|W120' | tail -3
echo "replace lines: $(grep -c '^replace' services/dispat/go.mod)"
date -u +%T
docker buildx build --progress plain --file services/dispat/Dockerfile --target tiny-test . > "$S/tiny-test-$TIP.log" 2>&1
echo "tiny-test exit=$?" | tee -a "$S/tiny-test-$TIP.log"
date -u +%T
dispat autowriter --package dispat --since all --sync-lock=false --unlink-local 2>&1 | grep -v 'W131\|W120' | tail -2
dispat scanner --verify-unlinked 2>&1 | tail -1
echo "verify-unlinked exit=$?"
grep -E '"Action":"fail"|panic: test timed out' "$S/tiny-test-$TIP.log" | grep -o '"Test":"[^"]*"' | sort -u | head -20
