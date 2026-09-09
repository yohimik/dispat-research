#!/usr/bin/env python3
"""Run the frozen matrix in Docker and append exact start/end provenance."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time


HERE = Path(__file__).resolve().parent


def append(path, value):
    with path.open('a') as stream:
        stream.write(json.dumps(value, sort_keys=True) + '\n')
        stream.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    args = parser.parse_args()
    if '/' in args.name or args.name in ('', '.', '..'):
        raise SystemExit('run name must be one path component')
    output = HERE / 'runs' / args.name
    log = HERE / f'{args.name}.log'
    execution = HERE / f'{args.name}-execution.jsonl'
    if output.exists() or log.exists() or execution.exists():
        raise SystemExit('refusing to overwrite existing run evidence')
    lock = json.loads((HERE / 'release-lock.json').read_text())
    command = [
        'docker', 'run', '--rm', '--network', 'none', '--cpus', '2', '--memory', '4g',
        '--platform', 'linux/arm64', '-v', f'{HERE}:/campaign', '-w', '/campaign',
        lock['runner_image'], 'python3', 'execute.py', f'runs/{args.name}',
    ]
    started = datetime.now(timezone.utc)
    append(execution, {'event': 'start', 'utc': started.isoformat(), 'command': command})
    monotonic_start = time.monotonic()
    with log.open('x') as stream:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, bufsize=1)
        for line in process.stdout:
            print(line, end='', flush=True)
            stream.write(line)
            stream.flush()
        returncode = process.wait()
    ended = datetime.now(timezone.utc)
    append(execution, {'event': 'end', 'utc': ended.isoformat(), 'exit': returncode,
                       'elapsed_seconds': round(time.monotonic() - monotonic_start, 6)})
    raise SystemExit(returncode)


if __name__ == '__main__':
    main()
