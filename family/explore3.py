from common import *
import numpy as np, scipy.optimize as so, networkx as nx
A=sqs_dual(); Aset=set(A)
comp=[m for m in MASK if m not in Aset and all(pc(m&a)>=3 for a in A) and all(m&a&b for a,b in itertools.combinations(A,2))]
G=nx.Graph(); G.add_nodes_from(range(len(comp)))
for i,j in itertools.combinations(range(len(comp)),2):
    a,b=comp[i],comp[j]
    if pc(a&b)>=3 and all(a&b&x for x in A): G.add_edge(i,j)
# maximal 3-wise intersecting subfamilies: enumerate cliques then filter triples (recursive)
best=[]
def ext(cur,cands):
    if not cands:
        best.append(cur); return
    # simple branch: all maximal families
    v=cands[0]
    ok=[u for u in cands[1:] if G.has_edge(v,u) and all(comp[v]&comp[u]&comp[w] for w in cur)]
    ext(cur+[v],ok)
    # without v
    rest=cands[1:]
    # only branch if some maximality possible
    ext(cur,rest)
# too many maybe; instead enumerate maximal cliques and check triples
fams=set()
cnt=0
for cl in nx.find_cliques(G):
    cnt+=1
print('maximal cliques',cnt)
def is3(fam):
    return all(a&b&c for a,b,c in itertools.combinations(fam,3))
bad=0
for cl in nx.find_cliques(G):
    fam=[comp[i] for i in cl]
    if not is3(fam): bad+=1
print('cliques not 3-wise:',bad)
maxmass=0
for cl in nx.find_cliques(G):
    fam=A+[comp[i] for i in cl]
    M=np.array([[ (f>>j)&1 for f in fam] for j in range(14)],float)
    c=np.zeros(len(fam)); c[8:]=-1
    res=so.linprog(c,A_eq=np.vstack([M,np.ones(len(fam))]),b_eq=[.5]*14+[1],bounds=[(0,None)]*len(fam),method='highs')
    if res.status==0: maxmass=max(maxmass,-res.fun)
print('max mass off A over maximal cliques (pairwise+A-triples only):',maxmass)
print('--- 3-wise cliques only')
mm=0; ex=None
for cl in nx.find_cliques(G):
    fam0=[comp[i] for i in cl]
    if not is3(fam0): continue
    fam=A+fam0
    M=np.array([[ (f>>j)&1 for f in fam] for j in range(14)],float)
    c=np.zeros(len(fam)); c[8:]=-1
    res=so.linprog(c,A_eq=np.vstack([M,np.ones(len(fam))]),b_eq=[.5]*14+[1],bounds=[(0,None)]*len(fam),method='highs')
    if res.status==0 and -res.fun>mm: mm=-res.fun; ex=(fam,res.x)
print(mm)
if ex: 
    fam,x=ex
    for f,xx in zip(fam,x):
        if xx>1e-9: print(format(f,'014b'),round(xx,5))
