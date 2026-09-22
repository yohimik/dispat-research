#!/bin/sh
# Runs the integration suite as N processes over an exact, round-robin split
# of its test names, so a machine with idle cores finishes the suite in a
# fraction of the single-process wall time. The suite has no t.Parallel and
# 57 Setenv calls, so parallelism has to come from processes, not goroutines.
#
#   run-suite-sharded.sh <worktree> <log-prefix> [shards=6]
set -u
tree=$1; prefix=$2; shards=${3:-6}
export PATH=/Users/yohimik/sdk/go1.26.5/bin:$PATH
cd "$tree" || exit 1
names=$(go test -C tests/integration . -list 'Test' 2>/dev/null | grep '^Test') || exit 1
i=0
for n in $names; do
    echo "$n" >> "$prefix-shard-$((i % shards)).names"
    i=$((i + 1))
done
s=0
while [ $s -lt "$shards" ]; do
    pattern="^($(paste -sd '|' "$prefix-shard-$s.names"))\$"
    ( go test -C tests/integration . -run "$pattern" -count=1 -timeout 40m > "$prefix-shard-$s.log" 2>&1
      echo "shard $s exit=$?" >> "$prefix-shard-$s.log" ) &
    s=$((s + 1))
done
wait
s=0
while [ $s -lt "$shards" ]; do
    grep -E "^(--- FAIL|FAIL|ok |shard)" "$prefix-shard-$s.log" | head -12
    rm -f "$prefix-shard-$s.names"
    s=$((s + 1))
done
