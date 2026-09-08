# Timing attempt 3 (five valid cells, then generator failure)

The first five rows remain in `timing.csv`. Before the sixth cell could warm
up, Dispat's Git traversal exited 128 because a generated commit's parent
object could not be read. The raw diagnostic named missing object
`85a751c92ec8aecca5e9a412846cb80029d6b504` and commit
`df95b366da8af91975ef9c95d349acdf195f037f`.

The failed fixture had already been removed by the runner's cleanup path, so
its object database could not be checked independently. Background Git
auto-maintenance was a suspected cause and the generator now disables
`gc.auto`, but that is not a proved diagnosis. A regenerated star fixture
passed `git fsck --full` and one status run; the complete cell still requires a
successful rerun. The three unmeasured cells are retained as per-cell CSV
files before assembly, so a later failure cannot erase a completed cell.
