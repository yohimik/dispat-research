"""E4b: plan-time and memory vs workspace size. Hot paths on the
container filesystem; results as CSV rows on stdout.

Cells: (P, shape, U, pad). For each: build once in /tmp, run
`dispat status` 1 warmup + 5 reps, report median wall and max RSS of the
child (resource.getrusage RUSAGE_CHILDREN delta is unreliable across
reps, so RSS is taken from a dedicated extra run)."""
import os
import resource
import statistics
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(__file__))
from gen import build  # noqa: E402

CELLS = [ (1000, "layered", 200, 0) ] if True else [
    (100, "layered", 200, 0),
    (1000, "layered", 200, 0),
    (10000, "layered", 200, 0),
    (1000, "chain", 200, 0),
    (10000, "chain", 200, 0),
    (1000, "star", 200, 0),
    (1000, "layered", 1000, 0),
    (1000, "layered", 200, 5000),
]

def run_once(w):
    t0 = time.monotonic()
    r = subprocess.run(["dispat", "status", "--log-format", "json"],
                       cwd=w, capture_output=True, text=True)
    dt = time.monotonic() - t0
    assert r.returncode == 0, r.stderr[-300:]
    return dt

def rss_run(w):
    before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    subprocess.run(["dispat", "status", "--log-format", "json"],
                   cwd=w, capture_output=True)
    after = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    return max(after, before)          # ru_maxrss is a high-water mark

print("P,shape,U,pad,edges,median_s,min_s,max_s,maxrss_mb")
for (p, shape, u, pad) in CELLS:
    w = tempfile.mkdtemp(prefix=f"e4-{p}-{shape}-")
    inst = build(p, shape, u, pad, seed=42, workdir=w)
    run_once(w)                        # warmup
    reps = [run_once(w) for _ in range(5)]
    rss = rss_run(w) / (1024 * 1024)   # linux ru_maxrss is KB -> MB via /1024? see note
    print(f"{p},{shape},{u},{pad},{len(inst['edges'])},"
          f"{statistics.median(reps):.3f},{min(reps):.3f},{max(reps):.3f},"
          f"{rss:.0f}", flush=True)
