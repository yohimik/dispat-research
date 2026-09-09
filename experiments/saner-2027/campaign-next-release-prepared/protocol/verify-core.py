#!/usr/bin/env python3
"""Validate completeness and internal accounting without treating divergences as harness failure."""
import collections, json, pathlib, sys

root=pathlib.Path(sys.argv[1]).resolve()
expected_version=sys.argv[2]
source=root/'e1-core-90001-300.json'
data=json.loads(source.read_text());summary=data['summary'];rows=data['rows']
errors=[]
def require(value,message):
 if not value:errors.append(message)
expected_seeds=set(range(90001,90301));observed=[r.get('seed') for r in rows]
require(len(rows)==300,'row count must be 300')
require(len(observed)==len(set(observed)),'seeds must be unique')
require(set(observed)==expected_seeds,'seeds must be exactly 90001..90300')
require(summary.get('profile')=='core','summary profile must be core')
require(summary.get('instances')==300,'summary instances must be 300')
require(summary.get('dispat','').startswith('dispat '+expected_version+' ('),'summary must identify locked Dispat version')
for row in rows:
 require(isinstance(row.get('packages'),int) and row['packages']>0,f"seed {row.get('seed')}: positive package count required")
 require(isinstance(row.get('diffs'),list),f"seed {row.get('seed')}: diffs must be a list")
 for diff in row.get('diffs',[]):
  require(isinstance(diff,list) and len(diff)==2 and all(isinstance(x,str) and x for x in diff),f"seed {row.get('seed')}: malformed difference")
 if row.get('invalid'):
  evidence=root.parent/row.get('failure','')
  require(bool(row.get('failure')) and evidence.is_dir(),f"seed {row.get('seed')}: invalid execution dossier missing")
  if evidence.is_dir():
   for name in ('failure.json','fixture.tar.gz','stdout.log','stderr.log'):require((evidence/name).is_file(),f"seed {row.get('seed')}: missing {name}")
   if (evidence/'failure.json').is_file():
    failure=json.loads((evidence/'failure.json').read_text());require(failure.get('seed')==row.get('seed') and failure.get('kind')=='invalid-execution',f"seed {row.get('seed')}: invalid dossier identity")
 if row.get('rejection'):
  rejection=row['rejection'];evidence=root/rejection.get('evidence','')
  require(rejection.get('code')=='E195' and rejection.get('returncode')==1,f"seed {row.get('seed')}: rejection classification")
  require(evidence.is_dir() and (evidence/'rejection.json').is_file(),f"seed {row.get('seed')}: rejection dossier missing")
  if (evidence/'rejection.json').is_file():
   detail=json.loads((evidence/'rejection.json').read_text());require(detail.get('seed')==row.get('seed') and detail.get('kind')=='semantic-rejection',f"seed {row.get('seed')}: rejection dossier identity")
 if any(d[1]=='UNKNOWN' for d in row.get('diffs',[]) if isinstance(d,list) and len(d)==2):
  require((root/'dossiers-core'/('seed'+str(row.get('seed'))) / 'dossier.json').is_file(),f"seed {row.get('seed')}: UNKNOWN difference dossier missing")
classes=collections.Counter(d[1] for r in rows for d in r.get('diffs',[]) if isinstance(d,list) and len(d)==2)
invalid=sum(bool(r.get('invalid')) for r in rows)
rejected=sum(bool(r.get('rejection')) for r in rows)
clean=sum(not r.get('diffs') and not r.get('invalid') for r in rows)
accepted_matching=sum(not r.get('diffs') and not r.get('invalid') and not r.get('rejection') for r in rows)
require(summary.get('clean')==clean,'summary clean count mismatch')
require(summary.get('invalid')==invalid,'summary invalid count mismatch')
require(summary.get('rejected')==rejected,'summary rejected count mismatch')
require(summary.get('divergence_classes')==dict(classes),'summary divergence classes mismatch')
out={'status':'INTEGRITY_PASS' if not errors else 'INTEGRITY_FAIL','profile':'core','expected_seeds':[90001,90300],
     'rows':len(rows),'accepted_matching':accepted_matching,'matching_including_semantic_rejections':clean,'semantic_rejections':rejected,'invalid_executions':invalid,
     'rows_with_differences':sum(bool(r.get('diffs')) for r in rows),'difference_classes':dict(classes),'errors':errors}
(root/'verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if errors:raise SystemExit(1)
