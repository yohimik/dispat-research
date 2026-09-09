#!/usr/bin/env python3
"""Freeze protocol and executable inputs without overwriting prior evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    parser.add_argument('--phase', required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f'refusing to overwrite {output}')
    names = ('PROTOCOL.md', 'execute.py', 'publisher.py', 'verify.py',
             'provenance.py', 'archive.py', 'freeze.py', 'run.py', 'release-lock.json')
    result = {
        'frozen_utc': datetime.now(timezone.utc).isoformat(),
        'phase': args.phase,
        'files': {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names},
        'prospective_matrix': {
            'fault_episodes': 120, 'no_fault_controls': 10,
            'foreign_identity_cases': 10, 'total': 140, 'seed': 20260910,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
