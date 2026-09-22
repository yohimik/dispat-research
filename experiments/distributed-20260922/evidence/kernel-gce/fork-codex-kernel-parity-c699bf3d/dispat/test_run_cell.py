"""The source-tree pool a cell leases instead of creating a kernel worktree.

The lease holds an advisory lock for the cell's whole life, so these cases run
where that lock exists: a worker node, never the operator's macOS host.
"""
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

FARM = Path(__file__).resolve().parent.parent
REF = dict(line.split('=', 1) for line in
           (FARM / 'dispat' / 'kernel' / 'ref.env').read_text().splitlines()
           if '=' in line and not line.startswith('#'))['KERNEL_REF']


@unittest.skipUnless(sys.platform.startswith('linux') and shutil.which('flock'),
                     'the lease needs the flock advisory lock of a worker node')
class SourcePoolTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.pool = self.root / 'src'
        self.pool.mkdir()
        self.scripts = self.root / 'scripts'
        self.scripts.mkdir()
        # A stand-in for the farm's build script: it writes the tree it ran in
        # and the pass line master/shellcommands.py counts.
        script = self.scripts / 'stable-build-arch.sh'
        script.write_text('#!/bin/bash\n'
                          'printf "%s\\n" "$PWD" >> "${POOL_TEST_RAN_IN}"\n'
                          'echo "Compiler version: stand-in"\n'
                          'echo "Building $1:defconfig ... passed"\n')
        script.chmod(0o755)
        self.ran_in = self.root / 'ran-in'

    def tree(self, name, tag=REF):
        tree = self.pool / name
        tree.mkdir()
        (tree / 'Makefile').write_text('# stand-in kernel\n')
        git = ['git', '-C', str(tree)]
        subprocess.run(git + ['init', '-q'], check=True)
        subprocess.run(git + ['config', 'user.email', 'pool@dispat.invalid'], check=True)
        subprocess.run(git + ['config', 'user.name', 'pool'], check=True)
        subprocess.run(git + ['add', 'Makefile'], check=True)
        subprocess.run(git + ['commit', '-q', '-m', 'chore: stand-in tree'], check=True)
        # Annotated, as the kernel's own release tags are: `git describe` reads
        # no other kind, and the farm script names a build with it.
        subprocess.run(git + ['tag', '-a', '-m', 'stand-in release', tag], check=True)
        return tree

    def cell(self):
        environment = dict(os.environ,
                           DISPAT_PACKAGE='build-alpha',
                           DISPAT_FARM_SOURCE_POOL=str(self.pool),
                           DISPAT_FARM_RESULTS=str(self.root / 'results'),
                           DISPAT_FARM_SCRIPTS=str(self.scripts),
                           POOL_TEST_RAN_IN=str(self.ran_in),
                           TMPDIR=str(self.root))
        return subprocess.run([str(FARM / 'dispat' / 'run-cell.sh')],
                              capture_output=True, text=True, env=environment)

    def results(self):
        return sorted((self.root / 'results').glob('*/result.json'))

    def test_a_cell_leases_a_prepared_tree_and_records_the_lease(self):
        tree = self.tree('slot0')
        run = self.cell()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(self.ran_in.read_text().splitlines(), [str(tree)])
        result = json.loads(self.results()[0].read_text())
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['counts']['passed'], 1)
        self.assertEqual(result['timings']['source'], str(tree))
        self.assertIn('source_lease_seconds', result['timings'])
        self.assertNotIn('kernel_checkout_seconds', result['timings'])

    def test_a_held_tree_is_left_to_its_cell(self):
        self.tree('slot0')
        free = self.tree('slot1')
        with open(str(self.pool / 'slot0.lock'), 'a') as held:
            fcntl.flock(held, fcntl.LOCK_EX)
            run = self.cell()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(self.ran_in.read_text().splitlines(), [str(free)])

    def test_a_full_pool_refuses_the_cell(self):
        self.tree('slot0')
        with open(str(self.pool / 'slot0.lock'), 'a') as held:
            fcntl.flock(held, fcntl.LOCK_EX)
            run = self.cell()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('no free source tree', run.stderr)

    def test_another_revision_refuses_the_cell(self):
        self.tree('slot0', tag='v0.0-stand-in')
        run = self.cell()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn(REF, run.stderr)
        self.assertFalse(self.ran_in.exists())

    def test_a_modified_tree_refuses_the_cell(self):
        tree = self.tree('slot0')
        (tree / 'Makefile').write_text('# edited\n')
        run = self.cell()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('modified tracked files', run.stderr)
        self.assertFalse(self.ran_in.exists())


if __name__ == '__main__':
    unittest.main()
