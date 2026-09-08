#!/bin/bash
# E2 orphan protocol, run inside dispat-exp:node on the e2net network.
# Emits a JSON transcript per step to /results/e2/.
set -u
OUT=/results
mkdir -p "$OUT"
REG=http://failproxy:4873
say() { echo "== $*"; }
NPM_TOKEN=$(node -e "fetch('http://failproxy:4873/-/user/org.couchdb.user:exp',{method:'PUT',headers:{'content-type':'application/json'},body:JSON.stringify({name:'exp',password:'exppass123'})}).then(r=>r.json()).then(j=>console.log(j.token))")
export NPM_TOKEN
reg_version() { # package -> published dist-tags.latest or "absent"
  node -e "fetch('$REG/$1').then(r=>r.json()).then(j=>console.log(j['dist-tags']?.latest??'absent')).catch(()=>console.log('absent'))"
}
tags_of() { git -C "$1" tag -l "$2@*" | sort; }

PHASE=${1:-all}
if [ "$PHASE" = lerna ] || [ "$PHASE" = all ]; then
# ---------- lerna ----------
say "lerna: fixture"
python3 /exp/e2/fixture.py /work/lerna lerna
cd /work/lerna
ln -s /opt/tools/node_modules node_modules 2>/dev/null
say "lerna: version under test: $(lerna --version)"
say "lerna: baseline publish (all six at 1.0.0)"
lerna publish from-package --yes --loglevel warn >/dev/null 2>&1
say "lerna: version (conventional commits)"
lerna version --conventional-commits --yes --loglevel warn >/dev/null 2>&1
echo "TAGS_AFTER_VERSION:"; git tag -l | sort
say "lerna: publish from-git with cli DENIED"
touch /deny/cli
lerna publish from-git --yes --loglevel warn > /tmp/lerna-pub.log 2>&1
echo "exit=$?"
echo "REGISTRY cli: $(reg_version cli)  core: $(reg_version core)  ui: $(reg_version ui)"
echo "CLI TAGS (exist despite failed publish?):"; tags_of . cli
say "lerna: recovery via from-package after clearing deny"
rm -f /deny/cli
lerna publish from-package --yes --loglevel warn > /tmp/lerna-recovery.log 2>&1
echo "exit=$? (dirty-tree block)  REGISTRY cli: $(reg_version cli)"
grep -m2 EUNCOMMIT /tmp/lerna-recovery.log
say "lerna: manual cleanup, then from-package again"
git checkout -q -- . && git clean -qfdx node_modules 2>/dev/null
lerna publish from-package --yes --loglevel warn > /tmp/lerna-recovery2.log 2>&1
echo "exit=$?  REGISTRY cli now: $(reg_version cli)"
cp /tmp/lerna-recovery2.log "$OUT/" 2>/dev/null
cp /tmp/lerna-recovery.log "$OUT/" 2>/dev/null
fi
if [ "$PHASE" = nx ] || [ "$PHASE" = all ]; then

# ---------- nx release ----------
export NX_DAEMON=false NX_TUI=false NX_NO_CLOUD=true
say "nx: fixture"
python3 /exp/e2/fixture.py /work/nx nx
cd /work/nx
ln -s /opt/tools/node_modules node_modules
say "nx: version under test: $(nx --version 2>/dev/null | grep -i local)"
say "nx: baseline publish (all six at 1.0.0)"
nx release publish > /tmp/nx-baseline.log 2>&1
echo "exit=$?  REGISTRY core: $(reg_version core)  cli: $(reg_version cli)"
say "nx: version+tag (conventional commits, publish skipped)"
nx release --skip-publish > /tmp/nx-version.log 2>&1
echo "exit=$?"
echo "TAGS_AFTER_VERSION:"; git tag -l | sort
say "nx: release publish with cli DENIED"
touch /deny/cli
nx release publish > /tmp/nx-pub.log 2>&1
echo "exit=$?"
echo "REGISTRY cli: $(reg_version cli)  core: $(reg_version core)  ui: $(reg_version ui)"
echo "CLI TAGS (exist despite failed publish?):"; tags_of . cli
say "nx: recovery via release publish after clearing deny"
rm -f /deny/cli
nx release publish > /tmp/nx-recovery.log 2>&1
echo "exit=$?  REGISTRY cli now: $(reg_version cli)"
grep -iE "already published|skip|409|conflict" /tmp/nx-recovery.log | head -4
cp /tmp/nx-*.log "$OUT/" 2>/dev/null
fi
if [ "$PHASE" = turbo ] || [ "$PHASE" = all ]; then

