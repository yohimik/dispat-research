#!/usr/bin/env python3
"""Fast configuration and artifact-integrity checks; no LLVM compilation or publication."""

import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("llvm_build", HERE / "build.py")
recipe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recipe)


def resolve(path):
    def visit(value, directory):
        if isinstance(value, list):
            return [visit(item, directory) for item in value]
        if not isinstance(value, dict):
            return value
        result = resolve(directory / value["$ref"]) if "$ref" in value else {}
        result.update({k: visit(v, directory) for k, v in value.items() if k != "$ref"})
        return result
    return visit(yaml.safe_load(path.read_text()), path.parent)


class ConfigurationTests(unittest.TestCase):
    def test_profiles_share_release_policy(self):
        local = resolve(ROOT / "dispat.yaml")
        remote = resolve(ROOT / "dispat.distributed.yaml")
        self.assertEqual(remote.pop("buildPlatforms"), ["linux/amd64"])
        nodes = remote.pop("execution")
        self.assertEqual(nodes["role"], "orchestrator")
        self.assertEqual(nodes["concurrency"], 1)
        self.assertEqual(local["concurrency"], [2, 1])
        for package in remote["packages"].values():
            self.assertTrue(package.pop("buildOutputs"))
        self.assertEqual(local, remote)
        for name in ("a", "b"):
            worker = resolve(HERE / "nodes" / f"worker-{name}.yaml")["execution"]
            self.assertEqual(worker["role"], "worker")
            self.assertEqual(worker["workers"], [])
            self.assertEqual(worker["transfer"], nodes["transfer"])
            self.assertEqual(worker["secretEnv"], nodes["secretEnv"])
            self.assertIn({"name": worker["name"], "endpoint": worker["endpoint"]}, nodes["workers"])

    def test_real_dispat_loads_and_plans_four_packages(self):
        binary = shutil.which(os.environ.get("DISPAT_BIN", "dispat"))
        self.assertIsNotNone(binary, "install dispat or set DISPAT_BIN")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("llvm", "clang", "lld"):
                (root / name).mkdir()
                (root / name / "source.txt").write_text(name)
            shutil.copy2(ROOT / "dispat.yaml", root)
            shutil.copytree(HERE / "packages", root / ".ci/dispat/packages")
            (root / ".ci/dispat/bundle").mkdir()
            def command(*args):
                result = subprocess.run(args, cwd=root, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result.stdout
            command("git", "init", "-b", "main")
            command("git", "add", ".")
            command("git", "-c", "user.name=Config Test", "-c", "user.email=test@example.invalid",
                    "commit", "-m", "feat(llvm): fixture SDK")
            command("git", "-c", "user.name=Config Test", "-c", "user.email=test@example.invalid",
                    "commit", "--allow-empty", "-m", "chore(llvm,clang,lld,toolchain): clear inherited pending metadata\n\nDeletes: *")
            command("git", "-c", "user.name=Config Test", "-c", "user.email=test@example.invalid",
                    "commit", "--allow-empty", "-m", "\n\n---\n\n".join(
                        f"release({name}): start fork toolchain releases\n\nRelease-As: 24.0.0-rc.0"
                        for name in ("llvm", "clang", "lld", "toolchain")))
            before = command("git", "status", "--porcelain")
            result = command(binary, "status", "--strict", "--require-release")
            for name in ("llvm", "clang", "lld", "toolchain"):
                self.assertIn(name, result)
            self.assertIn("24.0.0-rc.0", result)
            self.assertEqual(result.count("-> 24.0.0-rc.0"), 4)
            self.assertNotIn(" ERR ", result)
            self.assertEqual(command("git", "status", "--porcelain"), before)
            self.assertEqual(command("git", "tag", "--list"), "")

    def test_release_and_standalone_export_are_blocked(self):
        for arguments in (["release-ready"], ["export", "toolchain"]):
            result = subprocess.run([sys.executable, str(HERE / "build.py"), *arguments],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Distributed LLVM releases are blocked", result.stderr)

    def test_workflow_is_manual_for_releases_and_keeps_gate(self):
        workflow = yaml.load((ROOT / ".github/workflows/dispat.yml").read_text(), Loader=yaml.BaseLoader)
        self.assertEqual(set(workflow["on"]), {"pull_request", "workflow_dispatch"})
        self.assertEqual(workflow["concurrency"]["cancel-in-progress"], "false")
        self.assertEqual(workflow["jobs"]["release"]["needs"], "validate")
        gates = [s for s in workflow["jobs"]["validate"]["steps"]
                 if "build.py release-ready" in s.get("run", "")]
        self.assertEqual(len(gates), 1)
        self.assertIn("inputs.release", gates[0]["if"])


class OutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.root_patch = patch.object(recipe, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(self.root_patch.stop)
        self.identity = {"source": "a" * 40, "version": "24.0.0-rc.0", "platform": "linux/amd64",
                         "recipeSha256": "b" * 64, "targets": "X86", "compiler": "pinned compiler"}

    def provider(self, name="llvm"):
        folder = recipe.output(name)
        for required in ("lib/cmake/llvm/LLVMConfig.cmake", "bin/llvm-tblgen", "bin/FileCheck"):
            path = folder / "install" / required
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(required)
        receipt = {"package": name, "identity": self.identity,
                   "installSha256": recipe.fingerprint(folder / "install")}
        (folder / "build-info.json").write_text(json.dumps(receipt))
        return folder

    def test_absent_provider_is_not_rebuilt(self):
        with patch.object(recipe, "run") as run:
            with self.assertRaises(FileNotFoundError):
                recipe.configure("clang", self.identity)
            run.assert_not_called()

    def test_consumers_use_installed_sdk(self):
        self.provider()
        for name in ("clang", "lld"):
            with patch.object(recipe, "run") as run:
                recipe.configure(name, self.identity)
                arguments = [str(a) for a in run.call_args.args]
                self.assertIn(f"-DLLVM_DIR={recipe.output('llvm') / 'install/lib/cmake/llvm'}", arguments)
                self.assertEqual(arguments[arguments.index("-S") + 1], str(self.root / name))
                self.assertEqual(run.call_count, 1)

    def test_corrupt_and_wrong_version_provider_are_refused(self):
        folder = self.provider()
        recipe.verify_provider("llvm", self.identity)
        expected = copy.deepcopy(self.identity)
        expected["version"] = "24.0.1"
        with self.assertRaisesRegex(ValueError, "stale or incompatible"):
            recipe.verify_provider("llvm", expected)
        (folder / "install/bin/llvm-tblgen").write_text("modified")
        with self.assertRaisesRegex(ValueError, "integrity"):
            recipe.verify_provider("llvm", self.identity)

    def test_escaping_links_and_executable_mode_changes_are_refused(self):
        folder = self.provider()
        path = folder / "install/bin/llvm-tblgen"
        path.chmod(0o755)
        with self.assertRaisesRegex(ValueError, "integrity"):
            recipe.verify_provider("llvm", self.identity)
        (folder / "install/escape").symlink_to("../../../../outside")
        with self.assertRaisesRegex(ValueError, "nonrelocatable"):
            recipe.fingerprint(folder / "install")

    def test_bundle_rejects_conflicting_files(self):
        source = self.root / "source"
        destination = self.root / "destination"
        source.mkdir()
        destination.mkdir()
        (source / "tool").write_text("new")
        (destination / "tool").write_text("old")
        with self.assertRaisesRegex(ValueError, "conflicting"):
            recipe.merge_install(source, destination)

    def test_test_failure_prevents_install_and_receipt(self):
        calls = []
        def fail_check(*args, **kwargs):
            calls.append([str(a) for a in args])
            if "check-llvm" in args:
                raise subprocess.CalledProcessError(1, args)
        with patch.object(recipe, "run", side_effect=fail_check):
            with self.assertRaises(subprocess.CalledProcessError):
                recipe.build("llvm", self.identity)
        self.assertFalse(any("--install" in call for call in calls))
        self.assertFalse((recipe.output("llvm") / "build-info.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
