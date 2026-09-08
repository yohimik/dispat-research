# P=1000, layered, U=200, pad=5000

The first attempt failed its warmup because the generated repository had a
missing parent object. A single bounded retry spent more than five minutes in
fixture generation and was interrupted so the finite E1 and E4 recovery
repetitions could complete. A later `commit-tree` fixture, validated for exact
equivalence on a small case and checked with `git fsck` at full size, produced
the valid fresh row in `timing-cell7-valid-retry.csv`; no historical value was
used.
