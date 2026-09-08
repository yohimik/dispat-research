#!/usr/bin/env python3
"""Verify the imported snapshot without interpreting experiment claims."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'provenance/migration.json').read_text())
errors=[]
for row in manifest['files']:
    path=ROOT/row['path']
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:
        errors.append(row['path'])
archive=ROOT/manifest['nested_git_archive']
if hashlib.sha256(archive.read_bytes()).hexdigest()!=manifest['nested_git_archive_sha256']:
    errors.append(manifest['nested_git_archive'])
if errors:
    raise SystemExit('Missing or changed imported files:\n'+'\n'.join(errors))
print(f"PASS: {len(manifest['files'])} imported files match the migration snapshot.")
