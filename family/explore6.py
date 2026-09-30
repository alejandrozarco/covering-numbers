from common import *
import numpy as np, scipy.optimize as so, random, sys
exec(open('explore5.py').read().split('found=0')[0])
random.seed(5)
def sqs_in(fam):
    # all SQS duals inside fam
    out=[]
    import networkx as nx
    G=nx.Graph(); G.add_nodes_from(range(len(fam)))
    for i,j in itertools.combinations(range(len(fam)),2):
        if pc(fam[i]&fam[j])==3: G.add_edge(i,j)
    for cl in nx.enumerate_all_cliques(G):
        if len(cl)==8: out.append(tuple(cl))
    return out
for trial in range(60):
    fam=[]; cand=list(MASK); random.shuffle(cand); cnt=[0]*14
    while True:
        cand=[c for c in cand if all(pc(c&f)>=3 for f in fam) and all(c&f&g for f,g in itertools.combinations(fam,2))]
        if not cand: break
        sc=lambda c: sum(cnt[j] for j in range(14) if (c>>j)&1)+random.random()*3
        c=min(cand[:400],key=sc); fam.append(c); cand.remove(c)
        for j in range(14):
            if (c>>j)&1: cnt[j]+=1
    if balanced(fam).status!=0: continue
    sq=sqs_in(fam)
    inany=set(i for s in sq for i in s)
    print('family',len(fam),'#SQS inside',len(sq),'sets in some SQS',len(inany), 'pairwise overlaps of SQS', sorted(set(len(set(a)&set(b)) for a,b in itertools.combinations(sq,2))))
