#!/usr/bin/env python3
"""Create the descriptive aggregate without changing raw run evidence."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path


def add(bucket, key, lost, passed):
    row = bucket[key]
    row['episodes'] += 1
    row['passed'] += passed
    row['failed'] += not passed
    row['source_mutant_losing_episodes'] += bool(lost)
    row['source_mutant_lost_obligations'] += len(lost)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f'refusing to overwrite {output}')
    cases = json.loads((run / 'cases.json').read_text())
    dimensions = {name: defaultdict(lambda: defaultdict(int))
                  for name in ('class', 'channel', 'graph', 'boundary')}
    failed_cases = []
    mechanisms = {
        'repeated_fault_plan_and_tags_stable': {'passed': 0, 'denominator': 0},
        'successful_repair_empty_plan': {'passed': 0, 'denominator': 0},
        'one_artifact_write_per_obligation': {'passed': 0, 'denominator': 0},
        'foreign_identity_conflict_refused': {'passed': 0, 'denominator': 0},
        'final_noop_plan_empty_and_tags_stable': {'passed': 0, 'denominator': 0},
    }
    for case in cases:
        graph, channel, _target, boundary = case
        label = '-'.join(case)
        observation = json.loads((run / label / 'observation.json').read_text())
        passed = observation.get('status') == 'PASS'
        if not passed:
            failed_cases.append({'case': case, 'error': observation.get('error')})
        lost = observation.get('source_mutant_lost', [])
        case_class = ('fault_matrix' if boundary in ('build', 'before', 'after') else
                      'no_fault_control' if boundary == 'none' else 'foreign_identity')
        add(dimensions['class'], case_class, lost, passed)
        add(dimensions['channel'], channel, lost, passed)
        add(dimensions['graph'], graph, lost, passed)
        add(dimensions['boundary'], boundary, lost, passed)
        for name in ('one_artifact_write_per_obligation',
                     'final_noop_plan_empty_and_tags_stable'):
            mechanisms[name]['denominator'] += 1
            mechanisms[name]['passed'] += passed
        if boundary != 'none':
            for name in ('repeated_fault_plan_and_tags_stable',
                         'successful_repair_empty_plan'):
                mechanisms[name]['denominator'] += 1
                mechanisms[name]['passed'] += passed
        if boundary == 'foreign':
            mechanisms['foreign_identity_conflict_refused']['denominator'] += 1
            mechanisms['foreign_identity_conflict_refused']['passed'] += passed
    execution_path = run.parent.parent / f'{run.name}-execution.jsonl'
    execution = [json.loads(line) for line in execution_path.read_text().splitlines()]
    executor_summary = json.loads((run / 'summary.json').read_text())
    verifier = json.loads((run / 'verifier.json').read_text())
    result = {
        'status': ('PASS' if executor_summary['status'] == 'PASS' and
                   verifier['status'] == 'PASS' and not failed_cases else 'FAIL'),
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'run': str(run),
        'execution': {'start_utc': execution[0]['utc'], 'end_utc': execution[1]['utc'],
                      'elapsed_seconds': execution[1]['elapsed_seconds'],
                      'exit': execution[1]['exit']},
        'executor': executor_summary,
        'offline_consistency_check': {
            'status': verifier['status'], 'errors': verifier['errors'],
            'episodes_checked': verifier['episodes_checked'],
        },
        'failed_or_invalid_cases': failed_cases,
        'strata': {dimension: {key: dict(value) for key, value in sorted(rows.items())}
                   for dimension, rows in dimensions.items()},
        'mechanism_checks': mechanisms,
        'interpretation': {
            'source_mutant': ('Sensitivity of a deficient source-window analytical rule under '
                              'deterministic designed cases; not a competing-product win rate.'),
            'after_write_fault': ('Publisher durably writes a local artifact and returns nonzero; '
                                  'this does not simulate SIGKILL, a network partition, or power loss.'),
            'model': ('Executable stable-channel, one-intent projection over ordered four-node DAGs; '
                      'not a mechanized proof of the full language or implementation refinement.'),
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
