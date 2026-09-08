"""Frozen JSON-plan extraction (gate 0). Reads a dispat
`status --log-format json` stream on stdin, emits {pkg: row} JSON on stdout.

Event shape verified against dispat exp-342062d3:
  {"level":"info","package":"core","space":"packages","bump":"minor",
   "version":"1.0.0 -> 1.1.0","channel":"stable","reason":"direct",
   "ownCommits":1,"dueToProviders":[],"message":"● changed"}
"""
import json
import sys

def parse(stream):
    plan = {}
    for line in stream:
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = e.get("message", "")
        is_row = "package" in e and "version" in e and \
            (msg.endswith("changed") or "catch-up" in msg or "held" in msg
             or "channel-only" in msg)
        if is_row:
            ver = e.get("version", "")
            nxt = ver.split("->")[-1].strip() if "->" in ver else ver
            plan[e["package"]] = {
                "changed": "bump" in e and "held" not in msg,
                "next": nxt,
                "bump": e.get("bump", "none"),
                "channel": e.get("channel", "stable").split("->")[-1].strip(),
                "reason": e.get("reason", ""),
                "dueTo": e.get("dueToProviders", []) or [],
            }
    return plan

if __name__ == "__main__":
    print(json.dumps(parse(sys.stdin), indent=1, sort_keys=True))
