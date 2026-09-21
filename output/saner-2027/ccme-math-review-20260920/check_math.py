"""Finite checks of CCME review arguments; no product execution or benchmark.

Run with Python 3; paths are relative to this file. Each result is a generated
case or analytic operation count, never an independent empirical sample.
"""
from collections import deque
from itertools import combinations
from pathlib import Path
import hashlib
import json


def reach(graph, sources, depth):
    seen = dict.fromkeys(sources, 0)
    queue = deque(sources)
    while queue:
        v = queue.popleft()
        if seen[v] == depth:
            continue
        for nxt in graph[v]:
            if nxt not in seen:
                seen[nxt] = seen[v] + 1
                queue.append(nxt)
    return {v: d for v, d in seen.items() if v not in sources}


def check_graphs(n=5):
    edges = list(combinations(range(n), 2))
    marker_cases = propagation_cases = 0
    for code in range(1 << len(edges)):
        children = [[] for _ in range(n)]
        parents = [[] for _ in range(n)]
        for bit, (a, b) in enumerate(edges):
            if code & (1 << bit):
                children[a].append(b)
                parents[b].append(a)
        for chosen in range(1 << n):
            sources = {v for v in range(n) if chosen & (1 << v)}
            masks = [chosen & (1 << v) for v in range(n)]
            for v in reversed(range(n)):
                for parent in parents[v]:
                    masks[parent] |= masks[v]
            for marker in sources:
                expected = set(reach(parents, {marker}, n)) | {marker}
                actual = {v for v in range(n) if masks[v] & (1 << marker)}
                assert actual == expected
            marker_cases += 1
            if not sources:
                continue
            single = {s: reach(children, {s}, n) for s in sources}
            for depth in range(n):
                merged = {}
                for walk in single.values():
                    for target, distance in walk.items():
                        if target not in sources and distance <= depth:
                            merged[target] = min(merged.get(target, n), distance)
                assert merged == reach(children, sources, depth)
                propagation_cases += 1
    return {"vertices": n, "ordered_dags": 1 << len(edges),
            "marker_configurations": marker_cases,
            "source_set_depth_configurations": propagation_cases}


def check_channel():
    base = "beta"
    candidates = ["beta", "stable"]  # newest first
    old_literal = candidates[0]
    proposals = [value for value in candidates if value != base]
    corrected = proposals[0] if proposals else None
    assert old_literal == "beta" and corrected == "stable"
    return {"baseline": base, "newest_first": candidates,
            "old_literal": old_literal, "corrected": corrected}


def check_counts():
    rows = []
    for size in (64, 128, 256, 512):
        # Package chain: one depth-one request at each source.
        chain = [[v + 1] if v + 1 < size else [] for v in range(size)]
        shallow = sum(len(reach(chain, {v}, 1)) for v in range(size))
        cached = sum(len(reach(chain, {v}, size)) for v in range(size))
        assert shallow == size - 1
        assert cached == size * (size - 1) // 2
        # History chain with every commit marked, including ancestor-or-self.
        transpose = size * (size + 1) // 2
        rows.append({"size": size, "depth_one_targets": shallow,
                     "unbounded_cache_targets": cached,
                     "dense_marker_word_ors_64": (size - 1) * ((size + 63) // 64),
                     "set_bits_enumerated_by_scalar_transpose": transpose})
    return rows


def check_no_marker():
    # One untagged package keeps every commit, but no boundaries/corrections/cancels.
    h = 10
    old_traversal_term = (h + h - 1) * 0
    new_traversal_term = (h + h - 1) * max(1, 0)
    assert old_traversal_term == 0 and new_traversal_term >= h
    return {"commits": h, "markers": 0, "old_traversal_term": old_traversal_term,
            "corrected_traversal_term": new_traversal_term,
            "note": "Window output is charged separately; this checks traversal overhead."}


if __name__ == "__main__":
    result = {"status": "PASS", "kind": "generated finite checks and analytic operation counts",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "graphs": check_graphs(), "channel_counterexample": check_channel(),
              "chain_counts": check_counts(), "zero_marker_case": check_no_marker(),
              "limits": "No released binary executed; no timing or allocation measurement; finite checks are not proofs for arbitrary graphs."}
    path = Path(__file__).with_name("math-checks.json")
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
