#!/usr/bin/env python3
import json,pathlib,sys
p=pathlib.Path(sys.argv[1]);rows=json.loads((p/'results.json').read_text());checks=[];summary=[]
def check(ok,msg):
 if not ok:raise AssertionError(msg)
 checks.append(msg)
check(len(rows)==10,'ten case repetitions')
expected={'assets':'1.5.0','base':'0.8.3','app':'2.1.1'}
for r in rows:
 name=r['case']+'-'+str(r['rep']);e=r['first_events'];idx={(x['package'],x['stage'],x['event']):i for i,x in enumerate(e)};t={(x['package'],x['stage'],x['event']):x['monotonic_ns'] for x in e}
 check(all(x['version']==expected[x['package']] for x in e),name+': initial versions')
 check(all(e[i]['monotonic_ns']<=e[i+1]['monotonic_ns'] for i in range(len(e)-1)),name+': shared clock ordering')
 check(idx['assets','build','end']<idx['base','build','start'],name+': local artifact ready')
 check(idx['assets','publish','end']<idx['base','publish','start'],name+': upstream publication ordering')
 case=r['case']
 check((r['exit']==0)==(case in ('mixed','serialized')),name+': expected first outcome')
 if case=='serialized':
  check(idx['assets','publish','end']<idx['base','build','start'],name+': serialized barrier')
 if case in ('mixed','serialized','app-failure'):
  check(idx['base','publish','end']<idx['app','build','start'],name+': base publication precedes app build')
 if case=='mixed':
  overlap=min(t['base','build','end'],t['assets','publish','end'])-max(t['base','build','start'],t['assets','publish','start'])
  check(overlap>0,name+': local build overlaps npm publication')
  summary.append({'case':name,'overlap_seconds':overlap/1e9})
 if case=='missing-barrier':
  check(idx['app','build','start']<idx['base','publish','start'],name+': barrier absent')
  check(any(x['package']=='app' and x['event']=='end' and x['code']!=0 for x in e),name+': app build fails')
  check('app@2.1.1' not in r['first_tags'],name+': failed app untagged')
  log=(p/name/'release.log').read_text()
  check('not found' in log.lower(),name+': registry base absent')
 if case=='base-failure':
  check(not any(x['package']=='app' for x in e),name+': app blocked')
  check('base@0.8.3' not in r['first_tags'],name+': failed base untagged')
 if case in ('base-failure','app-failure'):
  check(r['retries']==[0],name+': successful retry')
  all_events=[json.loads(x) for x in (p/name/'events.jsonl').read_text().splitlines()]
  check(all(x['version']==expected[x['package']] for x in all_events),name+': stable retry versions')
 if case!='missing-barrier':
  check(r['final_exit']==0,name+': successful unchanged rerun')
  check(all(k+'@'+v in r['final_tags'] for k,v in expected.items()),name+': all completion records')
  log=(p/name/'final.log').read_text()
  check('build started' not in log and 'publish started' not in log,name+': no repeated stage on unchanged rerun')
check(json.loads((p/'cleanup.json').read_text())['removed'],'experiment containers removed')
out={'status':'PASS','assertions':len(checks),'cases':10,'recovery_cases':4,'overlap':summary,'checks':checks}
(p/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='checks'},indent=2))
