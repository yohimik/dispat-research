set -eu
cd /work/changesets-colleague
python3 - <<'EOF'
import json
p = 'packages/core/package.json'
d = json.load(open(p))
d = {'name': d['name'], 'description': 'the core library', **{k: v for k, v in d.items() if k != 'name'}}
json.dump(d, open(p, 'w'), indent=1); open(p, 'a').write('\n')
EOF
msg="fix(core): describe the package"
printf -- '---\n"core": patch\n---\n\ndescribe the package\n' > .changeset/describe-the-package.md
git add -A && git commit -q -m "$msg" && git push -q origin HEAD:refs/heads/main
git rev-parse HEAD > /results/midrelease-conflict-changesets/colleague.sha
echo "colleague pushed $(git rev-parse --short HEAD): $msg"
