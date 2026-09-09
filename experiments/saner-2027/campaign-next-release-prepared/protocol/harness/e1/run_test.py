import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(__file__))
import run


class DispatPlanTest(unittest.TestCase):
    def test_nonzero_exit_is_rejected_before_parsing_valid_looking_output(self):
        result = subprocess.CompletedProcess(
            ["dispat", "status", "--log-format", "json"], 1,
            stdout='{"level":"info","package":"p","message":"unchanged"}\n',
            stderr="git failed\n")
        with mock.patch.object(run.subprocess, "run", return_value=result), \
             mock.patch.object(run.planjson, "parse") as parse:
            with self.assertRaises(run.DispatExecutionError) as raised:
                run.dispat_plan("/fixture")
        parse.assert_not_called()
        self.assertIs(raised.exception.result, result)

    def test_failure_dossier_preserves_raw_result_and_git_diagnostics(self):
        result = subprocess.CompletedProcess(
            ["dispat"], 1, stdout="raw stdout\n", stderr="raw stderr\n")
        fsck = subprocess.CompletedProcess(
            ["git", "fsck"], 2, stdout="", stderr="missing object\n")
        with tempfile.TemporaryDirectory() as root, \
             mock.patch.object(run.subprocess, "run", return_value=fsck):
            run.failure_dossier(root, 580, {"seed": 580}, root, result)
            dst = os.path.join(root, "seed580")
            with open(os.path.join(dst, "failure.json")) as f:
                failure = run.json.load(f)
            with open(os.path.join(dst, "stdout.log")) as f:
                self.assertEqual(f.read(), result.stdout)
            with open(os.path.join(dst, "stderr.log")) as f:
                self.assertEqual(f.read(), result.stderr)
        self.assertEqual(failure["returncode"], 1)
        self.assertEqual(failure["fixture_git_fsck"]["returncode"], 2)
        self.assertEqual(failure["fixture_git_fsck"]["stderr"],
                         "missing object\n")


if __name__ == "__main__":
    unittest.main()
