import json
import tempfile
import unittest
from pathlib import Path

import timing


def event(second, role, message, **fields):
    return {
        "time": f"2026-01-01T00:00:{second:02d}Z",
        "role": role,
        "message": message,
        **fields,
    }


def assignment(second, task, worker, branch):
    return event(second, "orchestrator", "task assigned", run="run-1",
                 task=task, worker=worker, branch=branch, attempt=1)


def worker_event(second, message, task, node, branch):
    return event(second, "worker", message, run="run-1", task=task,
                 node=node, branch=branch, attempt=1, status="succeeded")


def receipt(second, task, worker):
    return event(second, "orchestrator", "task finished", run="run-1",
                 task=task, worker=worker, status="succeeded")


class TimingTest(unittest.TestCase):
    def test_repeated_tasks_and_worker_queues_are_isolated(self):
        coordinator = [
            event(0, "orchestrator", "release started"),
            assignment(1, "same:build", "w1", "branch-1"),
            assignment(2, "other:build", "w2", "branch-2"),
            receipt(6, "other:build", "w2"),
            assignment(7, "next:build", "w2", "branch-3"),
            receipt(12, "same:build", "w1"),
            assignment(13, "same:build", "w1", "branch-4"),
            receipt(15, "next:build", "w2"),
            receipt(20, "same:build", "w1"),
            event(21, "orchestrator", "release finished"),
        ]
        workers = [
            worker_event(2, "task claimed", "same:build", "w1", "branch-1"),
            worker_event(10, "task finished", "same:build", "w1", "branch-1"),
            worker_event(3, "task claimed", "other:build", "w2", "branch-2"),
            worker_event(5, "task finished", "other:build", "w2", "branch-2"),
            worker_event(8, "task claimed", "next:build", "w2", "branch-3"),
            worker_event(14, "task finished", "next:build", "w2", "branch-3"),
            worker_event(14, "task claimed", "same:build", "w1", "branch-4"),
            worker_event(19, "task finished", "same:build", "w1", "branch-4"),
        ]

        report = timing.analyze(
            coordinator, workers,
            {"same": {"cell": "same", "seconds": 99, "script_seconds": 88}},
        )
        jobs = report["jobs"]

        self.assertEqual([job["assignment_to_claim_seconds"] for job in jobs],
                         [1, 1, 1, 1])
        self.assertEqual(
            [job["worker_completion_to_coordinator_result_seconds"] for job in jobs],
            [2, 1, 1, 1],
        )
        self.assertEqual([job["queue_gap_after_previous_result_seconds"] for job in jobs],
                         [None, None, 1, 1])
        self.assertEqual(jobs[0]["result_evidence"], "ambiguous-repeated-task")
        self.assertEqual(jobs[3]["result_evidence"], "ambiguous-repeated-task")
        self.assertIsNone(jobs[0]["build_script_seconds"])
        self.assertTrue(report["full_run_complete"])

    def test_duplicate_cell_results_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, seconds in (("first", 1), ("second", 2)):
                result_dir = root / name
                result_dir.mkdir()
                (result_dir / "result.json").write_text(json.dumps({
                    "cell": "build-alpha",
                    "seconds": seconds,
                    "script_seconds": seconds,
                }))

            with self.assertRaisesRegex(ValueError, "ambiguous result for cell"):
                timing.read_results([root])


if __name__ == "__main__":
    unittest.main()
