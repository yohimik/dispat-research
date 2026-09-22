#!/usr/bin/env python3
"""Run inside the pinned Docker image. Outputs are append-only per new run."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import random
import shutil
import subprocess
import traceback

HERE = Path(__file__).resolve().parent
GRAPHS = {
    'chain': {'a': [], 'b': ['a'], 'c': ['b'], 'd': ['c']},
    'diamond': {'a': [], 'b': ['a'], 'c': ['a'], 'd': ['b', 'c']},
    'fanout': {'a': [], 'b': ['a'], 'c': ['a'], 'd': ['a']},
    'disconnected': {'a': [], 'b': ['a'], 'c': [], 'd': ['c']},
    'shortcut': {'a': [], 'b': ['a'], 'c': ['a', 'b'], 'd': ['a', 'c']},
}


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def reach(graph, source):
    reached = {source}
    while True:
        new = reached | {p for p, deps in graph.items() if set(deps) & reached}
        if new == reached:
            return reached
        reached = new


def subsets(values):
    values = sorted(values)
    return (set(v) for n in range(len(values) + 1) for v in itertools.combinations(values, n))


def finite_model(out):
    vertices = list('abcd')
    edges = [(p, q) for i, p in enumerate(vertices) for q in vertices[:i]]
    states = transitions = mutants = progress = 0
    with (out / 'model-states.jsonl').open('x') as logs:
        for edge_set in subsets(range(len(edges))):
            graph = {p: [q for k, (v, q) in enumerate(edges) if k in edge_set and v == p] for p in vertices}
            for source in vertices:
                original = reach(graph, source)
                seen = {frozenset()}
                queue = [set()]
                while queue:
                    done = queue.pop()
                    pending = original - done
                    mutant = pending if source not in done else set()
                    lost = pending - mutant
                    states += 1
                    mutants += bool(lost)
                    state_transitions = 0
                    for failed in subsets(pending):
                        blocked = set().union(*(reach(graph, p) for p in failed)) if failed else set()
                        completed = pending - blocked
                        after = done | completed
                        residual = original - after
                        assert residual == pending - completed
                        assert residual <= pending and not residual & after
                        assert bool(completed) == (len(residual) < len(pending))
                        transitions += 1
                        state_transitions += 1
                        progress += bool(completed)
                        frozen = frozenset(after)
                        if frozen not in seen:
                            seen.add(frozen)
                            queue.append(after)
                    logs.write(json.dumps({'edges': [edges[i] for i in sorted(edge_set)],
                                           'source': source, 'completed': sorted(done),
                                           'pending': sorted(pending), 'source_mutant_lost': sorted(lost),
                                           'failure_subsets_checked': state_transitions}) + '\n')
    return {'graphs': 64, 'source_instances': 256, 'states': states,
            'transitions': transitions, 'progress_transitions': progress,
            'source_mutant_losing_states': mutants, 'projection_violations': 0}


def parse_plan(output):
    events = []
    for line in output.splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            pass
    summaries = [e for e in events if e.get('message') == 'release plan ready']
    assert len(summaries) == 1, output
    selected = {}
    for e in events:
        message = e.get('message', '')
        if ('package' in e and 'version' in e and 'bump' in e and
                'held' not in message and
                (message.endswith('changed') or 'catch-up' in message or 'channel-only' in message)):
            selected[e['package']] = e['version'].split('->')[-1].strip()
    assert len(selected) == summaries[0]['releasing'], output
    return selected


def episode(out, case):
    name = '-'.join(case)
    graph_name, channel, target, boundary = case
    graph = GRAPHS[graph_name]
    folder = out / name
    folder.mkdir()
    work = folder / 'work'
    work.mkdir()
    traces = folder / 'commands'
    traces.mkdir()
    sequence = 0
    environment = {**os.environ, 'FIXTURE_ROOT': str(work)}

    def command(argv, check=True, cwd=work):
        nonlocal sequence
        result = subprocess.run(argv, cwd=cwd, env=environment, capture_output=True, text=True, timeout=120)
        sequence += 1
        save(traces / f'{sequence:04}.json', {'argv': argv, 'cwd': str(cwd), 'exit': result.returncode,
                                            'stdout': result.stdout, 'stderr': result.stderr})
        if check and result.returncode:
            raise RuntimeError(f'{argv}: {result.stdout}\n{result.stderr}')
        return result

    def plan():
        result = command(['dispat', 'status', '--log-format', 'json'])
        return parse_plan(result.stdout + result.stderr)

    def tags():
        return command(['git', 'tag', '--list']).stdout.splitlines()

    def release():
        return command(['dispat', 'release', '--log-format', 'json'], False).returncode

    try:
        shutil.copyfile(HERE / 'publisher.py', work / 'publisher.py')
        packages = {}
        for p in graph:
            (work / p).mkdir()
            (work / p / 'content.txt').write_text('versioned fixture content for ' + p + '\n')
            packages[p] = {'path': p, 'dependencies': graph[p]}
        cfg = {'logFormat': 'json', 'updateCheck': False, 'concurrency': [1, 1],
               'github': {'enabled': False}, 'changelog': {'enabled': False},
               'commit': {'enabled': True, 'push': False, 'name': 'Experiment', 'email': 'experiment@example.invalid'},
               'scripts': {'build': 'python3 "$FIXTURE_ROOT/publisher.py" build',
                           'publish': 'python3 "$FIXTURE_ROOT/publisher.py" publish'},
               'flow': {'build': 'build', 'publish': 'publish'}, 'packages': packages}
        save(work / 'dispat.json', cfg)
        (work / '.gitignore').write_text('events.jsonl\nfault.json\nregistry/\n')
        command(['git', 'init', '-q', '-b', 'main'])
        command(['git', 'config', 'user.name', 'Experiment'])
        command(['git', 'config', 'user.email', 'experiment@example.invalid'])
        command(['git', 'add', '.'])
        command(['git', 'commit', '-qm', 'chore: baseline'])
        for p in graph:
            command(['git', 'tag', p + '@1.0.0'])
            if channel == 'beta':
                command(['git', 'tag', p + '@1.0.1-beta.0'])
        command(['git', 'init', '--bare', '-q', str(folder / 'origin.git')])
        command(['git', 'remote', 'add', 'origin', str(folder / 'origin.git')])
        command(['git', 'push', '-q', 'origin', 'main', '--tags'])
        origins = ['a', 'c'] if graph_name == 'disconnected' else ['a']
        for p in origins:
            (work / p / 'content.txt').write_text('new feature content for ' + p + '\n')
            command(['git', 'add', '.'])
            command(['git', 'commit', '-qm', f'feat({p})^^: evolve fixture'])
        initial = plan()
        assert set(initial) == set(graph), initial
        initial_tags = tags()
        fault_boundary = 'after' if boundary == 'foreign' else boundary
        if boundary != 'none':
            save(work / 'fault.json', {'package': target, 'boundary': fault_boundary})
        first_exit = release()
        after = plan()
        first_tags = tags()
        completed = {p for p, v in initial.items() if p + '@' + v in first_tags}
        expected = {p: v for p, v in initial.items() if p not in completed}
        assert after == expected, (after, expected)
        assert (first_exit == 0) == (boundary == 'none'), first_exit
        if boundary != 'none':
            assert target in after
            second_exit = release()
            assert second_exit != 0
            assert plan() == after and tags() == first_tags
            (work / 'fault.json').unlink()
        lost = set()
        for origin in origins:
            if origin in completed:
                lost |= (reach(graph, origin) - {origin}) & set(after)
        foreign_refused = None
        if boundary == 'foreign':
            artifact = work / 'registry' / target / initial[target]
            original_content = artifact.read_bytes()
            artifact.write_bytes(b'conflicting foreign artifact\n')
            foreign_refused = release() != 0 and plan() == after and tags() == first_tags
            assert foreign_refused
            artifact.write_bytes(original_content)
        assert release() == 0
        assert plan() == {}
        completed_tags = tags()
        assert all(p + '@' + v in completed_tags for p, v in initial.items())
        before_events = (work / 'events.jsonl').read_text()
        assert release() == 0 and plan() == {} and tags() == completed_tags
        assert (work / 'events.jsonl').read_text() == before_events
        events = [json.loads(line) for line in before_events.splitlines()]
        writes = [e for e in events if e['event'] == 'write']
        assert len(writes) == 4 and {e['package'] for e in writes} == set(graph), writes
        command(['git', 'fsck', '--no-dangling'])
        result = {'case': case, 'status': 'PASS', 'initial': initial, 'initial_tags': initial_tags,
                  'first_exit': first_exit, 'after_failure': after, 'first_tags': first_tags,
                  'completed_before_retry': sorted(completed), 'source_mutant_lost': sorted(lost),
                  'foreign_refused': foreign_refused, 'final_tags': completed_tags,
                  'artifact_writes': len(writes), 'stage_events': len(events)}
    except Exception as exc:
        result = {'case': case, 'status': 'FAIL', 'error': str(exc), 'traceback': traceback.format_exc()}
    save(folder / 'observation.json', result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    binary = Path(shutil.which('dispat'))
    identity = {'platform': platform.platform(), 'architecture': platform.machine(),
                'python': platform.python_version(), 'git': subprocess.check_output(['git', '--version'], text=True).strip(),
                'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
                'version': subprocess.check_output(['dispat', '--version'], text=True).strip(),
                'pilot': args.pilot}
    save(out / 'identity.json', identity)
    lock = json.loads((HERE / 'release-lock.json').read_text())
    assert identity['binary_sha256'] == lock['dispat_binary_sha256']
    cases = [(g, ch, p, b) for g in GRAPHS for ch in ('stable', 'beta')
             for p in 'abcd' for b in ('build', 'before', 'after')]
    cases += [(g, ch, 'd', b) for g in GRAPHS for ch in ('stable', 'beta') for b in ('none', 'foreign')]
    if args.pilot:
        cases = [('chain', ch, 'd', b) for ch in ('stable', 'beta') for b in ('none', 'build', 'before', 'after', 'foreign')]
    random.Random(20260910).shuffle(cases)
    save(out / 'cases.json', cases)
    rows = []
    for case in cases:
        row = episode(out, case)
        rows.append(row)
        print('-'.join(case), row['status'], row.get('error', ''), flush=True)
    model = finite_model(out)
    summary = {'status': 'PASS' if all(r['status'] == 'PASS' for r in rows) else 'FAIL',
               'episodes': len(rows), 'passed': sum(r['status'] == 'PASS' for r in rows),
               'fault_episodes': sum(r['case'][3] in ('build', 'before', 'after') for r in rows),
               'controls': sum(r['case'][3] == 'none' for r in rows),
               'foreign_cases': sum(r['case'][3] == 'foreign' for r in rows),
               'source_mutant_losing_episodes': sum(bool(r.get('source_mutant_lost')) for r in rows),
               'source_mutant_lost_obligations': sum(len(r.get('source_mutant_lost', [])) for r in rows),
               'model': model}
    save(out / 'summary.json', summary)
    print(json.dumps(summary), flush=True)
    raise SystemExit(0 if summary['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
