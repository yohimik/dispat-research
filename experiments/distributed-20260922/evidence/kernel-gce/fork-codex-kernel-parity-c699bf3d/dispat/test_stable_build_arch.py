from pathlib import Path
import subprocess
import unittest


class ConfigSelectorTest(unittest.TestCase):
    script = Path(__file__).resolve().parent.parent / 'bin' / 'stable-build-arch.sh'

    def select(self, selector):
        command = (
            'source "$1"; select_configs "$2" defconfig allnoconfig tinyconfig || exit $?; '
            'printf "%s\\n" "${selected_configs[@]}"'
        )
        return subprocess.run(
            ['bash', '-c', command, 'selector-test', str(self.script), selector],
            capture_output=True, text=True)

    def test_single_and_group_preserve_original_order(self):
        single = self.select('tinyconfig')
        self.assertEqual(single.returncode, 0, single.stderr)
        self.assertEqual(single.stdout.splitlines(), ['tinyconfig'])

        grouped = self.select('tinyconfig,allnoconfig')
        self.assertEqual(grouped.returncode, 0, grouped.stderr)
        self.assertEqual(grouped.stdout.splitlines(), ['allnoconfig', 'tinyconfig'])

    def test_rejects_unknown_duplicate_and_empty_entries(self):
        for selector in ('missing', 'tinyconfig,tinyconfig', ',tinyconfig',
                         'tinyconfig,', 'tinyconfig,,defconfig',
                         'tinyconfig\nmissing', 'tinyconfig\rmissing'):
            with self.subTest(selector=selector):
                self.assertEqual(self.select(selector).returncode, 2)


if __name__ == '__main__':
    unittest.main()
