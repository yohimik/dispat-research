import subprocess,json,pathlib
r=pathlib.Path(__file__).resolve().parent
image=json.loads((r/'docker/runner-image.json').read_text())['Id']
base=['docker','run','--rm','--network','none','-e','GIT_CONFIG_COUNT=1','-e','GIT_CONFIG_KEY_0=init.defaultBranch','-e','GIT_CONFIG_VALUE_0=main','-e','GIT_AUTHOR_NAME=Experiment','-e','GIT_AUTHOR_EMAIL=experiment@example.invalid','-e','GIT_COMMITTER_NAME=Experiment','-e','GIT_COMMITTER_EMAIL=experiment@example.invalid','--cpus','2','--memory','4g','--tmpfs','/workspaces:rw,size=1g','-e','TMPDIR=/workspaces','-v',str(r/'harness')+':/exp:ro','-v',str(r)+':/results','-w','/exp',image]
def run(name,args):
 with (r/(name+'.log')).open('w') as log:p=subprocess.run(base+args,stdout=log,stderr=subprocess.STDOUT)
 print(name,p.returncode,flush=True)
 if p.returncode:raise SystemExit('Inspect '+name+'.log')
#run('binary-provenance',['sh','-c','dispat --version && sha256sum /usr/local/bin/dispat && python3 --version && node --version && npm --version && git --version && docker --version'])
#run('parser-gate',['sh','e1/gate0.sh'])
#run('golden-gate',['python3','e1/golden_test.py'])
#run('core-holdout',['python3','e1/run.py','--profile','core','--seed0','90001','--n','300','--workers','2','--out','/results/core'])
run('recovery-holdout',['python3','/results/recovery-holdout.py'])
# The mixed harness creates private sibling containers through the Docker socket.
base=['docker','run','--rm','--name','saner-canonical-mixed','--cpus','2','--memory','4g','-v','/var/run/docker.sock:/var/run/docker.sock','-v',str(r)+':'+str(r),'-w',str(r),image]
run('mixed-docker',['python3',str(r/'mixed-docker/run.py')])
