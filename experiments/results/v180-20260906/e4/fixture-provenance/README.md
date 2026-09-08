# Fixture provenance verification

Run on 2026-09-06 with image
`dispat-exp:runtime-v180` (`sha256:d4a42648510d6f1f9e750c4fac1ffad03686967bfa7b3b51676e2f8e714df222`),
2 CPUs and 4 GiB:

```sh
docker run --rm --cpus 2 --memory 4g \
  -v "$PWD":/exp:ro -v "$PWD/results/v180-20260906/e4/fixture-provenance":/results \
  -w /exp dispat-exp:runtime-v180 \
  bash e4/verify_fixture_provenance.sh /results
```

The script path and the source files it invokes are hashed in
`source-sha256.txt`; raw generation, refs, logs, `fsck` streams and exit codes
are retained here. `verdict.txt` is the compact result. Empty `fsck` streams
with exit `0` are Git's successful output.

The files named `u1000-fsck.*` came from the first interrupted provenance run,
which used an ordinary U1000 fixture and exited after that fixture failed
`fsck`. They remain immutable evidence. The completed rerun uses the explicit
names `u1000-normal-fsck.*` and `u1000-commit-tree-fsck.*`; both exit `0` and
their deterministic HEAD IDs match.

This reconstruction proves the generator equivalence and validates freshly
regenerated deterministic U1000 and pad5000 fixtures. It does not create
retrospective `fsck` evidence for the first six already-cleaned timing
fixtures. The timing runner itself checked the exact final U1000 and pad5000
fixtures immediately before measurement, but their successful empty streams
were not retained.
