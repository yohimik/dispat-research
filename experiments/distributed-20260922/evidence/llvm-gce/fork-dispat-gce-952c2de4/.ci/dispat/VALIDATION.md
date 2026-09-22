# Setup validation — 2026-09-21

LLVM source: `a9f4d3ff18c554d29bbabc546f9a9df0376701e0`, cloned from
`yohimik/llvm-project` with complete history and partial blob transfer.
Working branch: `codex/dispat-llvm-distributed`. Setup changes remain uncommitted.

| Check | Result |
| --- | --- |
| Published dispat 1.10.0 loads local policy | Passed |
| Local/distributed profiles retain identical release policy | Passed |
| Disposable Git fixture plans all four packages at 24.0.0-rc.0 | Passed, no parser errors |
| Status leaves fixture worktree unchanged and creates no tags | Passed |
| Missing, corrupt, wrong-version and mode-changed SDK rejection | Passed |
| Consumers use the installed SDK without invoking a provider build | Passed with command mocks |
| Escaping symlink and conflicting bundle-file rejection | Passed |
| Test failure prevents install and success metadata | Passed with command mocks |
| Release/export gates reject before publication | Passed |
| Manual-release workflow structure | Passed |
| actionlint 1.7.12 workflow validation with declared runner label | Passed (external shell/Python linters disabled) |
| LLVM CMake configure/generate | Passed with AppleClang 21, CMake 4.4.3, Ninja 1.13.2, Python 3.13.15 on macOS arm64 |
| Published CLI rejects experimental profile | Expected failure: unsupported `buildPlatforms` key |

The automated suite contains 10 tests. Run it from the checkout with the documented
Python environment on PATH:

```sh
dispat exec validate --in root
```

The workflow can also be checked with actionlint 1.7.12, including its custom
self-hosted runner label:

```sh
actionlint -config-file .ci/dispat/actionlint.yaml -shellcheck= -pyflakes= .github/workflows/dispat.yml
```

The CMake check configured the LLVM SDK for X86 code generation on this arm64
host; it did not compile it. Upstream CMake developer/benchmark warnings were
observed, with successful configure and generate exit status. No full LLVM,
Clang, LLD or bundle build, installed-SDK relocation test, remote-worker execution,
production history plan, performance comparison or release was performed.
The command-mocked consumer tests do not prove a real standalone build passes.

No changes were made to dispat's source, including the adjacent development
worker checkout. No GitHub workflow was dispatched, and no commit, release tag,
remote branch or release asset was published.
