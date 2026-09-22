#!/bin/sh
# run-subset-sharded.sh <worktree> <log-prefix> <name-regex> [shards=6] [count=1]
# Shards one named subset of the integration suite over N processes.
set -u
tree=$1; prefix=$2; filter=$3; shards=${4:-6}; count=${5:-1}
export PATH=/Users/yohimik/sdk/go1.26.5/bin:$PATH
cd "$tree" || exit 1
names=$(go test -C tests/integration . -list "$filter" 2>/dev/null | grep -E "$filter") || exit 1
rm -f "$prefix"-shard-*.names
i=0
for n in $names; do
    echo "$n" >> "$prefix-shard-$((i % shards)).names"
    i=$((i + 1))
done
s=0
while [ $s -lt "$shards" ]; do
    if [ -f "$prefix-shard-$s.names" ]; then
        pattern="^($(paste -sd '|' "$prefix-shard-$s.names"))\$"
        ( go test -C tests/integration . -run "$pattern" -count="$count" -timeout 40m > "$prefix-shard-$s.log" 2>&1
          echo "shard $s exit=$?" >> "$prefix-shard-$s.log" ) &
    fi
    s=$((s + 1))
done
wait
s=0
while [ $s -lt "$shards" ]; do
    if [ -f "$prefix-shard-$s.log" ]; then
        grep -E "^(--- FAIL|FAIL|ok |shard)" "$prefix-shard-$s.log" | head -12
    fi
    rm -f "$prefix-shard-$s.names"
    s=$((s + 1))
done
