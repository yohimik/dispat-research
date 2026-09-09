"""Execute unchanged CI entrypoints across package additions. Local publication only."""
import hashlib,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent
RESULTS=ROOT/'results';RESULTS.mkdir(exist_ok=False)

def run(args,cwd=None,check=True):
 p=subprocess.run(args,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
 if check and p.returncode:raise RuntimeError(str(args)+'\n'+p.stdout)
 return p

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

tasks=r'''import pathlib,json,os,sys,subprocess,shutil
r=pathlib.Path(os.environ['EXPERIMENT_ROOT']);p=pathlib.Path.cwd();name=os.environ['DISPAT_PACKAGE'];stage=sys.argv[1]
def event():
 with (r/'events.jsonl').open('a') as f:f.write(json.dumps({'package':name,'stage':stage,'version':os.environ.get('DISPAT_NEW_VERSION')})+'\n')
event()
if stage=='tests':
 if (r/('fail-'+name)).exists():raise RuntimeError('injected required test failure')
 if name=='tools':
  subprocess.run(['cc','main.c','-o','test-tool'],check=True)
  assert subprocess.check_output(['./test-tool'],text=True).strip()=='21'
 elif name=='schema':
  s=json.loads((p/'schema.json').read_text());assert s['type']=='object' and 'playerId' in s['required']
 else:
  s=json.loads((r/'schema/schema.json').read_text());sample=json.loads((p/'player.json').read_text())
  assert all(k in sample for k in s['required'])
elif stage=='build':
 (p/'built').mkdir(exist_ok=True)
 if name=='tools':subprocess.run(['cc','main.c','-o','built/game-tool'],check=True)
 elif name=='schema':
  s=json.loads((p/'schema.json').read_text());(p/'built/schema.json').write_text(json.dumps(s,sort_keys=True))
 else:
  assert (r/'schema/built/schema.json').exists()
  (p/'built/client.py').write_text("print('playerId')\n")
else:
 dest=r/'published'/name/os.environ['DISPAT_NEW_VERSION'];dest.parent.mkdir(parents=True,exist_ok=True)
 shutil.copytree(p/'built',dest)
'''
workflow='''#!/bin/sh
set -eu
python3 validate-gates.py
dispat run tests --since all
dispat
'''
validator='''import json
p=json.load(open('packages.json'))
assert p and all(v.get('scripts',{}).get('tests') for v in p.values()), 'required package test missing'
'''
checks=[]
def check(value,description):
 if not value:raise AssertionError(description)
 checks.append(description)

for rep in range(3):
 w=RESULTS/str(rep);w.mkdir();os.environ['EXPERIMENT_ROOT']=str(w)
 (w/'tasks.py').write_text(tasks);(w/'ci.sh').write_text(workflow);(w/'validate-gates.py').write_text(validator)
 (w/'tools').mkdir();(w/'tools/main.c').write_text('#include <stdio.h>\nint main(void){puts("21");return 0;}\n')
 def package(name):return {'path':name,'scripts':{'tests':'python3 "$EXPERIMENT_ROOT/tasks.py" tests'}}
 packages={'tools':package('tools')}
 global_cfg={'logFormat':'json','updateCheck':False,'concurrency':[3,3],'github':{'enabled':False},'changelog':{'enabled':False},'commit':{'enabled':True,'push':False,'name':'Experiment','email':'experiment@example.invalid'},'scripts':{'build':'python3 "$EXPERIMENT_ROOT/tasks.py" build','publish':'python3 "$EXPERIMENT_ROOT/tasks.py" publish'},'flow':{'build':'build','publish':'publish'},'packages':{'$ref':'./packages.json'}}
 (w/'global.json').write_text(json.dumps(global_cfg));(w/'dispat.json').write_text(json.dumps({'$ref':'./global.json','shell':['/bin/sh','-c']}))
 (w/'.gitignore').write_text('events.jsonl\n*.log\nfail-*\npublished/\n**/built/\n**/test-tool\n')
 def save(): (w/'packages.json').write_text(json.dumps(packages,indent=2))
 def commit(subject):run(['git','add','.'],w);run(['git','commit','--allow-empty','-qm',subject],w)
 save();run(['git','init','-q'],w);run(['git','config','user.name','Experiment'],w);run(['git','config','user.email','experiment@example.invalid'],w);commit('chore: seed')
 run(['git','tag','tools@1.0.0'],w)
 bare=RESULTS/(str(rep)+'-origin.git');run(['git','init','--bare','-q',str(bare)]);run(['git','remote','add','origin',str(bare)],w);run(['git','push','-q','origin','HEAD','--tags'],w)
 hashes={f:digest(w/f) for f in ['ci.sh','validate-gates.py','global.json','dispat.json']}
 snapshots=[]
 def pipeline(label,expected_exit=0,expected_tests=None):
  offset=len((w/'events.jsonl').read_text().splitlines()) if (w/'events.jsonl').exists() else 0
  p=run(['sh','ci.sh'],w,False);(w/(label+'.log')).write_text(p.stdout)
  check((p.returncode==0)==(expected_exit==0),f'{rep}/{label}: expected pipeline outcome')
  ev=[json.loads(x) for x in (w/'events.jsonl').read_text().splitlines()][offset:] if (w/'events.jsonl').exists() else []
  if expected_tests is not None:check({e['package'] for e in ev if e['stage']=='tests'}==set(expected_tests),f'{rep}/{label}: selected tests')
  check(all(digest(w/f)==v for f,v in hashes.items()),f'{rep}/{label}: entrypoint/common configuration unchanged')
  if expected_exit:check(not any(e['stage'] in ('build','publish') for e in ev),f'{rep}/{label}: failure prevents release stages')
  snapshots.append({'label':label,'exit':p.returncode,'events':ev,'packages':json.loads(json.dumps(packages)),'tags':run(['git','tag','--list'],w).stdout.splitlines()})
  return ev
 commit('feat(tools): add native asset validator')
 pipeline('baseline',expected_tests=['tools']);check((w/'published/tools/1.1.0/game-tool').exists(),f'{rep}: native binary published locally')
 run(['git','tag','schema@1.0.0'],w)
 (w/'schema').mkdir();(w/'schema/schema.json').write_text(json.dumps({'type':'object','required':['playerId']}));packages['schema']=package('schema');save();commit('feat(schema): add player format')
 pipeline('add-spec',expected_tests=['tools','schema']);check((w/'published/schema/1.1.0/schema.json').exists(),f'{rep}: specification artifact published locally')
 run(['git','tag','client@1.0.0'],w)
 (w/'client').mkdir();(w/'client/player.json').write_text(json.dumps({'playerId':'player-'+str(rep)}));packages['client']=package('client');packages['client']['dependencies']=['schema'];save();commit('feat(client): consume player format')
 pipeline('add-consumer',expected_tests=['tools','schema','client']);check((w/'published/client/1.1.0/client.py').exists(),f'{rep}: client artifact published locally')
 (w/'schema/schema.json').write_text(json.dumps({'type':'object','required':['playerId'],'description':'Player identity'}));commit('feat(schema)^^: describe player identity')
 before_tags=run(['git','tag','--list'],w).stdout
 (w/'fail-client').touch();pipeline('failed-test',1);check(run(['git','tag','--list'],w).stdout==before_tags,f'{rep}: failed gate writes no release tags');(w/'fail-client').unlink()
 missing=packages['client']['scripts'].pop('tests');save();pipeline('missing-test',1);packages['client']['scripts']['tests']=missing;save()
 pipeline('repair',expected_tests=['tools','schema','client'])
 tags=run(['git','tag','--list'],w).stdout
 check('schema@1.2.0' in tags and 'client@1.1.1' in tags,f'{rep}: specification propagation releases consumer')
 ev=pipeline('unchanged',expected_tests=['tools','schema','client']);check(not any(e['stage'] in ('build','publish') for e in ev),f'{rep}: unchanged run executes tests but no release stages')
 (RESULTS/(str(rep)+'-observations.json')).write_text(json.dumps({'snapshots':snapshots,'entrypoint_hashes':hashes},indent=2))
 print('integration repetition',rep,'PASS',flush=True)
(RESULTS/'verification.json').write_text(json.dumps({'status':'PASS','checks':checks,'assertions':len(checks),'repetitions':3},indent=2))
print('PASS',len(checks),'assertions',flush=True)
