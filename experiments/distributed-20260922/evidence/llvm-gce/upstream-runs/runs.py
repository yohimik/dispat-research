import json,subprocess,sys,datetime
def t(s): return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
def api(path):
    return json.loads(subprocess.run(['gh','api',path],capture_output=True,text=True).stdout or '{}')
wf=sys.argv[1]; n=int(sys.argv[2]); status=sys.argv[3] if len(sys.argv)>3 else 'success'
runs=api(f'repos/llvm/llvm-project/actions/workflows/{wf}/runs?status={status}&per_page={n}').get('workflow_runs',[])
for r in runs:
    d=(t(r['updated_at'])-t(r['run_started_at'])).total_seconds()/3600
    print(f"{r['id']}\t{r['event']}\t{r['head_branch'][:30]}\t{r['run_started_at'][:10]}\t{d:.2f}h")
