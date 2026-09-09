#!/usr/bin/env python3
"""Capture host, release, image, and command provenance before a measured run."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess


HERE = Path(__file__).resolve().parent


def command(argv):
    result = subprocess.run(argv, capture_output=True, text=True, timeout=120)
    return {'argv': argv, 'exit': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f'refusing to overwrite {output}')
    lock = json.loads((HERE / 'release-lock.json').read_text())
    checks = {
        'docker_version': command(['docker', 'version', '--format', '{{json .}}']),
        'runner_inspect': command(['docker', 'image', 'inspect', lock['runner_image']]),
        'source_inspect': command(['docker', 'image', 'inspect', lock['dispat_image']]),
        'github_releases': command(['gh', 'api', 'repos/yohimik/dispat/releases?per_page=100']),
        'research_git': command(['git', '-C', str(HERE.parents[2]), 'log', '-1',
                                 '--format=%H%n%cI%n%s']),
        'research_status': command(['git', '-C', str(HERE.parents[2]), 'status', '--short']),
        'host_os': command(['uname', '-a']),
        'macos': command(['sw_vers']),
    }
    failed = [name for name, result in checks.items() if result['exit'] != 0]
    if failed:
        raise SystemExit(f'provenance commands failed: {failed}')
    releases = json.loads(checks['github_releases']['stdout'])
    cli_releases = []
    for release in releases:
        match = re.fullmatch(r'services/dispat/v(\d+)\.(\d+)\.(\d+)', release['tag_name'])
        if match and not release['draft'] and not release['prerelease']:
            cli_releases.append((tuple(map(int, match.groups())), release))
    newest_version, newest = max(cli_releases)
    locked_version = tuple(map(int, lock['dispat_version'].split('.')))
    if newest_version != locked_version:
        raise SystemExit(f'locked CLI {locked_version} is not newest released CLI {newest_version}')
    runner = json.loads(checks['runner_inspect']['stdout'])[0]
    if runner['Id'] != lock['runner_image']:
        raise SystemExit('runner image ID differs from release lock')
    binary_probe = command([
        'docker', 'run', '--rm', '--network', 'none', '--cpus', '2', '--memory', '4g',
        '--platform', 'linux/arm64', lock['runner_image'], 'sh', '-c',
        "dispat --version; sha256sum $(command -v dispat); python3 --version; git --version; uname -a",
    ])
    if binary_probe['exit'] != 0 or lock['dispat_version_output'] not in binary_probe['stdout'] or \
            lock['dispat_binary_sha256'] not in binary_probe['stdout']:
        raise SystemExit('pinned runner binary identity probe failed')
    files = {}
    for name in ('PROTOCOL.md', 'execute.py', 'publisher.py', 'verify.py',
                 'provenance.py', 'archive.py', 'freeze.py', 'run.py',
                 'release-lock.json', 'FULL-FREEZE.json'):
        path = HERE / name
        files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    result = {
        'captured_utc': datetime.now(timezone.utc).isoformat(),
        'host_python': platform.python_version(),
        'host_platform': platform.platform(),
        'release_lock': lock,
        'newest_released_cli': {
            'tag': newest['tag_name'], 'published_at': newest['published_at'],
            'html_url': newest['html_url'], 'release_id': newest['id'],
        },
        'planned_execution': [
            'docker', 'run', '--rm', '--network', 'none', '--cpus', '2', '--memory', '4g',
            '--platform', 'linux/arm64', '-v', f'{HERE}:/campaign', '-w', '/campaign',
            lock['runner_image'], 'python3', 'execute.py', 'runs/full-01',
        ],
        'file_sha256': files,
        'binary_probe': binary_probe,
        'commands': checks,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'output': str(output), 'newest_released_cli': newest['tag_name'],
                      'runner_image': runner['Id']}, sort_keys=True))


if __name__ == '__main__':
    main()
