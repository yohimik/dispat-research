"""Synthetic immutable local registry adapter; not a product implementation."""
import hashlib
import json
import os
from pathlib import Path
import sys

root = Path(os.environ['FIXTURE_ROOT'])
package = os.environ['DISPAT_PACKAGE']
version = os.environ['DISPAT_NEW_VERSION']
stage = sys.argv[1]
fault = json.loads((root / 'fault.json').read_text()) if (root / 'fault.json').exists() else {}


def event(kind):
    with (root / 'events.jsonl').open('a') as stream:
        stream.write(json.dumps({'package': package, 'version': version, 'stage': stage, 'event': kind}) + '\n')


event('invoke')
denied = fault.get('package') == package
if stage == 'build':
    if denied and fault.get('boundary') == 'build':
        event('injected-failure')
        raise SystemExit(31)
    raise SystemExit(0)
if denied and fault.get('boundary') == 'before':
    event('injected-failure')
    raise SystemExit(32)
payload = json.dumps({'package': package, 'version': version,
                      'source_sha256': hashlib.sha256((Path.cwd() / 'content.txt').read_bytes()).hexdigest()}, sort_keys=True).encode()
destination = root / 'registry' / package / version
destination.parent.mkdir(parents=True, exist_ok=True)
if destination.exists():
    if destination.read_bytes() != payload:
        event('identity-conflict')
        raise SystemExit(34)
    event('identity-match')
else:
    with destination.open('xb') as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    event('write')
if denied and fault.get('boundary') == 'after':
    event('injected-failure')
    raise SystemExit(33)
