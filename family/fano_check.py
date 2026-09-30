# (1) intersecting 3-graphs on 7 points with covering number 3 are exactly Fano planes
# (2) 8 distinct 7-subsets of [14], pairwise |∩|=3, 3-wise intersecting  <=> SQS(8)-dual (checked by argument; here sanity)
import itertools
T=list(itertools.combinations(range(7),3))
def inter(a,b): return bool(set(a)&set(b))
# maximal intersecting 3-graphs: enumerate all intersecting families via cliques
import networkx as nx
G=nx.Graph(); G.add_nodes_from(range(len(T)))
for i,j in itertools.combinations(range(len(T)),2):
    if inter(T[i],T[j]): G.add_edge(i,j)
cnt=0; fano=0
def tau(fam):
    for k in (1,2):
        for C in itertools.combinations(range(7),k):
            if all(set(C)&set(T[f]) for f in fam): return k
    return 3
for cl in nx.find_cliques(G):
    if tau(cl)==3:
        cnt+=1
        # every tau=3 subfamily: minimal ones; check the maximal clique itself is a Fano plane
        pts=[sum(1 for f in cl if p in T[f]) for p in range(7)]
        if len(cl)==7 and all(len(set(T[a])&set(T[b]))==1 for a,b in itertools.combinations(cl,2)): fano+=1
print('maximal intersecting 3-graphs on [7] with tau=3:',cnt,' of which Fano planes:',fano)
