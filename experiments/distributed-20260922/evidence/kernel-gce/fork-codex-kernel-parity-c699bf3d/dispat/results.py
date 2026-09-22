#!/usr/bin/env python3
"""Read farm output using the classifications in master/shellcommands.py."""
import argparse
import json
import re
from pathlib import Path


def analyze(kind, lines, command_status):
    counts = dict(total=0, passed=0, failed=0, skipped=0,
                  kunit_passed=0, kunit_failed=0, kunit_skipped=0,
                  unrecognized=0, tracebacks=False)
    cases = []
    for line in lines:
        line = line.rstrip("\r\n")
        if line.startswith("Building "):
            if kind == "build":
                patterns = (
                    ("passed", r"Building (\S+):(\S+) \.\.\. passed$"),
                    ("failed", r"Building (\S+):(\S+) \.\.\. failed$"),
                    ("skipped", r"Building (\S+):(\S+) \.\.\. failed \(\S+\)"),
                )
            else:
                patterns = (
                    ("passed", r"Building (\S+):(\S+) \.+ running [\.R]+ passed$"),
                    ("failed", r"Building (\S+):(\S+) .*?failed.*$"),
                    ("skipped", r"Building (\S+):(\S+) \.+ skipped.*$"),
                )
            outcome = next((name for name, pattern in patterns
                            if re.match(pattern, line)), "unrecognized")
            counts["total"] += 1
            counts[outcome] += 1
            cases.append(dict(line=line, outcome=outcome))
        if kind == "qemu":
            if any(marker in line for marker in (
                    "[ cut here ]", "Call Trace:", "Call trace:",
                    "stack backtrace", "Kernel panic", "show_stack",
                    '(try booting with the "irqpoll" option)')):
                counts["tracebacks"] = True
            match = re.match(
                r"(?:\[ *\d+\.\d+\](?:\[ *T\d+\])? +)?"
                r"# Totals: pass:(\d+) fail:(\d+) skip:(\d+) total:\d+$", line)
            if match:
                for key, value in zip(("kunit_passed", "kunit_failed", "kunit_skipped"),
                                      match.groups()):
                    counts[key] += int(value)
    # A skipped-only or empty cell is not evidence of a successful build.
    valid = (command_status == 0 and counts["passed"] > 0
             and not any(counts[key] for key in
                         ("failed", "kunit_failed", "unrecognized", "tracebacks")))
    return dict(status="passed" if valid else "failed", command_status=command_status,
                counts=counts, cases=cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("build", "qemu"))
    parser.add_argument("log", type=Path)
    parser.add_argument("--command-status", type=int, required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--cell", required=True)
    parser.add_argument("--seconds", type=int, required=True)
    parser.add_argument("--script-seconds", type=int, required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--checkout-timings", type=Path)
    args = parser.parse_args()
    with args.log.open(errors="replace") as stream:
        result = analyze(args.kind, stream, args.command_status)
    result.update(ref=args.ref, revision=args.revision, cell=args.cell,
                  seconds=args.seconds, script_seconds=args.script_seconds)
    if args.checkout_timings:
        result['timings'] = json.loads(args.checkout_timings.read_text())
    args.json.write_text(json.dumps(result, indent=2) + "\n")
    if args.output:
        with args.output.open("a") as out:
            out.write("REF=" + args.ref + "\n")
            for name, key in (("TOTAL", "total"), ("PASS", "passed"),
                              ("FAIL", "failed"), ("SKIPPED", "skipped"),
                              ("KUNIT_PASS", "kunit_passed"),
                              ("KUNIT_FAIL", "kunit_failed"),
                              ("KUNIT_SKIPPED", "kunit_skipped")):
                out.write(f"{name}={result['counts'][key]}\n")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
