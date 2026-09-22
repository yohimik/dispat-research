# The corrected orphan check behind the "4000 histories, 247 orphans under the window rule, 0 under delivery"
# figures. proceed.py's own check counted a consumer as orphaned whenever it declared anything but the provider's
# NEWEST release; CCME propagation does not cascade (SPEC.md section 9.2), so a consumer is owed only the first
# provider release that carries a unit propagating to it. Same model and seed as proceed.py otherwise.
import random, importlib.util, io, contextlib
spec=importlib.util.spec_from_file_location("m","proceed.py"); m=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(m)
def orphans(pkgs, edges, units, tag, declared, ptags):
    out=[]
    for (D,Q) in edges:
        for (P,c) in units:
            if P!=Q or tag[D] is None: continue
            past=[t for t in ptags[Q] if t>=c]
            if not past: continue                      # Q never released that unit: nothing owed yet
            if declared[D].get(Q) is None or declared[D][Q]<past[0]: out.append((D,Q,c))
    return out
N=4000; res={}
for rule in ('old','new'):
    random.seed(11); bad=0; nonconv=0; rel=0
    for _ in range(N):
        n=random.randint(2,5); pkgs=[chr(97+i) for i in range(n)]
        edges=[(pkgs[i],pkgs[j]) for i in range(n) for j in range(i) if random.random()<0.5]
        tag={p:None for p in pkgs}; ptags={p:[] for p in pkgs}; declared={p:{} for p in pkgs}; units=[]; now=0
        for step in range(5):
            now+=1; units.append((random.choice(pkgs),now)); now+=1; fail={p for p in pkgs if random.random()<0.35}
            pl,pub,f,b=m.run(pkgs,edges,units,tag,ptags,declared,rule,fail,now); rel+=len(pub)
        for _ in range(n+3):
            now+=1; pl,pub,f,b=m.run(pkgs,edges,units,tag,ptags,declared,rule,set(),now); rel+=len(pub)
        now+=1; final=m.plan(pkgs,edges,units,tag,rule,ptags)
        bad+=bool(orphans(pkgs,edges,units,tag,declared,ptags)); nonconv+=bool(final)
    res[rule]=(bad,nonconv,rel)
print("rule  orphaned-histories  nonconverged  total-releases  (N=%d, seed 11)"%N)
for r,(b,c,l) in res.items(): print("%-5s %8d %14d %14d"%(r,b,c,l))
print("extra releases under delivery: %.2f%%"%(100.0*(res['new'][2]-res['old'][2])/res['old'][2]))
print("CAVEAT: the model parses every unit; it does not model the section 13.3 window restriction, whose gap was found later.")
