#!/usr/bin/env python3
# Per-cell timings of the Compute Engine runs, from the orchestrator's and the
# workers' JSON logs and the 20-second per-config timelines.
#
#   gce-timings.py gce-logs/
import glob
import json
import os
import sys
from datetime import datetime

root = sys.argv[1]


def parse(path):
    out = []
    for line in open(path, errors='replace'):
        line = line.strip()
        if not line.startswith('{'):
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def ts(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


cells = {}
for path in sorted(glob.glob(os.path.join(root, 'release*.log'))):
    run = os.path.basename(path)
    for e in parse(path):
        task = e.get('task', '')
        if not task.endswith(':build') or task.startswith('kernel'):
            continue
        cell = task[:-len(':build')]
        rec = cells.setdefault((run, cell), {'run': run, 'cell': cell})
        m = e.get('message')
        if m == 'task assigned':
            rec['assigned'] = ts(e['time']); rec['worker'] = e.get('worker')
        elif m == 'task finished':
            rec['finished'] = ts(e['time']); rec['status'] = e.get('status')

workers = {}
for path in sorted(glob.glob(os.path.join(root, 'w*/worker*.log'))):
    for e in parse(path):
        task = e.get('task', '')
        if not task.endswith(':build'):
            continue
        cell = task[:-len(':build')]
        rec = workers.setdefault((e.get('node'), cell, e.get('run')), {})
        m = e.get('message')
        if m == 'task claimed':
            rec['claimed'] = ts(e['time'])
        elif m == 'worktree added':
            rec['worktree'] = ts(e['time'])
        elif m in ('task finished', 'result pushed', 'coordination branch advanced'):
            rec.setdefault('done', ts(e['time']))

configs = {}
for path in sorted(glob.glob(os.path.join(root, 'w*/cell-timeline.log'))):
    node = os.path.basename(os.path.dirname(path))
    previous = None
    for line in open(path, errors='replace'):
        parts = line.split(' ', 2)
        if len(parts) < 3:
            continue
        when, _, rest = parts
        rest = rest.strip()
        if rest != previous:
            configs.setdefault(node, []).append((ts(when), rest))
            previous = rest

print('cell timings (orchestrator view)')
for key in sorted(cells):
    r = cells[key]
    a, f = r.get('assigned'), r.get('finished')
    dur = (f - a).total_seconds() / 60 if a and f else None
    print('  %-16s %-12s worker=%-3s status=%-9s assigned=%s finished=%s  %s' % (
        r['run'], r['cell'], r.get('worker'), r.get('status'),
        a.strftime('%H:%M:%S') if a else '-', f.strftime('%H:%M:%S') if f else '-',
        '%.1f min' % dur if dur is not None else 'unfinished'))
print()
print('worker view (claim -> worktree -> done)')
for key in sorted(workers, key=lambda k: (k[0] or '', k[1])):
    r = workers[key]
    c, w, d = r.get('claimed'), r.get('worktree'), r.get('done')
    print('  %-3s %-16s claimed=%s worktree=%s done=%s checkout=%s total=%s' % (
        key[0], key[1],
        c.strftime('%H:%M:%S') if c else '-', w.strftime('%H:%M:%S') if w else '-',
        d.strftime('%H:%M:%S') if d else '-',
        '%.0f s' % (w - c).total_seconds() if c and w else '-',
        '%.1f min' % ((d - c).total_seconds() / 60) if c and d else '-'))
print()
print('per-config timeline (first sighting, 20 s resolution)')
for node, rows in configs.items():
    for i, (when, what) in enumerate(rows):
        nxt = rows[i + 1][0] if i + 1 < len(rows) else None
        span = '%.1f min' % ((nxt - when).total_seconds() / 60) if nxt else 'until end'
        print('  %-3s %s %-60s %s' % (node, when.strftime('%H:%M:%S'), what[:60], span))
