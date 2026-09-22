# Model of CCME admission under "consumer with own change proceeds".
# Linear history: commit index = time. tag[P] = commit index of P's newest release (None = unreleased).
# Units: (pkg, commit) each bumps pkg and propagates depth 1 to direct consumers (edge D -> P).
import random, itertools
random.seed(11)
def plan(pkgs, edges, units, tag, rule, ptags):
    """returns {D: set of (P,c) contributions admitted} incl. direct as (D,c)."""
    cons={D:set() for D in pkgs}
    for (P,c) in units:
        if tag[P] is None or c>tag[P]: cons[P].add((P,c))          # direct, C in Wfresh(P)
        for (D,Q) in edges:
            if Q!=P: continue
            if rule=='old':
                adm = tag[D] is None or c>tag[D]                        # C in Wfresh(D)
            else:
                # discharged iff some release of P at or after c is at or before D's release
                adm = not any(c<=t<=(tag[D] if tag[D] is not None else -1) for t in ptags[P])
            if adm: cons[D].add((P,c))
    return {D:s for D,s in cons.items() if s}
def run(pkgs, edges, units, tag, ptags, declared, rule, fail, now):
    pl=plan(pkgs,edges,units,tag,rule,ptags)
    order=[]; seen=set()
    def visit(x):
        if x in seen: return
        seen.add(x)
        for (D,Q) in edges:
            if D==x: visit(Q)
        order.append(x)
    for x in sorted(pkgs): visit(x)
    published=set(); failed=set(); blocked=set()
    for D in order:
        if D not in pl: continue
        provs={Q for (X,Q) in edges if X==D}
        bad={Q for Q in provs if Q in failed|blocked}
        own = any(P==D for (P,c) in pl[D]) or any(P in published for (P,c) in pl[D])
        if bad and not own: blocked.add(D); continue
        if D in fail: failed.add(D); continue
        published.add(D); tag[D]=now; ptags[D].append(now)
        for Q in provs: declared[D][Q]=tag[Q]        # manifest names Q's PUBLISHED position
    return pl, published, failed, blocked
def orphans(pkgs, edges, units, tag, declared):
    out=[]
    for (D,Q) in edges:
        for (P,c) in units:
            if P==Q and tag[Q] is not None and c<=tag[Q] and tag[D] is not None and declared[D].get(Q)!=tag[Q]:
                out.append((D,Q,c))
    return out
def trial(rule):
    n=random.randint(2,5); pkgs=[chr(97+i) for i in range(n)]
    edges=[(pkgs[i],pkgs[j]) for i in range(n) for j in range(i) if random.random()<0.5]
    tag={p:None for p in pkgs}; ptags={p:[] for p in pkgs}; declared={p:{} for p in pkgs}
    units=[]; now=0; releases=0; plans=[]
    for step in range(5):
        now+=1; units.append((random.choice(pkgs),now))
        now+=1; fail={p for p in pkgs if random.random()<0.35}
        pl,pub,f,b=run(pkgs,edges,units,tag,ptags,declared,rule,fail,now); releases+=len(pub); plans.append(pl)
    for _ in range(n+3):
        now+=1; pl,pub,f,b=run(pkgs,edges,units,tag,ptags,declared,rule,set(),now); releases+=len(pub); plans.append(pl)
    now+=1; final=plan(pkgs,edges,units,tag,rule,ptags)
    return orphans(pkgs,edges,units,tag,declared), final, releases, (pkgs,edges,units)
bad_old=0; bad_new=0; nonconv_new=0; extra=0; N=3000
for _ in range(N):
    st=random.getstate()
    o_old,f_old,r_old,_=trial('old'); random.setstate(st)
    o_new,f_new,r_new,case=trial('new')
    bad_old+=bool(o_old); bad_new+=bool(o_new); nonconv_new+=bool(f_new); extra+=r_new-r_old
print("trials",N)
print("old rule: histories ending with an orphaned consumer (declares a stale provider though a unit propagated):",bad_old)
print("new rule: orphaned consumers:",bad_new,"| non-empty plan after failure-free runs:",nonconv_new,"| extra releases total:",extra)
# minimal example, spelled out
pkgs=['a','b']; edges=[('b','a')]   # b consumes a
for rule in ('old','new'):
    tag={'a':None,'b':None}; ptags={'a':[],'b':[]}; declared={'a':{},'b':{}}
    units=[('a',1),('b',1)]          # C: feat(a)^ and feat(b) at commit 1
    log=[]
    for now,fail in ((2,{'a'}),(3,set()),(4,set())):
        pl,pub,f,b=run(pkgs,edges,units,tag,ptags,declared,rule,fail,now)
        log.append(f"run@{now}: plan={sorted(pl)} published={sorted(pub)} failed={sorted(f)} blocked={sorted(b)} b declares a@{declared['b'].get('a')}")
    print(rule,"|",' ; '.join(log),"| a's tag:",tag['a'])
