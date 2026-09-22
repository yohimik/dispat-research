#!/usr/bin/env python3
"""Serialize updates to a node's shared kernel cache, then create a private tree."""
import fcntl
import json
from pathlib import Path
import subprocess
import sys
import time


def checkout(cache, repo, ref, destination, timings_path=None):
    started = time.monotonic()
    timings = {}
    cache = Path(cache)
    cache.parent.mkdir(parents=True, exist_ok=True)
    with Path(str(cache) + '.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        timings['cache_lock_seconds'] = time.monotonic() - started
        if not cache.exists():
            subprocess.run(['git', 'init', '-q', '--bare', str(cache)], check=True)
        command = ['git', '-C', str(cache)]
        tag = 'refs/tags/' + ref
        started = time.monotonic()
        subprocess.run(command + ['fetch', '-q', '--depth', '1', repo, tag + ':' + tag],
                       check=True)
        timings['kernel_fetch_seconds'] = time.monotonic() - started
        revision = subprocess.check_output(command + ['rev-parse', tag + '^{commit}'],
                                           text=True).strip()
        started = time.monotonic()
        subprocess.run(command + ['worktree', 'add', '-q', '--detach', destination, revision],
                       check=True)
        timings['kernel_checkout_seconds'] = time.monotonic() - started
    if timings_path:
        Path(timings_path).write_text(json.dumps(timings) + '\n')
    return revision


if __name__ == '__main__':
    print(checkout(*sys.argv[1:]))
