from common import *
import numpy as np, scipy.optimize as so, networkx as nx
A=sqs_dual(); Aset=set(A)
comp=[m for m in MASK if m not in Aset and all(pc(m&a)>=3 for a in A) and all(m&a&b for a,b in itertools.combinations(A,2))]
fam=A+comp
M=np.array([[ (f>>j)&1 for f in fam] for j in range(14)],float)
c=np.zeros(len(fam)); c[8:]=-1
res=so.linprog(c,A_eq=np.vstack([M,np.ones(len(fam))]),b_eq=[.5]*14+[1],bounds=[(0,None)]*len(fam),method='highs')
print('max mass on compatible sets (ignoring their mutual compat):',-res.fun)
# compatibility among comp
G=nx.Graph(); G.add_nodes_from(range(len(comp)))
for i,j in itertools.combinations(range(len(comp)),2):
    a,b=comp[i],comp[j]
    if pc(a&b)>=3 and all(a&b&x for x in A): G.add_edge(i,j)
print('edges',G.number_of_edges(), 'max clique', max(len(c) for c in nx.find_cliques(G)))
