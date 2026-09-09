"""E4b: plan-time and memory vs workspace size. Hot paths on the
container filesystem; results as CSV rows on stdout.

Cells: (P, shape, U, pad). For each: build once in /tmp, run
`dispat status` 1 warmup + 5 reps, report median wall and max RSS of the
child (resource.getrusage RUSAGE_CHILDREN delta is unreliable across
reps, so RSS is taken from a dedicated extra run)."""
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(__file__))
from gen import build  # noqa: E402

CELLS = [
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
    assert r.returncode == 0, (f"exit={r.returncode} "
                               f"stdout={r.stdout[-300:]!r} "
                               f"stderr={r.stderr[-300:]!r}")
    return dt

def rss_run(w):
    # ru_maxrss is a process-lifetime high-water mark. Measure each cell in a
    # fresh Python parent so a preceding large cell cannot contaminate it.
    code = ("import resource,subprocess;"
            "subprocess.run(['dispat','status','--log-format','json'],"
            "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True);"
            "print(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss/1024)")
    r = subprocess.run([sys.executable, "-c", code], cwd=w,
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())

selected = CELLS
if len(sys.argv) > 1:
    indexes = [int(value) for value in sys.argv[1].split(",")]
    selected = [CELLS[index] for index in indexes]

print("P,shape,U,pad,edges,median_s,min_s,max_s,maxrss_mb")
for (p, shape, u, pad) in selected:
    w = tempfile.mkdtemp(prefix=f"e4-{p}-{shape}-")
    try:
        if pad >= 5000:
            os.environ["REALIZE_COMMIT_TREE"] = "1"
        inst = build(p, shape, u, pad, seed=42, workdir=w)
        valid = subprocess.run(["git", "fsck", "--full"], cwd=w,
                               capture_output=True, text=True)
        assert valid.returncode == 0, (f"invalid generated fixture: "
                                       f"{valid.stdout[-300:]} "
                                       f"{valid.stderr[-300:]}")
        run_once(w)                        # warmup
        reps = [run_once(w) for _ in range(5)]
        rss = rss_run(w)                   # Fresh child reports MiB.
        print(f"{p},{shape},{u},{pad},{len(inst['edges'])},"
              f"{statistics.median(reps):.3f},{min(reps):.3f},{max(reps):.3f},"
              f"{rss:.0f}", flush=True)
    except Exception:
        failure_root = os.environ.get("E4_FAILURE_DIR")
        if failure_root:
            dst = os.path.join(failure_root, f"{p}-{shape}-{u}-{pad}")
            shutil.copytree(w, dst, dirs_exist_ok=True)
        raise
    finally:
        shutil.rmtree(w, ignore_errors=True)
