import json,subprocess,sys,datetime
def t(s): return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
run=sys.argv[1]
out=subprocess.run(['gh','api',f'repos/llvm/llvm-project/actions/runs/{run}/jobs?per_page=100','--paginate'],capture_output=True,text=True).stdout
jobs=[]
for chunk in out.replace('}{','}\n{').split('\n'):
    if chunk.strip():
        try: jobs+=json.loads(chunk).get('jobs',[])
        except Exception: pass
for j in sorted(jobs,key=lambda j:j.get('started_at') or ''):
    if not j.get('started_at') or not j.get('completed_at'): continue
    d=(t(j['completed_at'])-t(j['started_at'])).total_seconds()/60
    labels=','.join(j.get('labels') or [])[:40]
    print(f"{d:7.1f} min  {j['conclusion'] or '':9} {j['name'][:70]:70} [{labels}]")
    if len(sys.argv)>2 and d>20:
        for s in j.get('steps',[]):
            if s.get('started_at') and s.get('completed_at'):
                sd=(t(s['completed_at'])-t(s['started_at'])).total_seconds()/60
                if sd>=3: print(f"            {sd:6.1f} min  step: {s['name'][:80]}")
