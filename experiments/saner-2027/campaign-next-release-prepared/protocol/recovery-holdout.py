import sys,json,pathlib
sys.path.insert(0,'/exp/e4')
from recovery import episode
out=pathlib.Path('/results/recovery');rows=[]
for n in (20,100):
 for probability in (.1,.3):
  for seed in range(100,105):
   row=episode(n,probability,seed,str(out/'failures'));rows.append(row)
   (out/'results.json').write_text(json.dumps(rows,indent=2))
   print(json.dumps(row),flush=True)
assert len(rows)==20 and all(r['converged'] and r['g_ok'] for r in rows)
