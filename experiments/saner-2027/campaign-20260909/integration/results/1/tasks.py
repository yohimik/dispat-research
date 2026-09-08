import pathlib,json,os,sys,subprocess,shutil
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
