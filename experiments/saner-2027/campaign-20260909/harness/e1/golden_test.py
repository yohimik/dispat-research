"""Gate 1.2: cases lifted from the paper itself; oracle AND dispat must
both reproduce the paper's stated outcomes exactly."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
sys.path.insert(0, os.path.dirname(__file__))
import realize                     # noqa: E402
from run import dispat_plan        # noqa: E402
from oracle import Oracle          # noqa: E402

W = {"packages": ["core", "cli", "ui", "api"],
     "edges": [["cli", "core"], ["ui", "core"], ["api", "core"]],
     "tags": [{"pkg": "core", "version": "1.4.2", "commit": "c0"},
              {"pkg": "cli", "version": "2.0.0", "commit": "c0"},
              {"pkg": "ui", "version": "0.9.1", "commit": "c0"},
              {"pkg": "api", "version": "1.2.0", "commit": "c0"}]}

def inst(units, tags_extra=()):
    return {**W, "tags": W["tags"] + list(tags_extra), "head": "c1",
            "commits": [{"id": "c0", "units": []},
                        {"id": "c1", "units": units}],
            "features": {"prerelease": []}, "seed": 0, "profile": "golden"}

CASES = [
    # §2 motivating example / Table 3 run 1
    ("motivating", inst([{"type": "feat", "scope": ["core"], "pd": 1}]),
     {"core": ("1.5.0", "minor", "stable"), "cli": ("2.0.1", "patch", "stable"),
      "ui": ("0.9.2", "patch", "stable"), "api": ("1.2.1", "patch", "stable")}),
    # §6.3 channel pair, row 1: ^%beta releases core alone
    ("chan-suppress", inst([{"type": "feat", "scope": ["core"], "pd": 1,
                             "channel": "beta"}]),
     {"core": ("1.5.0-beta.0", "minor", "beta"), "cli": None,
      "ui": None, "api": None}),
    # §6.3 row 2: ^%beta++1 takes all four onto beta
    ("chan-carry", inst([{"type": "feat", "scope": ["core"], "pd": 1,
                          "channel": "beta", "pchannel": "beta", "pcd": 1}]),
     {"core": ("1.5.0-beta.0", "minor", "beta"),
      "cli": ("2.0.1-beta.0", "patch", "beta"),
      "ui": ("0.9.2-beta.0", "patch", "beta"),
      "api": ("1.2.1-beta.0", "patch", "beta")}),
    # Eq (7) counter-continue: same-core prerelease baseline advances
    ("train-continue",
     inst([{"type": "fix", "scope": ["core"], "pd": 0}],
          tags_extra=[{"pkg": "core", "version": "1.4.3-beta.1",
                       "commit": "c0"}]),
     {"core": ("1.4.3-beta.2", "patch", "beta"), "cli": None, "ui": None,
      "api": None}),
]

def cell(m, p):
    r = m.get(p, {})
    return (r["next"], r["bump"], r["channel"]) if r.get("changed") else None

fails = 0
for name, i, want in CASES:
    om = Oracle(i).plan()
    w = tempfile.mkdtemp(prefix="golden-")
    realize.realize(i, w)
    dm = dispat_plan(w)
    for p, exp in want.items():
        for who, m in (("oracle", om), ("dispat", dm)):
            got = cell(m, p)
            if got != exp:
                print(f"FAIL {name}/{p}/{who}: want {exp} got {got}")
                fails += 1
print("golden:", "PASS" if fails == 0 else f"{fails} failures")
sys.exit(1 if fails else 0)
