from common import *
import numpy as np, scipy.optimize as so, networkx as nx, random
A=sqs_dual(); Aset=set(A)
comp=[m for m in MASK if m not in Aset and all(pc(m&a)>=3 for a in A) and all(m&a&b for a,b in itertools.combinations(A,2))]
G=nx.Graph(); G.add_nodes_from(range(len(comp)))
for i,j in itertools.combinations(range(len(comp)),2):
    a,b=comp[i],comp[j]
    if pc(a&b)>=3 and all(a&b&x for x in A): G.add_edge(i,j)
def is3(fam): return all(a&b&c for a,b,c in itertools.combinations(fam,3))
def issqs(fam): return len(fam)==8 and all(pc(a&b)==3 for a,b in itertools.combinations(fam,2))
random.seed(1)
nf=0; nonsqs=0; sizes={}
for cl in nx.find_cliques(G):
    fam0=[comp[i] for i in cl]
    if not is3(fam0): continue
    nf+=1
    fam=A+fam0
    M=np.array([[ (f>>j)&1 for f in fam] for j in range(14)],float)
    Aeq=np.vstack([M,np.ones(len(fam))]); beq=[.5]*14+[1]
    for t in range(30):
        c=np.random.randn(len(fam))
        res=so.linprog(c,A_eq=Aeq,b_eq=beq,bounds=[(0,None)]*len(fam),method='highs-ds')
        sup=[fam[i] for i in range(len(fam)) if res.x[i]>1e-9]
        sizes[len(sup)]=sizes.get(len(sup),0)+1
        if not issqs(sup): nonsqs+=1
print(nf,'families; vertex support sizes',sizes,'non-SQS vertices',nonsqs)
