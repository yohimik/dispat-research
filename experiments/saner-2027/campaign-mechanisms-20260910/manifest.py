#!/usr/bin/env python3
"""Hash all retained campaign files except the manifest itself."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('campaign', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    campaign = args.campaign.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f'refusing to overwrite {output}')
    files = {}
    for path in sorted(campaign.rglob('*')):
        if path.is_file() and path != output and '__pycache__' not in path.parts:
            files[str(path.relative_to(campaign))] = {
                'bytes': path.stat().st_size,
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            }
    result = {'generated_utc': datetime.now(timezone.utc).isoformat(),
              'campaign': str(campaign), 'regular_files': len(files), 'files': files}
    with output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'output': str(output), 'regular_files': len(files)}, sort_keys=True))


if __name__ == '__main__':
    main()
