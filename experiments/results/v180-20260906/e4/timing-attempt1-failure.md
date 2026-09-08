# Timing attempt 1 (failed harness run)

This evidence was reconstructed from the captured terminal output after the
original `timing.csv` path was restarted. It is not a measured result file.

The run used `dispat-exp:runtime-v180`, `--cpus 2`, and `--memory 4g`. It
completed the first row:

```csv
P,shape,U,pad,edges,median_s,min_s,max_s,maxrss_mb
100,layered,200,0,185,0.046,0.042,0.078,0
```

The next cell failed during its 1,000-package warmup with subprocess exit
nonzero and empty captured stderr. The parent raised at `run_once`; no later
cell ran. Investigation established two harness defects: generated workspaces
were retained between cells, and RSS was divided by 1024 twice.
