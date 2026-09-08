#!/usr/bin/env python3
"""Local-only release experiment. All publication targets bind to loopback."""
import json,os,pathlib,subprocess,sys,time,urllib.request,uuid,hashlib,shutil
ROOT=pathlib.Path(__file__).resolve().parent
BIN=pathlib.Path(shutil.which('dispat')).resolve()
RUN=ROOT/('run-'+time.strftime('%Y%m%d-%H%M%S'));RUN.mkdir()
containers=[];images=[]
def cmd(args,cwd=None,env=None,check=True,timeout=180):
 p=subprocess.run(args,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
 if check and p.returncode:raise RuntimeError(str(args)+'\n'+p.stdout[-4000:])
 return p

def serve(image,port,mount=None):
 name='saner-chain-'+uuid.uuid4().hex[:10]
 args=['docker','run','-d','--name',name,'-p',f'127.0.0.1::{port}']
 if mount:args+=['-v',mount]
 args+=[image];cmd(args);containers.append(name)
 bound=cmd(['docker','port',name,f'{port}/tcp']).stdout.strip().split(':')[-1]
 return '127.0.0.1:'+bound

def wait(url):
 deadline=time.monotonic()+30
 while True:
  try:urllib.request.urlopen(url,timeout=2).read();return
  except Exception:
   if time.monotonic()>deadline:raise
   time.sleep(.2)

stage=r'''import os,pathlib,json,time,subprocess,sys
root=pathlib.Path(os.environ['CHAIN_ROOT']);pkg=os.environ['DISPAT_PACKAGE'];stage=sys.argv[1]
version=os.environ['DISPAT_NEW_VERSION'];cfg=json.loads((root/'experiment.json').read_text())
started=time.monotonic_ns()
def run(args,cwd=None):subprocess.run(args,cwd=cwd,check=True)
def event(kind,code=0):
 data=json.dumps(dict(package=pkg,stage=stage,event=kind,monotonic_ns=time.monotonic_ns(),version=version,code=code))+'\n'
 fd=os.open(root/'events.jsonl',os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600);os.write(fd,data.encode());os.close(fd)
event('start');code=0
try:
 if pkg=='assets':
  if stage=='build':
   manifest=pathlib.Path('package.json');m=json.loads(manifest.read_text());m['version']=version;manifest.write_text(json.dumps(m))
   run(['npm','run','build'])
  else:
   time.sleep(3)
   run(['npm','publish','--ignore-scripts','--registry','http://'+cfg['npm']])
 else:
  image=cfg['docker']+'/'+cfg['namespace']+'/'+pkg+':'+version
  if stage=='build':
   if pkg=='base':
    run(['docker','build','--no-cache','-f',str(root/'base'/'Dockerfile'),'-t',image,str(root)])
   else:
    provider=os.environ['DISPAT_WORKSPACE_BASE_VERSION'];base=cfg['docker']+'/'+cfg['namespace']+'/base:'+provider
    # Explicit pull enforces registry availability even with a local daemon cache.
    run(['docker','pull',base])
    if (root/'fail-app').exists():raise RuntimeError('injected downstream build failure')
    run(['docker','build','--no-cache','--build-arg','BASE='+base,'-t',image,str(root/'app')])
  else:
   if pkg=='base':
    time.sleep(2)
    if (root/'fail-base').exists():raise RuntimeError('injected base publish refusal before docker push')
   run(['docker','push',image])
except Exception as e:
 print(str(e),file=sys.stderr);code=37
event('end',code);sys.exit(code)
'''
try:
 vconf=RUN/'verdaccio.yaml';vconf.write_text('storage: /verdaccio/storage\nauth:\n  htpasswd:\n    file: /verdaccio/storage/htpasswd\npackages:\n  "**":\n    access: $all\n    publish: $all\nuplinks: {}\nlisten: 0.0.0.0:4873\nlog: {type: stdout, level: warn}\n')
 npm=serve('verdaccio/verdaccio:6',4873,str(vconf)+':/verdaccio/conf/config.yaml:ro');reg=serve('registry:3',5000)
 wait('http://'+npm+'/-/ping');wait('http://'+reg+'/v2/')
 metadata={'date':time.strftime('%Y-%m-%d'),'binary':str(BIN),'binary_sha256':hashlib.sha256(BIN.read_bytes()).hexdigest(),'version':cmd([str(BIN),'--version']).stdout,'node':cmd(['node','--version']).stdout.strip(),'npm':cmd(['npm','--version']).stdout.strip(),'docker':cmd(['docker','version','--format','{{.Server.Version}}']).stdout.strip(),'description':'Local registry, actual npm build/publish and Docker build/push/pull; explicit app pull tests registry availability, not isolated Docker daemons; three-second npm publish and two-second base publish delays are controls, not performance measurements.'}
 (RUN/'metadata.json').write_text(json.dumps(metadata,indent=2))
 results=[]
 for rep in range(2):
  for case in ('mixed','serialized','missing-barrier','base-failure','app-failure'):
   p=RUN/(case+'-'+str(rep));p.mkdir();ns='chain'+uuid.uuid4().hex[:10]
   for pkg in ('assets','base','app'):(p/pkg).mkdir()
   (p/'assets'/'package.json').write_text(json.dumps({'name':ns+'-assets','version':'1.4.2','scripts':{'build':'node build.cjs'},'files':['dist']}))
   (p/'assets'/'build.cjs').write_text("require('fs').mkdirSync('dist',{recursive:true}); require('fs').writeFileSync('dist/theme.txt','release assets');")
   (p/'base'/'Dockerfile').write_text('FROM scratch\nCOPY assets/dist/theme.txt /theme.txt\n')
   (p/'app'/'Dockerfile').write_text('ARG BASE\nFROM ${BASE}\nCOPY app.txt /app.txt\n')
   (p/'app'/'app.txt').write_text('application layer\n')
   (p/'stage.py').write_text(stage)
   (p/'experiment.json').write_text(json.dumps({'npm':npm,'docker':reg,'namespace':ns}))
   (p/'test.npmrc').write_text('registry=http://'+npm+'\n//'+npm+'/:_authToken=experiment-only\n')
   (p/'.gitignore').write_text('events.jsonl\n*.log\nfail-*\n.npm-cache/\nassets/dist/\n')
   (p/'.dockerignore').write_text('.git\n.npm-cache\n*.log\n')
   cfg={'concurrency':[3,3],'logFormat':'json','updateCheck':False,'github':{'enabled':False},'changelog':{'enabled':False},'commit':{'enabled':True,'push':False,'name':'Review Experiment','email':'review@example.invalid'},'scripts':{'build':sys.executable+' '+str(p/'stage.py')+' build','publish':sys.executable+' '+str(p/'stage.py')+' publish'},'packages':{pkg:{'path':pkg,'isBuildWaitingPublish': (pkg=='base' and case!='missing-barrier') or (pkg=='assets' and case=='serialized'),'flow':{'build':'build','publish':'publish'}} for pkg in ('assets','base','app')},'dependencies':{'base':['assets'],'app':['base']}}
   (p/'dispat.json').write_text(json.dumps(cfg))
   cmd(['git','init','-q'],p);cmd(['git','config','user.name','Review Experiment'],p);cmd(['git','config','user.email','review@example.invalid'],p)
   cmd(['git','add','.'],p);cmd(['git','commit','-qm','chore: seed fixture'],p)
   for pkg,ver in [('assets','1.4.2'),('base','0.8.2'),('app','2.1.0')]:cmd(['git','tag',pkg+'@'+ver],p)
   (p/'assets'/'theme.txt').write_text('new theme\n');cmd(['git','add','.'],p);cmd(['git','commit','-qm','feat(assets)^^: add theme assets'],p)
   bare=RUN/(case+'-'+str(rep)+'-remote.git');cmd(['git','init','--bare','-q',str(bare)]);cmd(['git','remote','add','origin',str(bare)],p);cmd(['git','push','-q','origin','HEAD','--tags'],p)
   if case=='base-failure':(p/'fail-base').touch()
   if case=='app-failure':(p/'fail-app').touch()
   env=os.environ.copy();env.update(CHAIN_ROOT=str(p),NPM_CONFIG_USERCONFIG=str(p/'test.npmrc'),NPM_CONFIG_CACHE=str(p/'.npm-cache'))
   for name in list(env):
    if name.startswith(('GITHUB_','GH_TOKEN','NPM_TOKEN','NODE_AUTH_TOKEN')):env.pop(name)
   plan=cmd([str(BIN),'status'],p,env,check=False);(p/'plan.log').write_text(plan.stdout)
   rel=cmd([str(BIN)],p,env,check=False);(p/'release.log').write_text(rel.stdout)
   events=[json.loads(x) for x in (p/'events.jsonl').read_text().splitlines()] if (p/'events.jsonl').exists() else []
   tags1=cmd(['git','tag','--list'],p).stdout.splitlines()
   retries=[]
   if case in ('base-failure','app-failure'):
    for sentinel in p.glob('fail-*'):sentinel.unlink()
    retry=cmd([str(BIN)],p,env,check=False);(p/'retry.log').write_text(retry.stdout);retries.append(retry.returncode)
   final=cmd([str(BIN)],p,env,check=False) if case!='missing-barrier' else None
   if final:(p/'final.log').write_text(final.stdout)
   tags2=cmd(['git','tag','--list'],p).stdout.splitlines()
   result={'case':case,'rep':rep,'exit':rel.returncode,'retries':retries,'final_exit':final.returncode if final else None,'first_events':events,'first_tags':tags1,'final_tags':tags2,'namespace':ns}
   results.append(result);(RUN/'results.json').write_text(json.dumps(results,indent=2))
   for pkg,ver in [('base','0.8.3'),('app','2.1.1')]:images.append(reg+'/'+ns+'/'+pkg+':'+ver)
   print(case,rep,'exit',rel.returncode,'retries',retries,'events',len(events),flush=True)
   if not events:raise RuntimeError('no stages executed; inspect '+str(p/'release.log'))
 print('RESULTS',RUN,flush=True)
finally:
 for name in containers:cmd(['docker','rm','-f',name],check=False)
 if images:cmd(['docker','image','rm',*images],check=False)
 (RUN/'cleanup.json').write_text(json.dumps({'containers':containers,'removed':True,'images':images},indent=2))
