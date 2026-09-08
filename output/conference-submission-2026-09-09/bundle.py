from pathlib import Path
import hashlib,json,re,zipfile
out=Path('output/conference-submission-2026-09-09'); dst=out/'artifact-draft'; dst.mkdir(exist_ok=True)
base=Path('../dispat-experiments')
roots={ 'results-1.8.2':base/'results/v182-20260907', 'comparison-1.7.2':base/'results/v172/e5-1.7.2-hand', 'harness':base/'prepare-v182/harness' }
manifest=[]
for prefix,root in roots.items():
 for p in sorted(root.rglob('*')):
  if not p.is_file() or p.is_symlink() or any(x in p.parts for x in ['.git','__pycache__','.complete','.staging','provenance','images','finalize']): continue
  if p.suffix in ['.gz','.zip','.pyc','.png','.pdf'] or p.stat().st_size>2000000: continue
  try: txt=p.read_text()
  except UnicodeError: continue
  # Fail closed on credential-shaped values, keeping the report to filenames only.
  if re.search(r'(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}|AIza[A-Za-z0-9_-]{30,}|-----BEGIN .*PRIVATE KEY)',txt): raise RuntimeError('Credential-shaped content in '+str(p))
  txt=txt.replace('/Users/yohimik','/home/researcher').replace('/home/yohimik','/home/researcher').replace('yohimik@gmail.com','author@example.invalid').replace('github.com/yohimik','github.com/anonymous-author').replace('ghcr.io/yohimik','ghcr.io/anonymous-author').replace('yohimik/','anonymous-author/').replace('Semen Fediukovich','Anonymous Author')
  target=dst/prefix/p.relative_to(root); target.parent.mkdir(parents=True,exist_ok=True); target.write_text(txt)
  manifest.append({'file':str(target.relative_to(dst)), 'sha256':hashlib.sha256(target.read_bytes()).hexdigest(), 'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(dst/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
(dst/'README.md').write_text('''# Anonymous review artifact draft

This accompanies *Recoverable Releases Across Package Registries: A Git-Backed Saga Protocol*.

- `results-1.8.2/`: primary campaign records (core/full differential profiles, six specification vectors, orphan recovery, repository replay, eight timing cells, and three fault experiments).
- `comparison-1.7.2/`: preserved earlier release-tool fault records; competitor cells were not rerun on 1.8.2.
- `harness/`: experiment scripts prepared for the 1.8.2 campaign, including the restricted reference oracle. This oracle is not a full implementation of the paper's current model.
- `MANIFEST.json`: per-file hashes of the review copies and original inputs. Sanitization changes author-specific paths and repository identifiers, not measured values. Embedded original hash manifests describe originals and need not match sanitized files.

This is a non-executable artifact draft for review, not a complete archival replication release. Binaries, Git repositories, images, compressed dossiers, environment inventories and files larger than 2 MB are omitted. Author-identifying image/repository paths are placeholders. The full originals remain preserved locally; do not treat the review-copy hash list as a replacement for the campaign's original 753-artifact manifest. No new experiment was run to create this bundle. The primary campaign README documents refusal handling and coverage limitations. Complete archival provenance and executable setup are still required before an accepted-paper artifact evaluation.
''')
with zipfile.ZipFile(out/'artifact-draft.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(dst.rglob('*')):
  if p.is_file(): z.write(p,p.relative_to(dst))
print('Bundled',len(manifest),'review files;', (out/'artifact-draft.zip').stat().st_size,'bytes')
