"""Result classification and the real cell wrapper, without cross toolchains."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor

from results import analyze


class ResultsTest(unittest.TestCase):
    def test_image_failure_overrides_zero_exit(self):
        result = analyze("build", ["Building arm:defconfig ... failed"], 0)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["counts"]["failed"], 1)

    def test_expected_skip_matches_buildbot(self):
        result = analyze("build", ["Building arm:defconfig ... passed",
                                  "Building arm:missing ... failed (config) - skipping"], 0)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["counts"]["failed"], 0)
        self.assertEqual(result["counts"]["skipped"], 1)

    def test_no_success_without_completed_tests(self):
        for lines in ([], ["Building arm:x ..."],
                      ["Building arm:x ... failed (script) - skipping"]):
            with self.subTest(lines=lines):
                self.assertEqual(analyze("build", lines, 0)["status"], "failed")

    def test_nonzero_exit_overrides_pass(self):
        self.assertEqual(analyze("build", ["Building arm:x ... passed"], 7)["status"], "failed")

    def test_qemu_and_kunit(self):
        lines = ["Building arm:virt:defconfig ... running ...R.. passed",
                 "Building arm:virt:missing ... skipped (unsupported)",
                 "[   1.50][ T12] # Totals: pass:12 fail:1 skip:2 total:15"]
        result = analyze("qemu", lines, 0)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["counts"]["passed"], 1)
        self.assertEqual(result["counts"]["skipped"], 1)
        self.assertEqual(result["counts"]["kunit_failed"], 1)

    def test_qemu_traceback(self):
        self.assertEqual(analyze("qemu", ["Building arm:virt:x ... running ... passed",
                                         "Kernel panic"], 0)["status"], "failed")

    def test_real_wrapper_retains_evidence_and_propagates_results(self):
        farm = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            def git(*args):
                subprocess.run(["git", "-C", str(source), *args], check=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            git("init", "-q")
            git("-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                "commit", "--allow-empty", "-qm", "fixture")
            git("-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                "tag", "-a", "v7.3-rc4", "-m", "fixture")
            scripts = root / "scripts"
            scripts.mkdir()
            script = scripts / "stable-build-arch.sh"
            env = dict(os.environ, DISPAT_PACKAGE="build-arm",
                       DISPAT_FARM_KERNEL_REPO=str(source),
                       DISPAT_FARM_LINUX=str(root / "cache.git"),
                       DISPAT_FARM_SCRIPTS=str(scripts),
                       DISPAT_FARM_RESULTS=str(root / "results"),
                       DISPAT_OUTPUT=str(root / "output"))
            for outcome, expected_status in (("failed", 1), ("passed", 0)):
                script.write_text("#!/bin/bash\necho 'Building arm:defconfig ... " + outcome + "'\nexit 0\n")
                script.chmod(0o755)
                run = subprocess.run(["bash", str(farm / "run-cell.sh")], env=env,
                                     capture_output=True, text=True)
                self.assertEqual(run.returncode, expected_status, run.stdout + run.stderr)
            reports = [json.loads(p.read_text()) for p in (root / "results").glob("*/result.json")]
            self.assertEqual(sorted(r["status"] for r in reports), ["failed", "passed"])
            self.assertEqual(len(list((root / "results").glob("*/cell.log"))), 2)
            self.assertIn("FAIL=1", (root / "output").read_text())

            # Two split cells share the cache but receive isolated kernel trees.
            script.write_text('#!/bin/bash\necho "Building $1:$3 ... passed"\n')
            def split(config):
                split_env = dict(env, DISPAT_PACKAGE='build-arm-' + config,
                                 FARM_ARCH='arm', FARM_CONFIG=config,
                                 DISPAT_FARM_LINUX=str(root / 'cold-shared-cache.git'),
                                 DISPAT_OUTPUT=str(root / ('output-' + config)))
                return subprocess.run(['bash', str(farm / 'run-cell.sh')], env=split_env,
                                      capture_output=True, text=True)
            with ThreadPoolExecutor(2) as pool:
                for run in pool.map(split, ['defconfig', 'allmodconfig']):
                    self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            reports = [json.loads(p.read_text()) for p in (root / 'results').glob('*/result.json')]
            actual = {r['cell']: r['cases'][0]['line'] for r in reports}
            self.assertEqual(actual['build-arm-defconfig'], 'Building arm:defconfig ... passed')
            self.assertEqual(actual['build-arm-allmodconfig'], 'Building arm:allmodconfig ... passed')


if __name__ == "__main__":
    unittest.main()
