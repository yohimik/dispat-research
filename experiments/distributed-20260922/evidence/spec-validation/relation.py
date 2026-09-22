import random, itertools
INF=10**9
def tasks(n, edges, rel, b, p, serial_publish=False):
    # task ids: ('B',i), ('P',i); edges: list of (c, prov); rel[(c,prov)] in {'independent','output','published'}
    pre={('B',i):set() for i in range(n)}; pre.update({('P',i):{('B',i)} for i in range(n)})
    for (c,pv) in edges:
        pre[('P',c)].add(('P',pv))
        r=rel[(c,pv)]
        if r=='output': pre[('B',c)].add(('B',pv))
        if r=='published': pre[('B',c)].add(('P',pv))
    if serial_publish:
        for i in range(1,n): pre[('P',i)].add(('P',i-1))   # plan order = index order (providers have lower index)
    dur={('B',i):b[i] for i in range(n)}; dur.update({('P',i):p[i] for i in range(n)})
    return pre,dur
def longest(pre,dur):
    memo={}
    def end(t):
        if t not in memo: memo[t]=dur[t]+max([end(q) for q in pre[t]],default=0)
        return memo[t]
    return max(end(t) for t in pre)
def greedy(pre,dur,mb,mp):
    # list scheduling, priority = (package index, stage), typed pools
    t=0; done={}; running=[]; free={'B':mb,'P':mp}; pending=sorted(pre, key=lambda x:(x[1],x[0]))
    while pending or running:
        started=True
        while started:
            started=False
            for x in list(pending):
                if free[x[0]]>0 and all(q in done and done[q]<=t for q in pre[x]):
                    free[x[0]]-=1; running.append((t+dur[x],x)); pending.remove(x); started=True
        running.sort(); t,x=running.pop(0); done[x]=t; free[x[0]]+=1
        while running and running[0][0]==t:
            _,y=running.pop(0); done[y]=t; free[y[0]]+=1
    return max(done.values())
random.seed(3)
# 1. chain formulas
for _ in range(300):
    n=random.randint(1,6); b=[random.randint(1,9) for _ in range(n)]; p=[random.randint(1,9) for _ in range(n)]
    edges=[(i,i-1) for i in range(1,n)]
    for r,f in (('published',lambda: sum(b)+sum(p)),
                ('output',lambda: max(sum(b[:k+1])+sum(p[k:]) for k in range(n))),
                ('independent',lambda: max(b[k]+sum(p[k:]) for k in range(n)))):
        pre,dur=tasks(n,edges,{e:r for e in edges},b,p); assert longest(pre,dur)==f(),(r,b,p)
# 2. fan-out / fan-in formulas
for _ in range(300):
    m=random.randint(1,5); b=[random.randint(1,9) for _ in range(m+1)]; p=[random.randint(1,9) for _ in range(m+1)]
    eo=[(i,0) for i in range(1,m+1)]
    exp={'published':b[0]+p[0]+max(b[i]+p[i] for i in range(1,m+1)),
         'output':b[0]+max(max(b[i],p[0])+p[i] for i in range(1,m+1)),
         'independent':max(max(b[i],b[0]+p[0])+p[i] for i in range(1,m+1))}
    for r in exp:
        pre,dur=tasks(m+1,eo,{e:r for e in eo},b,p); assert longest(pre,dur)==exp[r],(r,'fanout')
    c=m; ei=[(c,i) for i in range(m)]   # consumer is index m, providers 0..m-1
    exp={'published':max(b[i]+p[i] for i in range(m))+b[c]+p[c],
         'output':max(max(b[i] for i in range(m))+b[c], max(b[i]+p[i] for i in range(m)))+p[c],
         'independent':max(b[c], max(b[i]+p[i] for i in range(m)))+p[c]}
    for r in exp:
        pre,dur=tasks(m+1,ei,{e:r for e in ei},b,p); assert longest(pre,dur)==exp[r],(r,'fanin')
# 3. monotone under unlimited slots; typed-pool bound; anomaly search under budgets
order={'independent':0,'output':1,'published':2}; anomalies=[]; worst=0
for _ in range(4000):
    n=random.randint(2,6); b=[random.randint(1,9) for _ in range(n)]; p=[random.randint(1,9) for _ in range(n)]
    edges=[(c,pv) for c in range(n) for pv in range(c) if random.random()<0.4]
    mb=random.randint(1,3); mp=random.randint(1,3); res={}
    for r in order:
        pre,dur=tasks(n,edges,{e:r for e in edges},b,p)
        L=longest(pre,dur); g=greedy(pre,dur,mb,mp); res[r]=(L,g)
        bound=L+sum(b)/mb+sum(p)/mp; assert g<=bound+1e-9
        lower=max(L,sum(b)/mb,sum(p)/mp); worst=max(worst,g/lower)
    assert res['independent'][0]<=res['output'][0]<=res['published'][0]
    if res['independent'][1]>res['output'][1]: anomalies.append((n,b,p,edges,mb,mp,res))
print("chain, fan-out, fan-in formulas verified; unlimited-slot makespan monotone; greedy <= L + Wb/mb + Wp/mp always")
print("worst greedy/lower-bound ratio seen: %.3f"%worst)
print("greedy anomalies (independent slower than output under budgets):",len(anomalies),"of 4000")
if anomalies:
    a=min(anomalies,key=lambda x:(x[0],sum(x[1])+sum(x[2]))); print("smallest:",a)
# 4. serial publication lane
for _ in range(300):
    n=random.randint(1,6); b=[random.randint(1,9) for _ in range(n)]; p=[random.randint(1,9) for _ in range(n)]
    edges=[(c,pv) for c in range(n) for pv in range(c) if random.random()<0.4]
    pre,dur=tasks(n,edges,{e:'independent' for e in edges},b,p,serial_publish=True)
    assert longest(pre,dur)==max(b[k]+sum(p[k:]) for k in range(n))
print("single publication lane, independent: makespan = max_k(b_k + sum_{j>=k} p_j) verified")
# 5. worked example: terraform -> backend -> frontend ; frontend also -> terraform
b=[2,6,8]; p=[10,3,2]; edges=[(1,0),(2,0),(2,1)]
for name,rel in (('all published',{e:'published' for e in edges}),('all output',{e:'output' for e in edges}),
                 ('terraform edges independent, backend->frontend output',{(1,0):'independent',(2,0):'independent',(2,1):'output'}),
                 ('all independent',{e:'independent' for e in edges})):
    pre,dur=tasks(3,edges,rel,b,p); print("%-55s makespan %2d  (single lane: %2d)"%(name,longest(pre,dur),longest(*tasks(3,edges,rel,b,p,True))))
