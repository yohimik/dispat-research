#!/usr/bin/env python3
"""Restore exact replay heads and tags. Refuse to overwrite existing checkouts."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
def git(*args):
    return subprocess.check_output(['git', *map(str,args)], text=True).strip()

def main():
    for lock in sorted((ROOT/'experiments/fixture-locks').glob('*.json')):
        spec = json.loads(lock.read_text())
        target = ROOT/'experiments/e3a/repos'/lock.stem
        if target.exists():
            raise SystemExit(f'Refusing to overwrite {target}; verify or relocate it first.')
        if spec['status'].strip():
            raise SystemExit(f'{lock}: dirty original needs a separately reviewed restoration.')
        target.parent.mkdir(parents=True, exist_ok=True)
        git('clone', '--no-checkout', '--no-tags', spec['origin'].strip(), target)
        refs = [line.split() for line in spec['tags'].splitlines() if line.strip()]
        for offset in range(0, len(refs), 100):
            git('-C',target,'fetch','--no-tags','origin',*[oid for oid, _ in refs[offset:offset+100]])
        for oid, ref in refs:
            git('-C',target,'update-ref',ref,oid)
        head=spec['head'].strip()
        git('-C',target,'fetch','--no-tags','origin',head)
        git('-C',target,'checkout','--detach',head)
        assert git('-C',target,'rev-parse','HEAD') == head
        for oid, ref in refs:
            assert git('-C',target,'rev-parse',ref) == oid, ref
        print(f'Restored {lock.stem} at {head} with {len(refs)} locked tags.')

if __name__ == '__main__':
    main()
