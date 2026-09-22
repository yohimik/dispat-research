#!/usr/bin/env python3
# Forecast of the full upstream matrix on Compute Engine workers, from the
# cells measured on GCE and Guenter's measured step times for the same cells.
#
#   forecast.py guenter-v7.3-rc4.json gce-cells.json
#
# gce-cells.json: {"build-alpha": {"seconds": N, "node": "w2", "overhead": M}, ...}
# where seconds is the cell's script time on the worker (claim to result minus
# overhead) and overhead the checkout plus kernel fetch before the script.
import heapq
import json
import sys

guenter = json.load(open(sys.argv[1]))
gce = json.load(open(sys.argv[2]))


def lpt(tasks, slots):
    heap = [0.0] * slots
    for t in sorted(tasks, reverse=True):
        x = heapq.heappop(heap)
        heapq.heappush(heap, x + t)
    return max(heap)


# 1. Speed ratio per measured cell: GCE seconds / Guenter seconds.
ratios = {}
for cell, m in gce.items():
    arch = cell.replace('build-', '')
    g = guenter['upstream-%s-master' % arch]['step']
    ratios[cell] = m['seconds'] / g
    print('%-14s guenter %5d s  gce %5d s (+%3d s overhead)  ratio %.2f' % (
        cell, g, m['seconds'], m['overhead'], ratios[cell]))
ratio = sum(ratios.values()) / len(ratios)
worst = max(ratios.values())
best = min(ratios.values())
overhead = sum(m['overhead'] for m in gce.values()) / len(gce)
print('mean ratio %.2f (range %.2f..%.2f), mean overhead %.0f s' % (ratio, best, worst, overhead))

# 2. The whole matrix: Guenter's 57 builders scaled by the ratio, plus overhead.
builds = {k: v for k, v in guenter.items() if k.startswith('upstream-')}
qemu = {k: v for k, v in guenter.items() if k.startswith('qemu-')}
print()
print('Guenter: %d build groups %.1f h, %d qemu groups %.1f h, 6 machines, 3h52 wall' % (
    len(builds), sum(v['step'] for v in builds.values()) / 3600,
    len(qemu), sum(v['step'] for v in qemu.values()) / 3600))
for label, r in (('optimistic', best), ('neutral', ratio), ('pessimistic', worst)):
    tasks = [v['step'] * r + overhead for v in builds.values()]
    qtasks = [v['step'] * r + overhead for v in qemu.values()]
    work = sum(tasks) / 3600
    print()
    print('%s (ratio %.2f): build groups only, %.1f machine-hours on this worker shape' % (label, r, work))
    for n in (2, 4, 6, 8, 12, 26):
        print('  %2d workers: %5.0f min wall, cost %.2f USD spot / %.2f USD on-demand' % (
            n, lpt(tasks, n) / 60,
            n * (lpt(tasks, n) / 3600) * 0.21, n * (lpt(tasks, n) / 3600) * 0.62))
    both = tasks + qtasks
    print('  builds + qemu boots (qemu scaled the same, untested): %.1f machine-hours' % (sum(both) / 3600))
    for n in (6, 12, 24, 57):
        print('  %2d workers: %5.0f min wall' % (n, lpt(both, n) / 60))
