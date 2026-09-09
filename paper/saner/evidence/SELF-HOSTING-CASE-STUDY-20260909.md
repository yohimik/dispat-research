# Bounded self-hosting case-study evidence, 9 September 2026

This note is evidence for later editorial review. It is not manuscript text and does not change the experimental campaign. Repository observations refer to a checkout of the public `yohimik/dispat` repository and GitHub Actions metadata observed on 9 September 2026.

## Claims the evidence supports

Dispat is a substantial, rapidly developed Go monorepo that uses its checkout-built CLI to select tests and builds and to perform its own releases. At committed HEAD `5d93d800ca42de8a9b58aafeda639afd5e9ea9c3`, a conservative first-party count over `pkg/`, `services/`, `tests/`, and `tools/` contains 460 tracked `.go` files and 149,292 physical lines: 228 non-test files / 61,478 lines and 232 `_test.go` files / 87,814 lines. The current working tree, which includes the uncommitted commit-authoring feature, contains 468 files / 150,902 lines: 231 non-test files / 62,249 lines and 237 test files / 88,653 lines. These are size descriptors, not measures of delivered functionality, quality, effort, or handwritten code.

The first commit is `1fd472c70c4c8a44fff0df292cbcaa1bca3ce55e`, authored and committed at `2026-07-27T22:13:16+04:00`. Release-candidate tags for the CLI appear on 9 August, including `services/dispat/v1.0.0-rc.0` at `2026-08-09T15:27:44Z`; stable `services/dispat/v1.0.0` appears at `2026-08-16T19:36:54Z`. The interval from the first commit to the start of 9 September is already 43.07 elapsed days and spans 44 calendar dates. Therefore, “the whole project was built in under one month” is false. A bounded phrasing such as “the project reached a CLI release candidate roughly thirteen days after its first commit and continued intensive development through September 9” matches the Git evidence.

The repository uses existing libraries where suitable. Direct requirements visible in the first-party module manifests include `fsnotify` for file notifications, `go-toml/v2` and `yaml.v3` for configuration formats, `x/mod` for Go-module handling, `zerolog` for logging, `pflag` for flags, `gotenv` for environment files, `testify` for tests, and Aqua as repository tooling. This demonstrates reuse; it does not determine how much implementation work was avoided or whether each dependency choice was optimal.

## Observed self-hosting mechanism

The tests workflow installs a published Dispat only as a bootstrap, builds Dispat from the checkout, prepends that fresh binary to `PATH`, and then invokes it. The selective test step is:

```sh
dispat run tests --since "$(sh scripts/ci-base.sh)" --consumers
```

The same workflow uses `dispat run vet --since all`, `dispat exec` for repository-wide checks, and `dispat run build --since ...` for changed builds. Thus the observed self-hosting fact is stronger than merely storing a Dispat configuration: the checkout-built program drives test and build selection in CI. The `--consumers` test invocation explicitly expands from changed providers to consumers according to Dispat's configured graph.

The release workflow also builds the checkout's CLI before using `dispat status --require-release` to decide whether a release exists. If so, a full pre-release suite runs through `dispat run tests --since all`; only after the `tests` and credential-check jobs succeed does the release job invoke `dispat`. The repository configuration defines release scripts including `changelog: dispat changelog`, `commit: dispat commit --tag --push`, and `github: dispat github`, while package-local configuration supplies build, test, publication, and dependency behavior. This is direct evidence that Dispat computes and executes its own repository release graph.

## Observed GitHub runs, including negatives

