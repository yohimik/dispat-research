# dispat v1.6.0 vs v1.7.0: the mid-release experiment (E5)

2026-09-02. Both versions run as the released binary copied out of the
official `yohimik/dispat-alpine:<version>` image, inside the harness that
now lives in the dispat repository at `tests/experiments` (commit
9a5ad365, "ci(experiments): run the release experiments after the images
publish"). The harness is the same for every tool: one six-package
fixture, one injected fault, one recovery, one question of what the tool
would release next. Records: `e5-1.7.0/` (twelve cells: three
experiments by four tools) and `e5-1.6.0/` (the three dispat cells).

## The fault

E5 `midrelease`: a colleague's commit lands on `origin/main` right before
the tool's own first push of the branch. A git shim on `PATH` fires the
colleague's push once, immediately before the first `git push` the tool
makes that is neither its release lock nor a commit, so the interleaving
is a point in each tool's own sequence and the same for every tool. Two
scenarios: `clean` (the colleague touches `api/index.js`, no overlap with
the release) and `conflict` (the colleague edits `core/package.json` next
to the version line the release rewrites).

E2 `orphan` (the registry refusing `cli` mid-publish) was rerun in the
same harness as the control: identical on both versions, 7/7.

## Verdict

v1.7.0 closes the gap E5 exposes in v1.6.0. In v1.6.0 the colleague's
push turns a release that already published into a partial one: the
registry serves four new versions, the tags naming them exist only in the
release clone, `dispat status` sees nothing to do, and a rerun refuses to
start. Getting out is manual. In v1.7.0 the same push is absorbed: dispat
fetches, merges the branch on top of its release commit (the release
commit stays first parent, the tags stay on the planned tree), pushes,
warns W242, returns the lock and exits 0. The colleague's own change is
the next plan, and the next run from the same clone releases it. With a
conflict, W243 names it, the release's side is kept on `main`, and the
colleague's tip is pushed to a `release-conflicts/<released set>-<UTC>`
branch for reconciliation.

## dispat, both versions

| Cell | v1.6.0 | v1.7.0 |
|---|---|---|
| midrelease clean, exit | 1 (E224 push failed: `! [rejected] HEAD -> main (fetch first)`) | 0 (W242) |
| midrelease clean, clone after | 1 ahead 1 behind; release commit not on `origin/main` | level; merge commit on top, release commit first parent |
| midrelease clean, packages after | core 1.1.0, cli/ui/api 1.0.1 all `unpushed` (registry has them, tags local only) | all `consistent` |
| midrelease clean, next plan | empty | `api 1.0.1 -> 1.0.2 (direct)` |
| midrelease clean, rerun | exit 1: "the checkout is behind origin/main; pull before releasing" | exit 0, api 1.0.2 consistent |
| midrelease clean, checks | 5/12 | 12/12 |
| midrelease conflict, exit | 1 (E224) | 0 (W242 + W243) |
| midrelease conflict, origin | `main` only | `main` plus `release-conflicts/core-1.1.0-api-1.0.1-cli-1.0.1-ui-1.0.1-20260902-064033` |
| midrelease conflict, `main`'s tree | colleague's alone | release's side (version 1.1.0, no markers) |
| midrelease conflict, next plan | empty | `core 1.1.0 -> 1.1.1 (direct)` |
| midrelease conflict, rerun | refused, as above | exit 0, core 1.1.1 consistent |
| midrelease conflict, checks | 6/14 | 14/14 |
| orphan, checks | 7/7 | 7/7 |

The v1.6.0 rows are the same on both scenarios because the refusal comes
before any merge is attempted: the rejected push is the end of the run.
The lock tag is returned on both versions.

## The other tools on the same fault (v1.7.0 image)

| Cell | Steps | Checks | What it left |
|---|---|---|---|
| clean lerna | `version=1 publish=0 rebase=0 push=0 changed=0` | 1/5 | `lerna version` fails on the rejected push with all six tags local; `publish from-git` publishes them anyway; after `pull --rebase` every tag is `dangling` and `lerna changed` lists all six again |
| conflict lerna | `version=1 publish=0 rebase=1 resolve=0 push=0 changed=0` | 2/5 | as above, plus a manual conflict resolution in the rebase |
| clean nx | `release=1 recover=0 release2=0 publish=0 push=0 next=0` | 2/6 | pushes before it commits or tags, so the rejected push aborts with staged bumps and nothing recorded; `reset --hard` and `pull --rebase`, then a second release folds the colleague's fix into the same versions; tags unpushed until pushed by hand; next plan empty |
| conflict nx | same | 2/6 | same |
| clean changesets | `version=0 commit=0 publish=0 push=1 rebase=0 push2=0 status=0` | 3/5 | publishes and tags before the operator's push; after the rebase the four tags are `dangling`; the next plan is right because the colleague added a changeset file |
| conflict changesets | `version=0 commit=0 publish=0 push=1 rebase=1 resolve=0 push2=0 status=0` | 3/5 | same, with the manual resolution |
| clean/conflict dispat | `release=0 status=0 rerun=0` | 12/12, 14/14 | see above |

The check counts for lerna, nx and changesets are descriptions, not
failures: the harness asks every tool the questions dispat answers, and
records which hold.

`orphan` on the v1.7.0 image, for the record: lerna 3/5 (cli tagged for a
version the registry never received, `from-package` needs a manual
cleanup), nx 4/5 (same orphan tag, recovery skips what published),
changesets 5/5, dispat 7/7.

## Reading the git calls

`git-calls.log` in each dispat cell shows where the fault lands:
`push origin refs/tags/dispat-release-lock` first (not counted), then
`push origin HEAD` with the injection immediately before it. In v1.7.0
the next calls are the fetch, the merge, `push origin HEAD` again, the
tag push, and `push origin --delete refs/tags/dispat-release-lock`. In
v1.6.0 the sequence ends at the lock deletion with no second `push origin
HEAD`.

## Notes

- Dependencies in the fixture are tilde ranges, so the minor of `core`
  is outside its consumers' ranges and reaches `cli`, `ui` and `api`
  under every tool; `theme` and `docs` do not depend on `core`. lerna and
  nx cascade a patch of `core` transitively to all six; changesets and
  dispat keep it with `core`, which is why `expected_next` differs by
  tool.
- The v1.6.0 cells were run with `EXPECT=0` so the container's exit code
  is not the verdict; the verdict files carry the same checks as the
  v1.7.0 cells.
- The harness now runs in the repository's CI after every release that
  publishes the images (`Experiments` workflow, called from the release
  workflow with the version it published; dispatchable by hand for any
  released version). First CI run: https://github.com/yohimik/dispat/actions/runs/33600778853

## E1 on the v1.7.0 image

The differential campaign (model oracle vs the released planner) was
rerun with the v1.7.0 binary: golden PASS; core 1000/1000 (seeds
1..1000) and 500/500 (seeds 5001..5500); full 1000 -> 412 clean with
PG1 409 / PG2 240 / PG2x 58 / PG3 390, and 500 -> 222 clean with PG1
182 / PG2 135 / PG2x 23 / PG3 200; zero unclassified. Per-seed rows
match the v1.6.0 campaign on all 3,000 instances; only the version
string differs. Records in `e1-core/` and `e1-full/` beside this file.
The planner diff between the two tags is `AliasFilter` in
`internal/plan/plan.go` plus the W242/W243 codes; the mid-release fix
is in `internal/app/finalize.go` and `internal/gitx/gitx.go`.
