#!/usr/bin/env python3
"""Independent offline verifier for a completed mechanism campaign run."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys


GRAPHS = {
    'chain': {'a': [], 'b': ['a'], 'c': ['b'], 'd': ['c']},
    'diamond': {'a': [], 'b': ['a'], 'c': ['a'], 'd': ['b', 'c']},
    'fanout': {'a': [], 'b': ['a'], 'c': ['a'], 'd': ['a']},
    'disconnected': {'a': [], 'b': ['a'], 'c': [], 'd': ['c']},
    'shortcut': {'a': [], 'b': ['a'], 'c': ['a', 'b'], 'd': ['a', 'c']},
}


def load(path):
    return json.loads(path.read_text())


def candidate_plan(text):
    events = []
    for line in text.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    summaries = [e for e in events if e.get('message') == 'release plan ready']
    if len(summaries) != 1:
        raise ValueError(f'expected one plan summary, found {len(summaries)}')
    result = {}
    for event in events:
        message = event.get('message', '')
        if (event.get('package') and event.get('version') and event.get('bump') and
                'held' not in message and
                (message.endswith('changed') or 'catch-up' in message or 'channel-only' in message)):
            result[event['package']] = event['version'].split('->')[-1].strip()
    if len(result) != summaries[0].get('releasing'):
        raise ValueError('candidate count differs from plan summary')
    return result


def descendants(graph, source):
    result = {source}
    changed = True
    while changed:
        before = set(result)
        result.update(node for node, dependencies in graph.items() if set(dependencies) & result)
        changed = result != before
    return result


def expected_cases(pilot):
    if pilot:
        rows = [('chain', channel, 'd', boundary)
                for channel in ('stable', 'beta')
                for boundary in ('none', 'build', 'before', 'after', 'foreign')]
    else:
        rows = [(graph, channel, package, boundary)
                for graph in GRAPHS
                for channel in ('stable', 'beta')
                for package in 'abcd'
                for boundary in ('build', 'before', 'after')]
        rows.extend((graph, channel, 'd', boundary)
                    for graph in GRAPHS
                    for channel in ('stable', 'beta')
                    for boundary in ('none', 'foreign'))
    random.Random(20260910).shuffle(rows)
    return [list(row) for row in rows]


def expected_model_records():
    vertices = tuple('abcd')
    possible_edges = tuple((later, earlier)
                           for later_index, later in enumerate(vertices)
                           for earlier in vertices[:later_index])
    records = Counter()
    totals = Counter(graphs=64, source_instances=256)
    for mask in range(1 << len(possible_edges)):
        chosen = tuple(edge for bit, edge in enumerate(possible_edges) if mask & (1 << bit))
        graph = {node: [provider for consumer, provider in chosen if consumer == node]
                 for node in vertices}
        for source in vertices:
            obligations = descendants(graph, source)
            discovered = {frozenset()}
            frontier = [frozenset()]
            while frontier:
                completed = frontier.pop()
                pending = obligations - completed
                lost = pending if source in completed else set()
                transition_count = 0
                pending_list = sorted(pending)
                for failed_mask in range(1 << len(pending_list)):
                    failed = {node for bit, node in enumerate(pending_list)
                              if failed_mask & (1 << bit)}
                    blocked = set()
                    for failed_node in failed:
                        blocked.update(descendants(graph, failed_node))
                    newly_completed = pending - blocked
                    next_completed = completed | newly_completed
                    residual = obligations - next_completed
                    if residual != pending - newly_completed:
                        raise AssertionError('residual projection failed in verifier model')
                    if bool(newly_completed) != (len(residual) < len(pending)):
                        raise AssertionError('strict-decrease check failed in verifier model')
                    if completed & newly_completed:
                        raise AssertionError('duplicate ledger delivery in verifier model')
                    totals['transitions'] += 1
                    totals['progress_transitions'] += bool(newly_completed)
                    transition_count += 1
                    frozen = frozenset(next_completed)
                    if frozen not in discovered:
                        discovered.add(frozen)
                        frontier.append(frozen)
                totals['states'] += 1
                totals['source_mutant_losing_states'] += bool(lost)
                key = (chosen, source, tuple(sorted(completed)), tuple(sorted(pending)),
                       tuple(sorted(lost)), transition_count)
                records[key] += 1
    totals['projection_violations'] = 0
    return dict(totals), records


def stored_model_records(path):
    records = Counter()
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        row = json.loads(line)
        key = (tuple(tuple(edge) for edge in row['edges']), row['source'],
               tuple(row['completed']), tuple(row['pending']),
               tuple(row['source_mutant_lost']), row['failure_subsets_checked'])
        records[key] += 1
    return records


def check_case(run, case, errors):
    graph_name, channel, target, boundary = case
    label = '-'.join(case)
    folder = run / label
    observation_path = folder / 'observation.json'
    command_dir = folder / 'commands'
    if not observation_path.is_file() or not command_dir.is_dir():
        errors.append(f'{label}: missing observation or command directory')
        return None
    command_paths = sorted(command_dir.glob('*.json'))
    if [path.name for path in command_paths] != [f'{i:04}.json' for i in range(1, len(command_paths) + 1)]:
        errors.append(f'{label}: command sequence is not contiguous')
    commands = []
    for path in command_paths:
        try:
            command = load(path)
            if not isinstance(command['argv'], list) or not isinstance(command['exit'], int):
                raise TypeError('malformed command record')
            commands.append(command)
        except Exception as exc:
            errors.append(f'{label}: invalid {path.name}: {exc}')
            return None
    releases = [command for command in commands if command['argv'][:2] == ['dispat', 'release']]
    statuses = [command for command in commands if command['argv'][:2] == ['dispat', 'status']]
    tag_commands = [command for command in commands if command['argv'] == ['git', 'tag', '--list']]
    permitted_failures = set(id(command) for command in releases)
    for command in commands:
        if command['exit'] != 0 and id(command) not in permitted_failures:
            errors.append(f'{label}: non-release command failed: {command["argv"]}')
    expected_lengths = {'none': (3, 4, 4), 'build': (4, 5, 5),
                        'before': (4, 5, 5), 'after': (4, 5, 5),
                        'foreign': (5, 6, 6)}[boundary]
    if (len(releases), len(statuses), len(tag_commands)) != expected_lengths:
        errors.append(f'{label}: release/status/tag counts differ: '
                      f'{(len(releases), len(statuses), len(tag_commands))} != {expected_lengths}')
        return None
    expected_exits = ([0, 0, 0] if boundary == 'none' else
                      [1, 1, 1, 0, 0] if boundary == 'foreign' else
                      [1, 1, 0, 0])
    actual_success = [0 if command['exit'] == 0 else 1 for command in releases]
    if actual_success != expected_exits:
        errors.append(f'{label}: release exit pattern {actual_success} != {expected_exits}')
    try:
        plans = [candidate_plan(command['stdout'] + command['stderr']) for command in statuses]
    except Exception as exc:
        errors.append(f'{label}: cannot parse plans: {exc}')
        return None
    tags = [command['stdout'].splitlines() for command in tag_commands]
    initial = plans[0]
    if set(initial) != set('abcd'):
        errors.append(f'{label}: initial candidate set is {sorted(initial)}')
    base_tags = {f'{package}@1.0.0' for package in 'abcd'}
    if channel == 'beta':
        base_tags.update(f'{package}@1.0.1-beta.0' for package in 'abcd')
    if set(tags[0]) != base_tags:
        errors.append(f'{label}: baseline tags differ')
    completed = {package for package, version in initial.items()
                 if f'{package}@{version}' in tags[1]}
    residual = {package: version for package, version in initial.items() if package not in completed}
    if plans[1] != residual:
        errors.append(f'{label}: residual plan does not equal initial minus observed completion tags')
    if boundary == 'none':
        if residual or any(plans[index] for index in (2, 3)):
            errors.append(f'{label}: no-fault control retained work')
        if any(tags[index] != tags[1] for index in (2, 3)):
            errors.append(f'{label}: no-op changed tags')
    else:
        if target not in residual:
            errors.append(f'{label}: failed target missing from residual plan')
        if plans[2] != residual or tags[2] != tags[1]:
            errors.append(f'{label}: repeated failure changed plan or tags')
        repair_index = 4 if boundary == 'foreign' else 3
        if boundary == 'foreign' and (plans[3] != residual or tags[3] != tags[1]):
            errors.append(f'{label}: foreign conflict changed plan or tags')
        if plans[repair_index] or plans[repair_index + 1]:
            errors.append(f'{label}: repair or final no-op retained work')
        if tags[repair_index] != tags[repair_index + 1]:
            errors.append(f'{label}: final no-op changed tags')
    final_tags = set(tags[-1])
    for package, version in initial.items():
        if f'{package}@{version}' not in final_tags:
            errors.append(f'{label}: missing final completion tag for {package}')
    event_path = folder / 'work' / 'events.jsonl'
    if not event_path.is_file():
        errors.append(f'{label}: missing raw stage events')
        return None
    events = [json.loads(line) for line in event_path.read_text().splitlines()]
    writes = [event for event in events if event.get('event') == 'write']
    if Counter((event.get('package'), event.get('version')) for event in writes) != Counter(initial.items()):
        errors.append(f'{label}: artifact writes are not exactly one per initial obligation')
    injections = [event for event in events if event.get('event') == 'injected-failure']
    expected_stage = 'build' if boundary == 'build' else 'publish'
    expected_injections = 0 if boundary == 'none' else 2
    if len(injections) != expected_injections or any(
            event.get('package') != target or event.get('stage') != expected_stage
            for event in injections):
        errors.append(f'{label}: injected-failure events differ')
    matches = [event for event in events if event.get('event') == 'identity-match']
    if len(matches) != (2 if boundary in ('after', 'foreign') else 0):
        errors.append(f'{label}: identity-match count differs')
    conflicts = [event for event in events if event.get('event') == 'identity-conflict']
    if len(conflicts) != (1 if boundary == 'foreign' else 0):
        errors.append(f'{label}: identity-conflict count differs')
    registry = folder / 'work' / 'registry'
    artifacts = sorted(path for path in registry.glob('*/*') if path.is_file())
    if len(artifacts) != 4:
        errors.append(f'{label}: registry has {len(artifacts)} artifacts')
    for package, version in initial.items():
        artifact = registry / package / version
        try:
            payload = json.loads(artifact.read_bytes())
            source_hash = hashlib.sha256((folder / 'work' / package / 'content.txt').read_bytes()).hexdigest()
            if payload != {'package': package, 'version': version, 'source_sha256': source_hash}:
                errors.append(f'{label}: artifact identity differs for {package}')
        except Exception as exc:
            errors.append(f'{label}: invalid artifact for {package}: {exc}')
    observation = load(observation_path)
    if observation.get('status') != 'PASS':
        errors.append(f'{label}: executor observation is {observation.get("status")}')
    graph = GRAPHS[graph_name]
    origins = ('a', 'c') if graph_name == 'disconnected' else ('a',)
    mutant_lost = set()
    for origin in origins:
        if origin in completed:
            mutant_lost.update((descendants(graph, origin) - {origin}) & set(residual))
    if sorted(mutant_lost) != observation.get('source_mutant_lost'):
        errors.append(f'{label}: stored source-window counterfactual differs')
    return {'channel': channel, 'boundary': boundary, 'mutant_lost': len(mutant_lost),
            'mutant_losing': bool(mutant_lost)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f'refusing to overwrite {output}')
    errors = []
    identity = load(run / 'identity.json')
    cases = load(run / 'cases.json')
    expected = expected_cases(bool(identity.get('pilot')))
    if cases != expected:
        errors.append('cases.json differs from the complete deterministic matrix and order')
    rows = []
    for case in cases:
        try:
            row = check_case(run, case, errors)
            if row:
                rows.append(row)
        except Exception as exc:
            errors.append(f'{"-".join(case)}: verifier exception: {type(exc).__name__}: {exc}')
    derived_model, expected_records = expected_model_records()
    try:
        observed_records = stored_model_records(run / 'model-states.jsonl')
        if observed_records != expected_records:
            errors.append('model-states.jsonl differs from independent enumeration')
    except Exception as exc:
        errors.append(f'cannot verify model states: {exc}')
    summary = load(run / 'summary.json')
    expected_summary = {
        'status': 'PASS' if len(rows) == len(cases) and not errors else 'FAIL',
        'episodes': len(cases),
        'passed': len(rows),
        'fault_episodes': sum(case[3] in ('build', 'before', 'after') for case in cases),
        'controls': sum(case[3] == 'none' for case in cases),
        'foreign_cases': sum(case[3] == 'foreign' for case in cases),
        'source_mutant_losing_episodes': sum(row['mutant_losing'] for row in rows),
        'source_mutant_lost_obligations': sum(row['mutant_lost'] for row in rows),
        'model': derived_model,
    }
    if summary != expected_summary:
        errors.append('summary.json differs from independently derived aggregates')
    strata = {}
    for row in rows:
        key = f'{row["channel"]}/{row["boundary"]}'
        strata.setdefault(key, {'episodes': 0, 'mutant_losing_episodes': 0,
                                'mutant_lost_obligations': 0})
        strata[key]['episodes'] += 1
        strata[key]['mutant_losing_episodes'] += row['mutant_losing']
        strata[key]['mutant_lost_obligations'] += row['mutant_lost']
    result = {
        'status': 'PASS' if not errors else 'FAIL',
        'verified_utc': datetime.now(timezone.utc).isoformat(),
        'run': str(run),
        'episodes_checked': len(cases),
        'case_checks_completed': len(rows),
        'errors': errors,
        'strata': dict(sorted(strata.items())),
        'model': derived_model,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if not errors else 1)


if __name__ == '__main__':
    main()
