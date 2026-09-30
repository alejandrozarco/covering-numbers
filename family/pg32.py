# Weighted blow-up of the 15 planes of PG(3,2): C(2m,m,3) <= 15 if exist integers w_P>=0, sum 2m,
# every point j of PG(3,2) has sum_{P ∋ j} w_P <= m.
import itertools, pulp
pts=list(range(1,16))  # nonzero vectors of F_2^4
planes=[frozenset(p for p in pts if bin(p&h).count('1')%2==0) for h in range(1,16)]
assert all(len(P)==7 for P in planes)
assert all(P&Q&R for P,Q,R in itertools.combinations(planes,3))
res={}
for m in range(3,41):
    prob=pulp.LpProblem('b',pulp.LpMinimize)
    w=[pulp.LpVariable(f'w{i}',0,None,cat='Integer') for i in range(15)]
    prob+=pulp.lpSum(w)
    prob+=pulp.lpSum(w)==2*m
    for j in pts: prob+=pulp.lpSum(w[i] for i,P in enumerate(planes) if j in P)<=m
    prob.solve(pulp.HiGHS(msg=0, threads=1))
    res[m]=pulp.LpStatus[prob.status]
    if res[m]=='Optimal': res[m]=[int(v.value()) for v in w]
print({m:(r if isinstance(r,str) else 'OK') for m,r in res.items()})
