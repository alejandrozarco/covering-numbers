# random greedy search for maximal 3-wise intersecting families (pairwise>=3) that admit a balanced distribution
from common import *
import numpy as np, scipy.optimize as so, random, sys
random.seed(int(sys.argv[1]) if len(sys.argv)>1 else 0)
def balanced(fam):
    M=np.array([[ (f>>j)&1 for f in fam] for j in range(14)],float)
    res=so.linprog(np.random.rand(len(fam)),A_eq=np.vstack([M,np.ones(len(fam))]),b_eq=[.5]*14+[1],bounds=[(0,None)]*len(fam),method='highs-ds')
    return res
def issqs(fam): return len(fam)==8 and all(pc(a&b)==3 for a,b in itertools.combinations(fam,2))
found=0
for trial in range(int(sys.argv[2]) if len(sys.argv)>2 else 200):
    fam=[]; cand=list(MASK); random.shuffle(cand)
    cnt=[0]*14
    while True:
        # compatible candidates
        cand=[c for c in cand if all(pc(c&f)>=3 for f in fam) and all(c&f&g for f,g in itertools.combinations(fam,2))]
        if not cand: break
        # prefer sets covering low-count elements
        sc=lambda c: sum(cnt[j] for j in range(14) if (c>>j)&1)+random.random()*3
        c=min(cand[:400],key=sc)
        fam.append(c); cand.remove(c)
        for j in range(14):
            if (c>>j)&1: cnt[j]+=1
    res=balanced(fam)
    if res.status==0:
        found+=1
        sup=[fam[i] for i in range(len(fam)) if res.x[i]>1e-9]
        print('trial',trial,'family size',len(fam),'balanced; vertex support',len(sup),'sqs' if issqs(sup) else 'NON-SQS',flush=True)
print('found',found)
