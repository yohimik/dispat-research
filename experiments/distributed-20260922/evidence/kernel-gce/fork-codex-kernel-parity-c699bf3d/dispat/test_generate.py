import json
from pathlib import Path
import subprocess
import unittest

from generate import build_configs, BUILD_ARCHES


class SplitGeneratorTest(unittest.TestCase):
    def test_matrix_uses_every_original_configuration_once(self):
        generator = Path(__file__).with_name('generate.py')
        run = subprocess.run(['python3', str(generator), '--split-configs', '--jobs', '11',
                              '--qemu', '', '--no-write-cells'], check=True,
                             capture_output=True, text=True)
        envs = [json.loads(line.split('env: ', 1)[1])
                for line in run.stdout.splitlines() if line.startswith('    env: ')]
        actual = [(env['FARM_ARCH'], env['FARM_CONFIG']) for env in envs]
        expected = [(arch, config) for arch in BUILD_ARCHES for config in build_configs(arch)]
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), len(set(actual)))
        self.assertTrue(all(env['FARM_BUILD_JOBS'] == '11' for env in envs))
        self.assertIn(('powerpc', '85xx/tqm8548_defconfig'), actual)

    def test_grouped_configuration_still_matches_checked_in_file(self):
        generator = Path(__file__).with_name('generate.py')
        output = subprocess.check_output(['python3', str(generator), '--no-write-cells'], text=True)
        self.assertEqual(output, generator.parent.parent.joinpath('dispat.yaml').read_text())

    def test_bad_job_limit_is_rejected(self):
        run = subprocess.run(['python3', str(Path(__file__).with_name('generate.py')),
                              '--jobs', '0', '--no-write-cells'], capture_output=True)
        self.assertNotEqual(run.returncode, 0)

    def generate(self, *arguments):
        generator = Path(__file__).with_name('generate.py')
        return subprocess.run(['python3', str(generator), '--no-write-cells',
                               '--qemu', ''] + list(arguments),
                              capture_output=True, text=True)

    def test_placement_and_jobs_are_chosen_per_cell(self):
        run = self.generate('--arches', 'hexagon', '--split-configs', '--jobs', '6',
                            '--orchestrator', 'hexagon:defconfig', '--concurrency', '2',
                            '--cell-jobs', 'hexagon:defconfig=22',
                            '--env', 'DISPAT_FARM_SOURCE_POOL=/srv/farm/src')
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn('  concurrency: 2\n', run.stdout)
        packages = run.stdout.split('packages:\n', 1)[1].split('  build-')
        placed = {}
        for package in packages[1:]:
            name = package.split(':', 1)[0]
            env = json.loads(package.split('env: ', 1)[1].splitlines()[0])
            placed[name] = ('runOnly: orchestrator' in package, env)
        self.assertEqual(sorted(placed), ['hexagon-allnoconfig', 'hexagon-defconfig',
                                          'hexagon-tinyconfig'])
        self.assertTrue(placed['hexagon-defconfig'][0])
        self.assertFalse(placed['hexagon-tinyconfig'][0])
        self.assertEqual(placed['hexagon-defconfig'][1]['FARM_BUILD_JOBS'], '22')
        self.assertEqual(placed['hexagon-tinyconfig'][1]['FARM_BUILD_JOBS'], '6')
        self.assertTrue(all(env['DISPAT_FARM_SOURCE_POOL'] == '/srv/farm/src'
                            for _, env in placed.values()))

    def test_a_batch_becomes_one_package_in_the_original_order(self):
        run = self.generate('--arches', 'm68k_nommu', '--split-configs',
                            '--batch', 'm68k_nommu:m5307c3_defconfig+m5272c3_defconfig',
                            '--orchestrator',
                            'm68k_nommu:m5307c3_defconfig+m5272c3_defconfig')
        self.assertEqual(run.returncode, 0, run.stderr)
        names = [line.strip().rstrip(':')
                 for line in run.stdout.split('packages:\n', 1)[1].splitlines()
                 if line.startswith('  build-')]
        self.assertEqual(names, [
            'build-m68k_nommu-m5272c3_defconfig+m5307c3_defconfig',
            'build-m68k_nommu-m5249evb_defconfig',
            'build-m68k_nommu-m5407c3_defconfig',
            'build-m68k_nommu-m5475evb_defconfig',
        ])
        batched = run.stdout.split('  build-m68k_nommu-m5272c3_defconfig+')[1]
        env = json.loads(batched.split('env: ', 1)[1].splitlines()[0])
        self.assertEqual(env['FARM_CONFIG'], 'm5272c3_defconfig,m5307c3_defconfig')
        self.assertIn('    runOnly: orchestrator\n', batched)

    def test_a_batch_of_an_unknown_configuration_is_rejected(self):
        for entry in ('m68k_nommu:m5272c3_defconfig+nosuchconfig',
                      'm68k_nommu:m5272c3_defconfig'):
            with self.subTest(entry=entry):
                run = self.generate('--arches', 'm68k_nommu', '--split-configs',
                                    '--batch', entry)
                self.assertNotEqual(run.returncode, 0)

    def test_a_batch_needs_split_configs(self):
        run = self.generate('--arches', 'm68k_nommu',
                            '--batch', 'm68k_nommu:m5272c3_defconfig+m5307c3_defconfig')
        self.assertNotEqual(run.returncode, 0)

    def test_a_worker_cell_can_be_recorded_by_the_orchestrator(self):
        run = self.generate('--arches', 'hexagon', '--publish-on-orchestrator')
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn('\nrunOnly: [worker, orchestrator]\n', run.stdout)

    def test_one_node_alone_names_no_worker(self):
        run = self.generate('--arches', 'hexagon', '--split-configs', '--no-workers',
                            '--concurrency', '2', '--cell-jobs', 'hexagon:defconfig=24')
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn('\nrunOnly: orchestrator\n', run.stdout)
        self.assertNotIn('workers:', run.stdout)
        self.assertIn('  concurrency: 2\n', run.stdout)

    def test_a_selector_no_cell_matches_is_rejected(self):
        run = self.generate('--arches', 'hexagon', '--split-configs',
                            '--orchestrator', 'hexagon:nosuchconfig')
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('hexagon:nosuchconfig', run.stderr)

    def test_a_grouped_cell_is_selected_by_its_architecture(self):
        run = self.generate('--arches', 'hexagon', '--orchestrator', 'hexagon')
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn('    runOnly: orchestrator\n', run.stdout.split('  build-hexagon:')[1])


if __name__ == '__main__':
    unittest.main()
