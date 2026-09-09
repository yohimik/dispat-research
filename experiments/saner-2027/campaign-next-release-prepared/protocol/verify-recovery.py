#!/usr/bin/env python3
"""Recheck retained recovery observations without rerunning the release CLI."""
import json
from pathlib import Path
r=Path(__file__).resolve().parent/'recovery'
rows=json.loads((r/'results.json').read_text())
assert len(rows)==20
assert {(x['requested_packages'],x['p_fail'],x['seed']) for x in rows}=={(n,p,s) for n in (20,100) for p in (.1,.3) for s in range(100,105)}
commands=0
for episode in rows:
    pending=set(episode['initial_versions'])
    assert len(pending)==episode['n']
    for run in episode['trace']:
        now=set(run['pending'])
        assert now<=pending and len(now)==run['remaining']
        assert len(pending)==run['planned']
        assert all(v==episode['initial_versions'][k] for k,v in run['versions'].items())
        assert set(run['versions'])==now
        pending=now
    assert not pending and episode['converged'] and episode['g_ok']
    assert episode['runs']==len(episode['trace'])
    if episode['progress_every_run']:
        assert all(x['remaining']<x['planned'] for x in episode['trace'])
        assert episode['runs']<=episode['n']
    traces=sorted((r/'traces'/f"n{episode['requested_packages']}-p{episode['p_fail']}-seed{episode['seed']}").glob('command-*.json'))
    assert traces, 'raw traces absent'
    data=[json.loads(f.read_text()) for f in traces]
    assert len([x for x in data if x['args'][:2]==['dispat','release']])==episode['runs']
    for x in data:
        assert isinstance(x['exit'],int) and isinstance(x['stdout'],str) and isinstance(x['stderr'],str)
    commands+=len(traces)
summary={'status':'PASS','episodes':len(rows),'maximum_runs':max(x['runs'] for x in rows),'progress_every_run':sum(x['progress_every_run'] for x in rows),'raw_command_records':commands,'scope':'retained observations; not a fresh execution or theorem proof'}
(r/'verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
