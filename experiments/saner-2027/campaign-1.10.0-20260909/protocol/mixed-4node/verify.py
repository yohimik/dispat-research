#!/usr/bin/env python3
import io,json,pathlib,random,sys,tarfile
from oracle_predicates import base_build_does_not_wait_for_ui_publication
p=pathlib.Path(sys.argv[1]);rows=json.loads((p/'results.json').read_text());checks=[];summary=[]
def check(ok,msg):
 if not ok:raise AssertionError(msg)
 checks.append(msg)
def oci_contains(path,member,content):
 with tarfile.open(path) as outer:
  index=json.load(outer.extractfile('index.json'))
  manifest_digest=index['manifests'][0]['digest'].split(':',1)[1]
  manifest=json.load(outer.extractfile('blobs/sha256/'+manifest_digest))
  for layer in manifest['layers']:
   blob=outer.extractfile('blobs/sha256/'+layer['digest'].split(':',1)[1]).read()
   with tarfile.open(fileobj=io.BytesIO(blob),mode='r:*') as payload:
    names={n.lstrip('./'):n for n in payload.getnames()}
    if member in names and payload.extractfile(names[member]).read()==content:return True
 return False
configurations={'mixed','serialized','missing-barrier','base-failure','app-failure'}
expected_pairs={(case,rep) for case in configurations for rep in range(6)}
check(len(rows)==30,'thirty case repetitions')
check({(r.get('case'),r.get('rep')) for r in rows}==expected_pairs,'exact five configurations times repetitions zero through five')
schedule=json.loads((p/'schedule.json').read_text());expected_order=[(rep,case) for rep in range(6) for case in ['mixed','serialized','missing-barrier','base-failure','app-failure']];random.Random(20260909).shuffle(expected_order)
check(schedule.get('seed')==20260909,'declared schedule seed')
check(schedule.get('order')==[list(x) for x in expected_order],'exact seeded schedule')
check([(r.get('rep'),r.get('case')) for r in rows]==expected_order,'result order follows declared schedule')
expected={'assets':'1.5.0','ui':'3.2.1','base':'0.8.3','app':'2.1.1'}
for r in rows:
 name=r['case']+'-'+str(r['rep']);e=sorted(r['first_events'],key=lambda x:x['monotonic_ns']);idx={(x['package'],x['stage'],x['event']):i for i,x in enumerate(e)};t={(x['package'],x['stage'],x['event']):x['monotonic_ns'] for x in e};codes={(x['package'],x['stage'],x['event']):x['code'] for x in e}
 check(all(x.get('package') in expected and x.get('stage') in ('build','publish') and x.get('event') in ('start','end') and isinstance(x.get('monotonic_ns'),int) and isinstance(x.get('wall_ns'),int) and isinstance(x.get('code'),int) for x in e),name+': event schema and package universe')
 check(all(x.get('version')==expected.get(x.get('package')) for x in e),name+': initial versions')
 check(len(idx)==len(e),name+': unique package-stage-event keys')
 intervals={(pkg,stage) for pkg,stage,event in idx if event=='start'}
 check(intervals=={(pkg,stage) for pkg,stage,event in idx if event=='end'},name+': every stage has one start and one end')
 check(all(t[pkg,stage,'start']<=t[pkg,stage,'end'] for pkg,stage in intervals),name+': valid per-stage intervals')
 check(idx['assets','build','end']<idx['ui','build','start'],name+': assets local output ready for ui')
 check(idx['ui','build','end']<idx['base','build','start'],name+': ui local output ready for base')
 check(idx['assets','publish','end']<idx['ui','publish','start'],name+': assets publication precedes ui publication')
 check(idx['ui','publish','end']<idx['base','publish','start'],name+': ui publication precedes base publication')
 case=r['case']
 registry=json.loads((p/name/'registry.json').read_text())
 check((p/name/'assets/dist/theme.txt').read_text()=='new theme\n',name+': built assets preserve changed source')
 check((p/name/'ui/dist/ui.txt').read_text()=='ui(new theme)\n',name+': ui build consumes assets local output')
 ui_manifest=json.loads((p/name/'ui/package.json').read_text());asset_dependency=ui_manifest.get('dependencies',{}).get(r['namespace']+'-assets')
 check(asset_dependency in ('^1.4.2','^1.5.0'),name+': ui declares compatible assets npm dependency')
 check(oci_contains(p/name/'base.oci.tar','ui.txt',b'ui(new theme)\n'),name+': base OCI artifact contains ui local output')
 check('1.5.0' in registry['assets']['versions'],name+': assets npm version independently observed')
 check('3.2.1' in registry['ui']['versions'],name+': ui npm version independently observed')
 check(registry['ui']['versions']['3.2.1'].get('dependencies',{}).get(r['namespace']+'-assets') in ('^1.4.2','^1.5.0'),name+': published ui manifest retains assets dependency')
 for pkg,ver in [('base','0.8.3'),('app','2.1.1')]:
  expected_present=not (case=='missing-barrier' and pkg=='app')
  observed=registry[pkg]['exit']==0 and ver in json.loads(registry[pkg]['body']).get('tags',[])
  check(observed==expected_present,name+': '+pkg+' registry state')
 check((r['exit']==0)==(case in ('mixed','serialized')),name+': expected first outcome')
 if case=='serialized':
  check(idx['assets','publish','end']<idx['ui','build','start'],name+': serialized assets barrier')
  check(idx['ui','publish','end']<idx['base','build','start'],name+': serialized ui barrier')
 if case in ('mixed','serialized','app-failure'):
  check(idx['base','publish','end']<idx['app','build','start'],name+': base publication precedes app build')
 if case=='mixed':
  overlap_assets=min(t['ui','build','end'],t['assets','publish','end'])-max(t['ui','build','start'],t['assets','publish','start'])
  overlap_ui=min(t['base','build','end'],t['ui','publish','end'])-max(t['base','build','start'],t['ui','publish','start'])
  check(overlap_assets>0,name+': ui local build overlaps assets publication')
  check(base_build_does_not_wait_for_ui_publication(t),name+': base local build does not wait for ui publication')
  summary.append({'case':name,'assets_to_ui_overlap_seconds':overlap_assets/1e9,
                  'ui_publication_end_after_base_build_start_seconds':(t['ui','publish','end']-t['base','build','start'])/1e9,
                  'ui_to_base_interval_intersection_seconds':overlap_ui/1e9,
                  'base_build_completed_before_ui_publish_started':t['base','build','end']<t['ui','publish','start']})
 if case=='missing-barrier':
  check(idx['app','build','start']<idx['base','publish','end'],name+': barrier absent')
  check(any(x['package']=='app' and x['event']=='end' and x['code']!=0 for x in e),name+': app build fails')
  check(codes['app','build','end']==37,name+': injected missing-base build failure code')
  check('app@2.1.1' not in r['first_tags'],name+': failed app untagged')
  log=(p/name/'release.log').read_text()
  check('not found' in log.lower(),name+': registry base absent')
 if case=='base-failure':
  check(codes['base','publish','end']==37,name+': injected base publication failure code')
  check(not any(x['package']=='app' for x in e),name+': app blocked')
  check('base@0.8.3' not in r['first_tags'],name+': failed base untagged')
 if case in ('base-failure','app-failure'):
  check(r['retries']==[0],name+': successful retry')
  all_events=[json.loads(x) for x in (p/name/'events.jsonl').read_text().splitlines()]
  check(all(x['version']==expected[x['package']] for x in all_events),name+': stable retry versions')
 if case=='app-failure':
  check(codes['app','build','end']==37,name+': injected app build failure code')
  check('app@2.1.1' not in r['first_tags'],name+': failed app untagged')
 if case!='missing-barrier':
  check(oci_contains(p/name/'app.oci.tar','ui.txt',b'ui(new theme)\n'),name+': final app OCI artifact contains inherited ui output')
  check(r['final_exit']==0,name+': successful unchanged rerun')
  check(all(k+'@'+v in r['final_tags'] for k,v in expected.items()),name+': all completion records')
  log=(p/name/'final.log').read_text()
  check('build started' not in log and 'publish started' not in log,name+': no repeated stage on unchanged rerun')
check(json.loads((p/'cleanup.json').read_text())['removed'],'experiment containers removed')
out={'status':'PASS','checks_executed':len(checks),'configurations':5,'repetitions_per_configuration':6,'executions':30,'repair_executions':12,'overlap':summary,'checks':checks}
(p/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='checks'},indent=2))
