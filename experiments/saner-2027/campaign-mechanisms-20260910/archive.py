#!/usr/bin/env python3
"""Archive and verify expanded case fixtures, then optionally remove them."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tarfile


def digest(stream):
    value = hashlib.sha256()
    while chunk := stream.read(1024 * 1024):
        value.update(chunk)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    parser.add_argument('--remove-expanded', action='store_true')
    args = parser.parse_args()
    run = args.run.resolve()
    archive = run / 'expanded-fixtures.tar.gz'
    verification = run / 'archive-verification.json'
    if archive.exists() or verification.exists():
        raise SystemExit('refusing to overwrite existing archive evidence')
    roots = []
    for observation in sorted(run.glob('*/observation.json')):
        for name in ('work', 'origin.git'):
            root = observation.parent / name
            if root.is_dir():
                roots.append(root)
    if not roots:
        raise SystemExit('no expanded fixture roots found')
    expected = {}
    for root in roots:
        for path in sorted(root.rglob('*')):
            if path.is_file():
                relative = str(path.relative_to(run))
                with path.open('rb') as stream:
                    expected[relative] = {'sha256': digest(stream), 'bytes': path.stat().st_size}
    with tarfile.open(archive, 'x:gz', compresslevel=9) as stream:
        for root in roots:
            stream.add(root, arcname=str(root.relative_to(run)), recursive=True)
    observed = {}
    with tarfile.open(archive, 'r:gz') as stream:
        for member in stream.getmembers():
            if member.isfile():
                extracted = stream.extractfile(member)
                observed[member.name] = {'sha256': digest(extracted), 'bytes': member.size}
    if observed != expected:
        archive.unlink()
        raise SystemExit('archive content differs from expanded fixtures; removed invalid archive')
    archive_sha256 = hashlib.sha256(archive.read_bytes()).hexdigest()
    result = {
        'status': 'PASS',
        'verified_utc': datetime.now(timezone.utc).isoformat(),
        'run': str(run),
        'archive': archive.name,
        'archive_sha256': archive_sha256,
        'regular_files': len(expected),
        'uncompressed_bytes': sum(row['bytes'] for row in expected.values()),
        'roots': [str(root.relative_to(run)) for root in roots],
        'files': expected,
        'expanded_removed': bool(args.remove_expanded),
    }
    with verification.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    if args.remove_expanded:
        for root in roots:
            shutil.rmtree(root)
    print(json.dumps({key: result[key] for key in
                      ('status', 'archive', 'archive_sha256', 'regular_files',
                       'uncompressed_bytes', 'expanded_removed')}, sort_keys=True))


if __name__ == '__main__':
    main()
