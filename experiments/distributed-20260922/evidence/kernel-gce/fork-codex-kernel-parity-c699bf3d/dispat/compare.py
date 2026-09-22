#!/usr/bin/env python3
"""Reject a benchmark unless coverage, tools, revision and elapsed time match."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path


def compare(reference, reports, elapsed):
    problems = []
    cases = []
    if not isinstance(reference.get('compiler'), str) or not reference['compiler']:
        problems.append('baseline has no exact compiler value')
    if ('assembler' not in reference or
            not (reference['assembler'] is None or
                 isinstance(reference['assembler'], str) and reference['assembler'])):
        problems.append('baseline has no exact assembler value')
    for path in reports:
        result = json.loads(path.read_text())
        if result['status'] != 'passed':
            problems.append(f'{path}: failed cell')
        if result['revision'] != reference['kernel_revision']:
            problems.append(f'{path}: different kernel revision')
        cases.extend(case['line'] for case in result['cases'])
        log = (path.parent / 'cell.log').read_text().splitlines()
        for key, prefix in [('compiler', 'Compiler version: '),
                            ('assembler', 'Assembler version: ')]:
            actual = [line[len(prefix):] for line in log if line.startswith(prefix)]
            expected = reference.get(key)
            # A null assembler is meaningful for LLVM builds: the farm script
            # emits no assembler line. Require that absence just as strictly as
            # a non-empty GNU assembler version.
            if actual != ([expected] if isinstance(expected, str) else []):
                problems.append(f'{path}: different or missing {key}')
    if Counter(cases) != Counter(reference['cases']):
        problems.append('configuration results differ (including duplicates)')
    if not math.isfinite(elapsed) or elapsed <= 0 or elapsed > reference['seconds']:
        problems.append('elapsed time exceeds reference or is invalid')
    return dict(accepted=not problems, problems=problems,
                reference_seconds=reference['seconds'], elapsed_seconds=elapsed,
                speedup=reference['seconds'] / elapsed if elapsed > 0 else None,
                cases=len(cases))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--arch', required=True)
    parser.add_argument('--elapsed', type=float, required=True,
                        help='whole run elapsed seconds, including dispatch and reporting')
    parser.add_argument('reports', type=Path, nargs='+')
    args = parser.parse_args()
    reference = json.loads(args.baseline.read_text())[args.arch]
    result = compare(reference, args.reports, args.elapsed)
    print(json.dumps(result, indent=2))
    return 0 if result['accepted'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
