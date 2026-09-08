set -eu
cd /work/dispat-colleague
echo "// concurrent fix" >> packages/api/index.js
msg="fix(api): concurrent change"
git add -A && git commit -q -m "$msg" && git push -q origin HEAD:refs/heads/main
git rev-parse HEAD > /results/midrelease-clean-dispat/colleague.sha
echo "colleague pushed $(git rev-parse --short HEAD): $msg"
