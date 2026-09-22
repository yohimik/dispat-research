#!/usr/bin/env python3
"""Export image-build inputs without Git history or QEMU rootfs assets.

The destination must not exist. Initialize it as a separate Git repository before
dispatching; never remove history or assets from the original farm repository.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    files = subprocess.check_output(
        ['git', '-C', str(root), 'ls-files', '-z', '--', 'bin', 'kconfig'])
    paths = [p.decode() for p in files.split(b'\0') if p]
    paths += ['dispat/' + p for p in (
        'run-cell.sh', 'checkout.py', 'results.py', 'generate.py', 'kernel/ref.env')]
    args.destination.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for path in paths:
        source = root / path
        target = args.destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        hashes[path] = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest = dict(
        source_commit=subprocess.check_output(
            ['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip(),
        scope='image builds only; no QEMU/rootfs assets',
        files=hashes,
    )
    (args.destination / 'source-manifest.json').write_text(
        json.dumps(manifest, indent=2) + '\n')
    print(f'Exported {len(paths)} files to {args.destination}')


if __name__ == '__main__':
    main()
