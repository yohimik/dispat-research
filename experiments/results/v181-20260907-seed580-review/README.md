# E1 core seed 580 investigation

Disposition: **invalid harness/infrastructure sample; no evidence of a Dispat
1.8.1 regression**.

This directory is new evidence. The completed campaign at
`results/v181-20260907` was not modified. `campaign.identity`, `image-ids.sh`,
and `runtime-image-id.txt` bind the reproduction to the completed campaign and
its recorded runtime image
`sha256:da722d8c6b6fd13010bf1bd5980d1ee940adff5bee160238d892dc3ca42830f1`,
which contains the published 1.8.1 image pinned by the campaign identity.

## Findings

- The original dossier has `"dispat": {}` and seven UNKNOWN rows: every
  package for which the oracle expected a release. This shape is an empty
  parse, not a conflicting release plan.
- A narrow `e1/run.py` reproduction in `repro-runpy/` reproduced that shape.
- Raw repetitions show that freshly realized repositories under container
  `/tmp` intermittently fail Git reads. Failures return exit code 1 and a
  single JSON error such as `option 'merged' must point to a commit` or
  `Could not read <object>; Failed to traverse parents`. The 1.8.1 immediate
  sample failed 4/30 times (`raw/variant-summary.json`).
- `git fsck --no-dangling`, run before Dispat, independently failed on 7/30
  newly realized repositories. Its failures corresponded to the same 7/30
  Dispat failures. The fixture repository can therefore be unreadable before
  the binary under test starts planning.
- The retained 1.8.0 runtime showed the same behavior today: 8/30 immediate
  runs failed and parsed empty (`raw/v180-immediate-summary.json`). This rules
  out a behavior introduced by 1.8.1.
- When the repository is readable, five consecutive 1.8.1 invocations return
  exit code 0, all 14 plan rows, and no stderr (`raw/runs.json`). The harness's
  own comparison reports no differences (`comparison.txt`).

No timeout occurred: successful calls took about 19--20 ms in the bind-backed
preserved workspace, and failing `/tmp` calls returned in roughly 2--4 ms.
The failure is nondeterministic visibility/readability of freshly written Git
objects in the container's ephemeral filesystem.

## Harness issue and proposed fix

`e1/run.py::dispat_plan` discards the subprocess return code and feeds error
output to the plan parser. A CLI failure consequently becomes `{}` and is
reported as semantic UNKNOWN divergences. The harness should first require
return code zero and preserve stdout/stderr, seed, and worktree diagnostics as
an infrastructure failure. It should also validate a freshly realized repo
before running Dispat and either place fixtures on a reliable mounted
filesystem or retry realization after an integrity failure. Such retries must
be classified separately from oracle comparisons.

No parser/runtime source was changed, and no commit or push was made.
