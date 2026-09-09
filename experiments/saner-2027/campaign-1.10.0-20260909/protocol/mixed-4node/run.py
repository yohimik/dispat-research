#!/usr/bin/env python3
"""Four-node npm -> npm -> Docker -> Docker extension using local registries."""
import json,os,pathlib,subprocess,sys,time,urllib.request,uuid,hashlib,shutil,random
if sys.version_info < (3, 12):
 raise SystemExit('Use Python 3.12+: cross-process monotonic timestamps are required.')
ROOT=pathlib.Path(__file__).resolve().parent
binary=os.environ.get('DISPAT_BIN') or shutil.which('dispat')
if not binary:raise SystemExit('Set DISPAT_BIN to the released Dispat binary.')
BIN=pathlib.Path(binary).resolve()
expected_version=os.environ.get('DISPAT_EXPECTED_VERSION')
expected_version_output=os.environ.get('DISPAT_EXPECTED_VERSION_OUTPUT')
expected_sha256=os.environ.get('DISPAT_EXPECTED_SHA256')
if not expected_version or not expected_version_output or not expected_sha256:
 raise SystemExit('DISPAT_EXPECTED_VERSION, DISPAT_EXPECTED_VERSION_OUTPUT and DISPAT_EXPECTED_SHA256 are required.')
actual_version=subprocess.check_output([str(BIN),'--version'],text=True)
if actual_version.strip().splitlines()[-1] != expected_version_output:
 raise SystemExit('Expected Dispat '+expected_version+', observed '+actual_version.strip())
actual_sha256=hashlib.sha256(BIN.read_bytes()).hexdigest()
if actual_sha256 != expected_sha256:
 raise SystemExit('Dispat binary SHA-256 mismatch: '+actual_sha256)
