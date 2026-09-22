import json
from pathlib import Path
import tempfile
import unittest

from compare import compare


class CompareTest(unittest.TestCase):
    def test_gate_requires_time_coverage_revision_and_toolchain(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'result.json'
            log = path.parent / 'cell.log'
            reference = dict(seconds=10, kernel_revision='abc', compiler='gcc 16',
                             assembler=None,
                             cases=['Building arm:defconfig ... passed'])
            result = dict(status='passed', revision='abc',
                          cases=[dict(line=reference['cases'][0], outcome='passed')])
            path.write_text(json.dumps(result))
            log.write_text('Compiler version: gcc 16\n')
            self.assertTrue(compare(reference, [path], 10)['accepted'])
            self.assertFalse(compare(reference, [path], 10.01)['accepted'])
            self.assertFalse(compare(reference, [path, path], 8)['accepted'])
            log.write_text('Compiler version: gcc 14\n')
            self.assertFalse(compare(reference, [path], 8)['accepted'])
            log.write_text('Compiler version: gcc 16\n')
            result['revision'] = 'different'
            path.write_text(json.dumps(result))
            self.assertFalse(compare(reference, [path], 8)['accepted'])

    def test_gate_requires_explicit_exact_toolchain_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'result.json'
            path.write_text(json.dumps(dict(
                status='passed', revision='abc',
                cases=[dict(line='Building hexagon:defconfig ... passed',
                            outcome='passed')])))
            log = path.parent / 'cell.log'
            log.write_text('Compiler version: clang 16\n')
            reference = dict(seconds=10, kernel_revision='abc', compiler='clang 16',
                             assembler=None,
                             cases=['Building hexagon:defconfig ... passed'])
            self.assertTrue(compare(reference, [path], 8)['accepted'])

            # Null means the reference emitted no assembler line; accepting an
            # unexpected line would no longer be exact toolchain parity.
            log.write_text('Compiler version: clang 16\nAssembler version: GNU as 2.44\n')
            self.assertFalse(compare(reference, [path], 8)['accepted'])
            log.write_text('Compiler version: clang 16\n')
            del reference['assembler']
            self.assertFalse(compare(reference, [path], 8)['accepted'])
            reference['assembler'] = ''
            self.assertFalse(compare(reference, [path], 8)['accepted'])


if __name__ == '__main__':
    unittest.main()
