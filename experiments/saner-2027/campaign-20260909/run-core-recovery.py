import subprocess,json,pathlib,sys,hashlib
r=pathlib.Path(__file__).resolve().parent
image=json.loads((r/'images.json').read_text())['dispat-exp:v182-runtime']['Id']
base=['docker','run','--rm','--network','none','--cpus','2','--memory','4g','--tmpfs','/workspaces:rw,size=1g','-e','TMPDIR=/workspaces','-v',str(r/'harness')+':/exp:ro','-v',str(r)+':/results','-w','/exp',image]
def run(name,args):
 with (r/(name+'.log')).open('w') as log:
  p=subprocess.run(base+args,stdout=log,stderr=subprocess.STDOUT)
 print(name,p.returncode,flush=True)
 if p.returncode:raise SystemExit('Inspect '+name+'.log; no failed stage is skipped.')
run('binary-provenance',['sh','-c','dispat --version && sha256sum $(command -v dispat) && python3 --version && git --version'])
run('parser-gate',['sh','e1/gate0.sh'])
run('golden-gate',['python3','e1/golden_test.py'])
run('core-holdout',['python3','e1/run.py','--profile','core','--seed0','90001','--n','300','--workers','2','--out','/results/core'])
run('recovery-holdout',['python3','/results/recovery-holdout.py'])
