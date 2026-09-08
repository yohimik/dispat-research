#!/usr/bin/env python3
"""Check the built review PDF and its active TeX inputs. Requires Poppler."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def command(*args):
    return subprocess.check_output(args, text=True)

def require(condition, message):
    if not condition:
        raise SystemExit('FAIL: ' + message)

files = []
def expand(path):
    files.append(path)
    source = path.read_text()
    return re.sub(r'\\input\{([^}]+)\}', lambda m: expand(ROOT / (m[1] + '.tex')), source)

source = expand(ROOT / 'main.tex')
pdf = ROOT / 'build/main.pdf'
text = command('pdftotext', '-layout', str(pdf), '-')
pages = text.split('\f')
if not pages[-1].strip():
    pages.pop()
require(len(pages) == 12, 'exactly 12 pages')
require(re.search(r'^\s*R\s*EFERENCES\b', pages[10], re.M), 'references start on page 11')
require(not any(re.search(r'^\s*R\s*EFERENCES\b', p, re.M) for p in pages[:10]), 'ten content pages')
require('[31]' in pages[11] and '[40]' in pages[11], 'second reference page contains references 31–40')
require(not re.search(r'\b(?:TODO|FIXME|TBD|yohimik|dispat|CCME|Fediukovich)\b|\?\?', text, re.I), 'no placeholders or known identifying names')
require('\\documentclass[10pt,conference]{IEEEtran}' in source, 'IEEE 10pt conference format')
require('compsoc' not in source, 'no compsoc format')
keys = re.findall(r'\\bibitem\{([^}]+)\}', source)
cites = [k.strip() for group in re.findall(r'\\cite\{([^}]+)\}', source) for k in group.split(',')]
require(len(keys) == len(set(keys)), 'unique bibliography keys')
require(set(keys) == set(cites), 'all citations resolve and every reference is used')
require(list(dict.fromkeys(cites)) == keys, 'references ordered by first citation')
labels = re.findall(r'\\label\{([^}]+)\}', source)
refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', source)
require(len(labels) == len(set(labels)) and set(refs) <= set(labels), 'unique and resolved cross-references')
log = (ROOT / 'build/main.log').read_text()
require(not re.search(r'Overfull|Font Warning|Missing character|undefined references|multiply defined', log), 'no overflow, missing glyphs, font substitutions, or unresolved references')
info = command('pdfinfo', str(pdf))
require('612 x 792 pts (letter)' in info, 'US Letter paper')
require(not re.search(r'^Author:\s*\S', info, re.M), 'no PDF author metadata')
fonts = command('pdffonts', str(pdf)).splitlines()[2:]
require(all(re.search(r'\byes\s+yes\s+yes\s+\d+', line) for line in fonts), 'all fonts embedded with Unicode mappings')
result = {'status': 'PASS', 'pages': 12, 'content_pages': 10, 'reference_pages': 2,
          'references': len(keys), 'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
          'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
          'limits': 'Structural checks do not prove mathematics, anonymous eligibility, or empirical validity. Visually inspect after edits.'}
(ROOT / 'build/verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
