# The worked example quoted to the docs (terraform 4/6, backend 9/3, frontend 12/2 minutes): 36 / 27 / 15 unlimited,
# and 27 / 18 / 15 under build budgets 1 / 2 / 3 with one publish slot. Uses relation.py's model unchanged.
import importlib.util, io, contextlib
spec=importlib.util.spec_from_file_location("rel","relation.py"); m=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(m)
b=[4,9,12]; p=[6,3,2]; edges=[(1,0),(2,0),(2,1)]   # 0 terraform, 1 backend, 2 frontend
for name in ('published','output','independent'):   # relation.py's names for publish / build / none
    rel={e:name for e in edges}; pre,dur=m.tasks(3,edges,rel,b,p)
    row=[m.longest(pre,dur)]+[m.greedy(pre,dur,mb,1) for mb in (1,2,3)]
    print("%-12s unlimited %2d | build budget 1: %2d, 2: %2d, 3: %2d (one publish slot)"%(name,*row))
