import os,pathlib,json,time,subprocess,sys
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
