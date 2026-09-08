# Seed 580 review addendum

This addendum supersedes two overly strong statements in the separately hashed
`results/v181-20260907-seed580-review/README.md` without changing that evidence
directory.

- The same failure also occurs with the retained 1.8.0 runtime. This provides
  no evidence of a regression introduced by Dispat 1.8.1.
- The observed cause of the invalid sample is an intermittent Git read failure
  in freshly realized repositories under container `/tmp`. The underlying
  filesystem cause was not isolated.

The updated harness rejects a nonzero `dispat status` result before parsing it.
It writes raw stdout, stderr, return code, seed, generated instance, and a
post-failure `git fsck --no-dangling` result under
`failures-<profile>/seed<seed>/`. The result row has `invalid: true` and a
failure-dossier path, while `diffs` remains empty so execution failures cannot
be counted as semantic divergences. The summary adds an `invalid` count, and
`clean` excludes invalid rows. The runner exits nonzero after saving the result
if any execution is invalid, preventing a future campaign stage from being
marked complete.

The exact campaign runtime image was used for `run/e1-core-580-1.json`. That
narrow run completed with `clean: 1`, `invalid: 0`, and no divergence.
