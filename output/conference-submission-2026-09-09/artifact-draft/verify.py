#!/usr/bin/env python3
"""Verify review-copy integrity and recompute selected paper counts offline.

This reads saved observations. It does not rerun Dispat or prove the theorems.
Requires Python 3.8+ and the standard library only; no network or writes.
"""
import collections
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def main():
    manifest = read(ROOT / 'MANIFEST.json')
    seen = set()
    for entry in manifest:
        name = entry['file']
        require(name not in seen, 'Duplicate manifest entry: ' + name)
        seen.add(name)
        path = (ROOT / name).resolve()
        require(ROOT in path.parents, 'Path outside artifact: ' + name)
        require(path.is_file(), 'Missing file: ' + name)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'],
                'Hash mismatch: ' + name)
    print('Verified %d review-copy hashes.' % len(seen))
    e1 = ROOT / 'results-1.8.2/e1'
    totals = {}
    for profile in ('core', 'full'):
        paths = sorted(e1.glob(profile + '-*/e1-' + profile + '-*.json'))
        require(len(paths) == 2, 'Expected both seed batches for ' + profile)
        rows = []
        for path in paths:
            record = read(path)
            batch = record['rows']
            summary = record['summary']
            require(len(batch) == summary['instances'], 'Instance count: ' + str(path))
            require(summary['invalid'] == 0, 'Invalid executions: ' + str(path))
            require(sum(bool(r.get('rejection')) for r in batch) == summary['rejected'],
                    'Rejection count: ' + str(path))
            require(sum(not r['diffs'] for r in batch) == summary['clean'],
                    'Clean count: ' + str(path))
            classes = collections.Counter(d[1] for r in batch for d in r['diffs'])
            require(dict(classes) == summary['divergence_classes'],
                    'Difference classifications: ' + str(path))
            rows.extend(batch)
        require(len({r['seed'] for r in rows}) == len(rows), 'Overlapping seed batches')
        rejected = sum(bool(r.get('rejection')) for r in rows)
        require(all(r['rejection']['code'] == 'E195' for r in rows if r.get('rejection')),
                'Unexpected rejection reason')
        totals[profile] = {'instances': len(rows), 'matching': sum(not r['diffs'] for r in rows),
                           'accepted': len(rows) - rejected, 'rejected': rejected,
                           'differing_rows': sum(len(r['diffs']) for r in rows)}
    require(totals['core']['instances'] == totals['core']['matching'] == 1500, 'Core claim')
    require(totals['full'] == {'instances':1500, 'matching':550, 'accepted':997,
                              'rejected':503, 'differing_rows':1914}, 'Full-profile claim')
    print(json.dumps(totals, indent=2))
    vectors = read(e1 / 'ccme2-vectors.json')
    require(len(vectors['results']) == vectors['total'] == 6, 'Vector count')
    require(all(r['pass'] and not r['failures'] for r in vectors['results']), 'Failed vector')
    recovery = [r for p in sorted((ROOT/'results-1.8.2/e4').glob('rep*/e4c-recovery.json')) for r in read(p)]
    require(len(recovery) == 24 and all(r['converged'] and r['g_ok'] and not r['invariant_errors'] for r in recovery), 'Recovery claim')
    require(max(r['runs'] for r in recovery) == 4, 'Recovery run bound')
    with (ROOT/'results-1.8.2/e4/timing.csv').open(newline='') as stream:
        cells = list(csv.DictReader(stream))
    require(len(cells) == 8, 'Timing cell count')
    for p in sorted((ROOT/'results-1.8.2/e2').glob('dispat-rep*/verdict.json')):
        require(read(p)['passed'], 'Orphan recovery verdict: ' + str(p))
    faults = sorted((ROOT/'results-1.8.2/e5').glob('*/verdict.json'))
    require(len(faults) == 3, 'Fault scenario count')
    for p in faults:
        record = read(p)
        require(record['passed'] and all(c['ok'] for c in record['checks']), 'Fault verdict: ' + str(p))
    print('6 vectors; 24 recovered episodes, maximum 4 runs; 8 timing cells; 3 fault scenarios.')
    print('PASS: selected claims agree with saved records. This is not an experiment rerun.')


if __name__ == '__main__':
    main()
