import itertools, random
from collections import deque
def bfs(adj, s):
    d={s:0}; q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if v not in d: d[v]=d[u]+1; q.append(v)
    return d
def diam(adj, nodes):
    return max(max(bfs(adj,u).values()) for u in nodes)
def comps(n, edges):
    adj={i:set() for i in range(n)}
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    seen=set(); out=[]
    for i in range(n):
        if i in seen: continue
        c=sorted(bfs(adj,i)); seen|=set(c); out.append(c)
    return adj,out
def center(adj, comp):
    ecc={u:max(bfs(adj,u).values()) for u in comp}
    r=min(ecc.values())
    return min(u for u in comp if ecc[u]==r), r     # least name among centres
def is_tree(n, edges):
    adj,cs=comps(n,edges); return len(cs)==1 and len(edges)==n-1
def brute(n, edges):
    adj,cs=comps(n,edges); need=len(cs)-1
    cand=[(a,b) for a in range(n) for b in range(a+1,n) if (a,b) not in edges]
    best=None
    for extra in itertools.combinations(cand, need):
        e=set(edges)|set(extra)
        if is_tree(n,e):
            a,_=comps(n,e); d=diam(a,range(n))
            best=d if best is None else min(best,d)
    return best
def centre_join(n, edges):
    adj,cs=comps(n,edges)
    cr=[center(adj,c) for c in cs]
    # hub: largest radius, tie least centre name
    hub=max(cr,key=lambda t:(t[1],-t[0]))
    e=set(edges)
    for c,r in cr:
        if c!=hub[0]: e.add((min(c,hub[0]),max(c,hub[0])))
    a,_=comps(n,e)
    rs=sorted((r for _,r in cr),reverse=True)+[ -10,-10]
    dmax=max(diam(adj,c) for c in cs)
    formula=max(dmax, rs[0]+rs[1]+1 if len(cr)>1 else 0, rs[1]+rs[2]+2 if len(cr)>2 else 0)
    return diam(a,range(n)), formula
def kruskal_name(n, edges):
    adj,cs=comps(n,edges); parent=list(range(n))
    def f(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    for a,b in edges: parent[f(b)]=f(a)
    e=set(edges)
    for i in range(n):
        for j in range(i+1,n):
            if f(i)!=f(j): parent[f(j)]=f(i); e.add((i,j))
    a,_=comps(n,e); return diam(a,range(n))
random.seed(7); worse=0; trials=0; maxgap=0
for _ in range(1500):
    n=random.randint(2,7)
    # random forest with random labels
    perm=list(range(n)); random.shuffle(perm); edges=set(); parent=list(range(n))
    def f(x):
        while parent[x]!=x: x=parent[x]
        return x
    for _ in range(random.randint(0,n-1)):
        a,b=random.sample(range(n),2)
        if f(a)!=f(b): parent[f(b)]=f(a); edges.add((min(a,b),max(a,b)))
    b=brute(n,edges); cj,fo=centre_join(n,edges); k=kruskal_name(n,edges)
    assert cj==b==fo,(n,edges,b,cj,fo)
    trials+=1
    if k>b: worse+=1; maxgap=max(maxgap,k-b)
print("centre-join == brute-force optimum == formula on",trials,"forests; name-order Kruskal worse on",worse,"max gap",maxgap)
# two chains of 5
edges={(0,1),(1,2),(2,3),(3,4),(5,6),(6,7),(7,8),(8,9)}
print("two 5-chains: kruskal",kruskal_name(10,edges),"centre-join",centre_join(10,edges))
