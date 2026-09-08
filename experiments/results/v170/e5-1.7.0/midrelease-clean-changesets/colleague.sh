set -eu
cd /work/changesets-colleague
echo "// concurrent fix" >> packages/api/index.js
msg="fix(api): concurrent change"
printf -- '---\n"api": patch\n---\n\nconcurrent change\n' > .changeset/concurrent-change.md
git add -A && git commit -q -m "$msg" && git push -q origin HEAD:refs/heads/main
git rev-parse HEAD > /results/midrelease-clean-changesets/colleague.sha
echo "colleague pushed $(git rev-parse --short HEAD): $msg"
