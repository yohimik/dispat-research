# Historical paper sources

`paper/saner/` is the only active conference manuscript. The full English technical report remains separately at `paper/main.tex`.

- `icse-2026-09-10.tar.gz` preserves the complete obsolete `paper/icse/` tree: source, notes and its saved build. Its 11 files were extracted and checked byte-for-byte before the working tree was removed. The adjacent JSON records paths, hashes and source revision. Archive SHA-256: `0dfea625dc7d79d776c19872b030095bfe9291c8421f82479a2c408ea0dd0fd1`.
- `saner-comparison-2026-09-10.tex` is an unused historical fragment removed from the active manuscript directory. It was not included in the paper build.

To inspect or replay the old ICSE draft, first verify the archive checksum against the JSON, then extract into an empty directory:

```sh
mkdir /tmp/dispat-icse-review
tar -xzf paper/archives/icse-2026-09-10.tar.gz -C /tmp/dispat-icse-review
```

Extraction recreates `paper/icse/` under that directory. For historical scripts that require the repository layout, restore it in a disposable checkout. Original evidence paths are retained as recorded. This archive is historical and does not represent an active submission.