# ---------- turborepo + changesets ----------
export TURBO_TELEMETRY_DISABLED=1
say "turbo: fixture"
python3 /exp/e2/fixture.py /work/turbo turbo
cd /work/turbo
ln -s /opt/tools/node_modules node_modules
say "turbo: versions under test: turbo $(turbo --version), changesets $(changeset --version 2>/dev/null | tail -1)"
say "turbo: baseline publish (all six at 1.0.0)"
for p in core cli ui api theme docs; do
  (cd packages/$p && npm publish --ignore-scripts >/dev/null 2>&1)
done
echo "REGISTRY core: $(reg_version core)  cli: $(reg_version cli)"
say "turbo: pipeline (turbo run build)"
turbo run build > /tmp/turbo-build.log 2>&1
echo "exit=$?"
grep -oE "[0-9]+ successful, [0-9]+ total" /tmp/turbo-build.log | head -1
say "turbo: changeset version (core major -> out-of-range patches on cli,ui,api)"
changeset version > /tmp/cs-version.log 2>&1
echo "exit=$?"
for p in core cli ui api theme docs; do
  echo "  $p -> $(python3 -c "import json;print(json.load(open('packages/$p/package.json'))['version'])")"
done
git add -A && git commit -qm "chore: version packages"
echo "TAGS_AFTER_VERSION (expect none new):"; git tag -l | sort
say "turbo: changeset publish with cli DENIED"
touch /deny/cli
changeset publish > /tmp/cs-pub.log 2>&1
echo "exit=$?"
echo "REGISTRY cli: $(reg_version cli)  core: $(reg_version core)  ui: $(reg_version ui)"
echo "CLI TAGS (tag-after-publish, so none expected):"; tags_of . cli
echo "ALL TAGS now:"; git tag -l | sort
say "turbo: recovery via changeset publish after clearing deny"
rm -f /deny/cli
changeset publish > /tmp/cs-recovery.log 2>&1
echo "exit=$?  REGISTRY cli now: $(reg_version cli)"
echo "CLI TAGS now:"; tags_of . cli
grep -iE "already|skip" /tmp/cs-recovery.log | head -4
cp /tmp/turbo-build.log /tmp/cs-*.log "$OUT/" 2>/dev/null
fi
if [ "$PHASE" = dispat ] || [ "$PHASE" = all ]; then
set -euo pipefail
say "dispat: fixture"
python3 /exp/e2/fixture.py /work/dispat dispat
cd /work/dispat
say "dispat: baseline publish (all six at 1.0.0)"
for p in core cli ui api theme docs; do
  (cd packages/$p && npm publish --ignore-scripts --registry "$REG" >"/results/baseline-$p.log" 2>&1)
  [ "$(reg_version "$p")" = 1.0.0 ]
done
say "dispat: release run 1 with cli DENIED"
touch /deny/cli
rc=0
dispat release --log-format json > /results/d1.log 2>&1 || rc=$?
echo "exit=$rc"
[ "$rc" -ne 0 ]
python3 /exp/shared/planjson.py < /results/d1.log > /results/dispat-run1-plan.json
for log in /tmp/pub-*.log; do cp "$log" "/results/run1-$(basename "$log")"; done
echo "CLI TAGS after failed run (must be empty beyond 1.0.0):"
tags_of . cli | tee /results/run1-cli-tags.txt
[ "$(cat /results/run1-cli-tags.txt)" = cli@1.0.0 ]
[ "$(reg_version cli)" = 1.0.0 ]
[ "$(reg_version core)" = 1.1.0 ]
echo "REGISTRY cli: 1.0.0  core: 1.1.0"
say "dispat: release run 2, deny cleared"
rm /deny/cli
rc=0
dispat release --log-format json > /results/d2.log 2>&1 || rc=$?
echo "exit=$rc"
[ "$rc" = 0 ]
for log in /tmp/pub-*.log; do cp "$log" "/results/run2-$(basename "$log")"; done
echo "CLI TAGS now:"
tags_of . cli | tee /results/run2-cli-tags.txt
[ "$(cat /results/run2-cli-tags.txt)" = "$(printf 'cli@1.0.0\ncli@1.0.1')" ]
[ "$(reg_version cli)" = 1.0.1 ]
echo "REGISTRY cli now: 1.0.1"
say "dispat: run 3 must be empty"
dispat status --log-format json > /results/status3.log 2>&1
python3 /exp/shared/planjson.py < /results/status3.log > /results/plan3.json
python3 - <<'CHECK'
import json
from pathlib import Path
plan=json.loads(Path('/results/plan3.json').read_text())
assert len(plan)==6,plan
assert not [p for p,r in plan.items() if r['changed']],plan
rows=[json.loads(l) for l in Path('/results/status3.log').read_text().splitlines() if l.startswith('{')]
assert any(r.get('message')=='release plan ready' and r.get('releasing')==0 for r in rows)
Path('/results/verdict.json').write_text(json.dumps({'passed':True,'failed_publish_untagged':True,'same_version_recovery':True,'final_releasing':0})+'\n')
print('releasing: []')
CHECK
fi
say done