RUN=ROOT/('run-'+time.strftime('%Y%m%d-%H%M%S'));RUN.mkdir()
containers=[];images=[];net=None;builder=None
def cmd(args,cwd=None,env=None,check=True,timeout=180):
 p=subprocess.run(args,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
 if check and p.returncode:raise RuntimeError(str(args)+'\n'+p.stdout[-4000:])
 return p

def serve(image,port,mount=None):
 name='saner-chain-'+uuid.uuid4().hex[:10]
 args=['docker','run','-d','--name',name,'--network',net]
 if mount:args+=['-v',mount]
 args+=[image];cmd(args);containers.append(name)
 return name+':'+str(port)

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
 data=json.dumps(dict(package=pkg,stage=stage,event=kind,monotonic_ns=time.monotonic_ns(),wall_ns=time.time_ns(),version=version,code=code))+'\n'
 fd=os.open(root/'events.jsonl',os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600);os.write(fd,data.encode());os.close(fd)
event('start');code=0
try:
 if pkg in ('assets','ui'):
  if stage=='build':
   manifest=pathlib.Path('package.json');m=json.loads(manifest.read_text());m['version']=version;manifest.write_text(json.dumps(m))
   run(['npm','run','build'])
  else:
   time.sleep(3)
   run(['npm','publish','--ignore-scripts','--registry','http://'+cfg['npm']])
 else:
  image=cfg['docker']+'/'+cfg['namespace']+'/'+pkg+':'+version
  args=['docker','buildx','build','--builder',cfg['builder'],'--progress','plain','--provenance=false','-t',image]
  if pkg=='base':args+=['-f',str(root/'base'/'Dockerfile'),str(root)]
  else:
   provider=os.environ['DISPAT_WORKSPACE_BASE_VERSION'];base=cfg['docker']+'/'+cfg['namespace']+'/base:'+provider
   args+=['--build-arg','BASE='+base,str(root/'app')]
  if stage=='build':
   if pkg=='app' and (root/'fail-app').exists():raise RuntimeError('injected downstream build failure')
   args[3:3]=['--output','type=oci,dest='+str(root/(pkg+'.oci.tar'))]
  else:
   if pkg=='base':
    time.sleep(2)
    if (root/'fail-base').exists():raise RuntimeError('injected base publish refusal before registry push')
   args[3:3]=['--push']
  run(args)
except Exception as e:
 print(str(e),file=sys.stderr);code=37
event('end',code);sys.exit(code)
'''
try:
 net='saner-net-'+uuid.uuid4().hex[:8];cmd(['docker','network','create','--internal',net])
 cmd(['docker','network','connect',net,os.environ['HOSTNAME']])
 vconf=RUN/'verdaccio.yaml';vconf.write_text('storage: /verdaccio/storage\nauth:\n  htpasswd:\n    file: /verdaccio/storage/htpasswd\npackages:\n  "**":\n    access: $all\n    publish: $all\nuplinks: {}\nlisten: 0.0.0.0:4873\nlog: {type: stdout, level: warn}\n')
 npm=serve('verdaccio/verdaccio@sha256:fcb86134563534e2f634752e6c6c3edcdb78242ec16578c73ce39d1dadbaa801',4873,str(vconf)+':/verdaccio/conf/config.yaml:ro');regname='saner-reg-'+uuid.uuid4().hex[:8]
 cmd(['docker','run','-d','--name',regname,'--network',net,'registry@sha256:1be55279f18a2fe1a74edf2664cac61c1bea305b7b4642dab412e7affdcb3e33']);containers.append(regname)
 reg=regname+':5000'
 builder='saner-builder-'+uuid.uuid4().hex[:8]
 bk=RUN/'buildkit.toml';bk.write_text('[registry."'+reg+'"]\n  http = true\n')
 cmd(['docker','buildx','create','--name',builder,'--driver','docker-container','--driver-opt','network='+net,'--driver-opt','image=moby/buildkit@sha256:28a898719c18a33f4e8000685287fa36fd0dd9560c6440227d3a732d79bb41d8','--buildkitd-config',str(bk)])
 cmd(['docker','buildx','inspect',builder,'--bootstrap'],timeout=240)
 wait('http://'+npm+'/-/ping')
 metadata={'python':sys.version,'date':time.strftime('%Y-%m-%d'),'binary':str(BIN),'binary_sha256':hashlib.sha256(BIN.read_bytes()).hexdigest(),'version':cmd([str(BIN),'--version']).stdout,'node':cmd(['node','--version']).stdout.strip(),'npm':cmd(['npm','--version']).stdout.strip(),'docker':cmd(['docker','version','--format','{{.Server.Version}}']).stdout.strip(),'description':'Separate four-node extension: assets npm local output feeds ui npm; ui local output feeds the base image; app uses FROM the published base. Private registries and separate OCI output prevent public publication and a local Docker-daemon FROM shortcut. Three-second npm and two-second base publication delays expose overlap and are not performance measurements.'}
 metadata['images']=[{k:i.get(k) for k in ('Id','RepoTags','RepoDigests')} for i in json.loads(cmd(['docker','image','inspect','registry@sha256:1be55279f18a2fe1a74edf2664cac61c1bea305b7b4642dab412e7affdcb3e33','verdaccio/verdaccio@sha256:fcb86134563534e2f634752e6c6c3edcdb78242ec16578c73ce39d1dadbaa801','moby/buildkit@sha256:28a898719c18a33f4e8000685287fa36fd0dd9560c6440227d3a732d79bb41d8']).stdout)]
 metadata['buildx']=cmd(['docker','buildx','version']).stdout.strip()
 (RUN/'metadata.json').write_text(json.dumps(metadata,indent=2))
 shutil.copy2(__file__,RUN/'harness-at-run.py')
 results=[]
 cases=['mixed','serialized','missing-barrier','base-failure','app-failure']
 order=[(rep,case) for rep in range(6) for case in cases];random.Random(20260909).shuffle(order)
 (RUN/'schedule.json').write_text(json.dumps({'seed':20260909,'order':order},indent=2))
 for rep,case in order:
  if True:
   p=RUN/(case+'-'+str(rep));p.mkdir();ns='chain'+uuid.uuid4().hex[:10]
   for pkg in ('assets','ui','base','app'):(p/pkg).mkdir()
   (p/'assets'/'package.json').write_text(json.dumps({'name':ns+'-assets','version':'1.4.2','scripts':{'build':'node build.cjs'},'files':['dist']}))
   (p/'assets'/'build.cjs').write_text("const f=require('fs'); f.mkdirSync('dist',{recursive:true}); f.copyFileSync('theme.txt','dist/theme.txt');")
   (p/'assets'/'theme.txt').write_text('original theme\n')
   (p/'ui'/'package.json').write_text(json.dumps({'name':ns+'-ui','version':'3.2.0','dependencies':{ns+'-assets':'^1.4.2'},'scripts':{'build':'node build.cjs'},'files':['dist']}))
   (p/'ui'/'build.cjs').write_text("const f=require('fs'); const theme=f.readFileSync('../assets/dist/theme.txt','utf8').trim(); f.mkdirSync('dist',{recursive:true}); f.writeFileSync('dist/ui.txt','ui('+theme+')\\n');")
   (p/'base'/'Dockerfile').write_text('FROM scratch\nCOPY ui/dist/ui.txt /ui.txt\n')
   (p/'app'/'Dockerfile').write_text('ARG BASE\nFROM ${BASE}\nCOPY app.txt /app.txt\n')
   (p/'app'/'app.txt').write_text('application layer\n')
   (p/'stage.py').write_text(stage)
   (p/'experiment.json').write_text(json.dumps({'npm':npm,'docker':reg,'namespace':ns,'builder':builder}))
   (p/'test.npmrc').write_text('registry=http://'+npm+'\n//'+npm+'/:_authToken=experiment-only\n')
   (p/'.gitignore').write_text('events.jsonl\n*.log\nfail-*\n.npm-cache/\nassets/dist/\nui/dist/\n*.oci.tar\n')
   (p/'.dockerignore').write_text('.git\n.npm-cache\n*.log\n*.oci.tar\nevents.jsonl\n')
   cfg={'concurrency':[4,4],'logFormat':'json','updateCheck':False,'github':{'enabled':False},'changelog':{'enabled':False},'commit':{'enabled':True,'push':False,'name':'Review Experiment','email':'review@example.invalid'},'scripts':{'build':sys.executable+' '+str(p/'stage.py')+' build','publish':sys.executable+' '+str(p/'stage.py')+' publish'},'packages':{pkg:{'path':pkg,'isBuildWaitingPublish': (pkg=='base' and case!='missing-barrier') or (pkg in ('assets','ui') and case=='serialized'),'flow':{'build':'build','publish':'publish'}} for pkg in ('assets','ui','base','app')},'dependencies':{'ui':['assets'],'base':['ui'],'app':['base']}}
   (p/'dispat.json').write_text(json.dumps(cfg))
   cmd(['git','init','-q'],p);cmd(['git','config','user.name','Review Experiment'],p);cmd(['git','config','user.email','review@example.invalid'],p)
   cmd(['git','add','.'],p);cmd(['git','commit','-qm','chore: seed fixture'],p)
   for pkg,ver in [('assets','1.4.2'),('ui','3.2.0'),('base','0.8.2'),('app','2.1.0')]:cmd(['git','tag',pkg+'@'+ver],p)
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
   registry={}
   for pkg,ver in [('base','0.8.3'),('app','2.1.1')]:
    query=cmd(['docker','exec',regname,'wget','-qO-','http://127.0.0.1:5000/v2/'+ns+'/'+pkg+'/tags/list'],check=False)
    registry[pkg]={'exit':query.returncode,'body':query.stdout}
   for pkg in ('assets','ui'):
    npmq=urllib.request.urlopen('http://'+npm+'/'+ns+'-'+pkg,timeout=10)
    registry[pkg]=json.load(npmq)
   (p/'registry.json').write_text(json.dumps(registry,indent=2))
   result={'case':case,'rep':rep,'exit':rel.returncode,'retries':retries,'final_exit':final.returncode if final else None,'first_events':events,'first_tags':tags1,'final_tags':tags2,'namespace':ns,'builder':builder}
   results.append(result);(RUN/'results.json').write_text(json.dumps(results,indent=2))
   for pkg,ver in [('base','0.8.3'),('app','2.1.1')]:images.append(reg+'/'+ns+'/'+pkg+':'+ver)
   print(case,rep,'exit',rel.returncode,'retries',retries,'events',len(events),flush=True)
   if not events:raise RuntimeError('no stages executed; inspect '+str(p/'release.log'))
 print('RESULTS',RUN,flush=True)
finally:
 if builder:cmd(['docker','buildx','rm','-f',builder],check=False)
 for name in containers:cmd(['docker','rm','-f',name],check=False)
 if net:
  cmd(['docker','network','disconnect',net,os.environ['HOSTNAME']],check=False)
  cmd(['docker','network','rm',net],check=False)
 remaining=cmd(['docker','ps','-aq','--filter','name=saner-chain-'],check=False).stdout.strip()
 (RUN/'cleanup.json').write_text(json.dumps({'containers':containers,'removed':all(cmd(['docker','inspect',n],check=False).returncode!=0 for n in containers),'images':images},indent=2))