The most recent completed release run queried, [34119084809](https://github.com/yohimik/dispat/actions/runs/34119084809), ran on commit `8db82c612c59fd7849ecc6895c941aabd2658456` from `2026-09-07T11:55:10Z` to `12:16:17Z` and concluded `success`. Its recorded jobs show a successful checkout-built plan, full suite, and `Run dispat, publish binaries` job; within that release job, `Run the release` succeeded. Three preceding release runs also succeeded: [34108847285](https://github.com/yohimik/dispat/actions/runs/34108847285), [34061459953](https://github.com/yohimik/dispat/actions/runs/34061459953), and [34054341541](https://github.com/yohimik/dispat/actions/runs/34054341541).

The history is not uniformly successful. `gh run list --workflow release.yml --limit 100` returned 92 runs: 73 successful, 13 failed, and 6 cancelled. These counts describe workflow outcomes across changing code and configuration; they are neither independent trials nor a reliability rate for the current version. For a concrete failure, [33945938195](https://github.com/yohimik/dispat/actions/runs/33945938195) passed planning and the full test suite on 5 September but failed in `Run the release`. For a concrete cancellation, [34053351827](https://github.com/yohimik/dispat/actions/runs/34053351827) passed planning but its full-suite test step was cancelled, so its publication job did not run. The GitHub metadata alone does not establish why either run failed or was cancelled. A defensible account must retain these negatives alongside successful self-releases.

## AI-assistance boundary

The user's account is that the codebase was developed rapidly with substantial AI assistance. Git records commits under `yohimik` and `github-actions[bot]`; it does not contain a reliable per-line or per-commit provenance field for AI contribution. Commit volume, elapsed time, file count, and test volume cannot identify which code was generated, suggested, reviewed, or rewritten by AI. Accordingly, the case study can report “author-reported AI-assisted development” and independently report the dates and repository measurements above. It cannot infer that AI caused the pace, reduced defects, or produced the observed correctness. Successful CI and releases establish that particular automated checks and workflows completed, not that the software is defect-free.

This is a single-project observational case. The author also controls the implementation, configuration, tests, and release workflow, which creates construct and observer bias. Self-hosting exercises realistic integration paths but is not an independent external adoption study. The high test-line count includes fixtures and harness code; physical lines are sensitive to formatting and are not semantic LOC. The working-tree count is provisional because those files were not committed when measured.

## Reproduction commands and source locations

Run these from `/Users/yohimik/Projects/dispat`:

```sh
git log --reverse --format='%H%x09%aI%x09%cI%x09%s' | head
git for-each-ref refs/tags/services/dispat/v1.0.0-rc.0 refs/tags/services/dispat/v1.0.0 \
  --format='%(creatordate:iso8601)%09%(refname:short)%09%(objectname)'
git rev-parse HEAD
git status --short
```

The committed code count used `git ls-tree -r --name-only HEAD`, retained `.go` paths rooted at `pkg/`, `services/`, `tests/`, or `tools/`, and excluded `vendor`, `deps`, `build`, `dist`, `output`, `generated`, `*.gen.go`, and filenames containing `generated`. Contents and physical line counts came from `git show HEAD:<path>`. The working-tree count used the same roots and exclusions over `Path.rglob('*.go')`. `rg -l '^// Code generated .* DO NOT EDIT\.' pkg services tests tools -g '*.go'` returned no additional generated files.

Configuration and workflow sources:

- `/Users/yohimik/Projects/dispat/.github/workflows/tests.yml`, especially lines 26–30, 59–69, 139–170, and 193–227 in the inspected checkout;
- `/Users/yohimik/Projects/dispat/.github/workflows/release.yml`, especially lines 3–28, 38–44, 81–113, 189–279, and the `Run the release` step beginning near line 403;
- `/Users/yohimik/Projects/dispat/dispat.yaml` and package/space `dispat.yaml` files;
- `pkg/*/go.mod`, `services/dispat/go.mod`, `tests/integration/go.mod`, and `tools/go.mod`.

GitHub observations used:

```sh
gh run list --repo yohimik/dispat --workflow release.yml --limit 100 \
  --json databaseId,conclusion,createdAt,updatedAt,headSha,url
gh run view 34119084809 --repo yohimik/dispat \
  --json databaseId,conclusion,createdAt,updatedAt,headSha,url,jobs
gh run view 33945938195 --repo yohimik/dispat \
  --json databaseId,conclusion,createdAt,updatedAt,headSha,url,jobs
gh run view 34053351827 --repo yohimik/dispat \
  --json databaseId,conclusion,createdAt,updatedAt,headSha,url,jobs
```

The GitHub queries are time-dependent. Preserve the run IDs and observation date when using them; refresh counts only as a new dated observation rather than overwriting these figures.
