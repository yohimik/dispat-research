#!/bin/bash
# Reproduce the commit-tree equivalence check and deterministic final fixture
# validation used after the failed E4 timing attempts.
set -eu
OUT=${1:-/results/fixture-provenance}
mkdir -p "$OUT"

run_fsck() {
  name=$1
  repo=$2
  set +e
  git -C "$repo" fsck --full > "$OUT/$name-fsck.stdout" 2> "$OUT/$name-fsck.stderr"
  rc=$?
  set -e
  echo "$rc" > "$OUT/$name-fsck.exit"
  git -C "$repo" rev-parse HEAD > "$OUT/$name-head.txt"
  return 0
}

python3 e4/gen.py 20 layered 3 5 42 /tmp/e4-normal > "$OUT/small-normal-generate.log"
REALIZE_COMMIT_TREE=1 python3 e4/gen.py 20 layered 3 5 42 /tmp/e4-commit-tree > "$OUT/small-commit-tree-generate.log"
run_fsck small-normal /tmp/e4-normal
run_fsck small-commit-tree /tmp/e4-commit-tree
git -C /tmp/e4-normal show-ref > "$OUT/small-normal-refs.txt"
git -C /tmp/e4-commit-tree show-ref > "$OUT/small-commit-tree-refs.txt"
git -C /tmp/e4-normal log --format='%H%x1f%P%x1f%an%x1f%ae%x1f%B%x1f' \
  --name-only --diff-merges=first-parent HEAD > "$OUT/small-normal-log.txt"
git -C /tmp/e4-commit-tree log --format='%H%x1f%P%x1f%an%x1f%ae%x1f%B%x1f' \
  --name-only --diff-merges=first-parent HEAD > "$OUT/small-commit-tree-log.txt"
cmp "$OUT/small-normal-head.txt" "$OUT/small-commit-tree-head.txt"
cmp "$OUT/small-normal-refs.txt" "$OUT/small-commit-tree-refs.txt"
cmp "$OUT/small-normal-log.txt" "$OUT/small-commit-tree-log.txt"
echo exact-equivalence-pass > "$OUT/small-equivalence.verdict"

python3 e4/gen.py 1000 layered 1000 0 42 /tmp/e4-u1000-normal > "$OUT/u1000-normal-generate.log"
run_fsck u1000-normal /tmp/e4-u1000-normal
REALIZE_COMMIT_TREE=1 python3 e4/gen.py 1000 layered 1000 0 42 /tmp/e4-u1000-commit-tree > "$OUT/u1000-commit-tree-generate.log"
run_fsck u1000-commit-tree /tmp/e4-u1000-commit-tree
cmp "$OUT/u1000-normal-head.txt" "$OUT/u1000-commit-tree-head.txt"
REALIZE_COMMIT_TREE=1 python3 e4/gen.py 1000 layered 200 5000 42 /tmp/e4-pad5000 > "$OUT/pad5000-generate.log"
run_fsck pad5000 /tmp/e4-pad5000

{
  echo "small_normal_fsck=$(cat "$OUT/small-normal-fsck.exit")"
  echo "small_commit_tree_fsck=$(cat "$OUT/small-commit-tree-fsck.exit")"
  echo "small_equivalent=yes"
  echo "u1000_normal_fsck=$(cat "$OUT/u1000-normal-fsck.exit")"
  echo "u1000_commit_tree_fsck=$(cat "$OUT/u1000-commit-tree-fsck.exit")"
  echo "u1000_heads_equal=yes"
  echo "pad5000_commit_tree_fsck=$(cat "$OUT/pad5000-fsck.exit")"
} > "$OUT/verdict.txt"

sha256sum e4/verify_fixture_provenance.sh e4/timing.py e4/gen.py \
  shared/realize.py > "$OUT/source-sha256.txt"
find "$OUT" -type f ! -name SHA256SUMS -print0 | sort -z | \
  xargs -0 sha256sum > "$OUT/SHA256SUMS"
