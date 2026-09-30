#!/usr/bin/env python3
"""Weighted blow-up of the hyperplanes of PG(t,2): gives C(2m,m,t) <= 2^(t+1)-1 whenever there are integers
w_H >= 0 (H hyperplane), sum_H w_H = 2m, and every point p has sum_{H ∋ p} w_H <= m.
(Any t hyperplanes of PG(t,2) share a point; block_p = union of the classes of hyperplanes through p.)
Usage: pgblow.py t mmin mmax [outdir]"""
import sys, itertools, pulp, json, os
t, m0, m1 = map(int, sys.argv[1:4]); outdir = sys.argv[4] if len(sys.argv) > 4 else None
d = t + 1; pts = list(range(1, 2 ** d))
hyp = [frozenset(p for p in pts if bin(p & h).count('1') % 2 == 0) for h in pts]
res = {}
for m in range(m0, m1 + 1):
    prob = pulp.LpProblem('b', pulp.LpMinimize)
    w = [pulp.LpVariable(f'w{i}', 0, None, cat='Integer') for i in range(len(hyp))]
    prob += pulp.lpSum(w)
    prob += pulp.lpSum(w) == 2 * m
    for p in pts: prob += pulp.lpSum(w[i] for i, H in enumerate(hyp) if p in H) <= m
    prob.solve(pulp.HiGHS(msg=0, threads=1))
    st = pulp.LpStatus[prob.status]
    if st == 'Optimal':
        ws = [int(round(v.value())) for v in w]; res[m] = ws
        if outdir:
            # explicit covering: points = (hyperplane index, copy); blocks indexed by PG points
            P = [(i, c) for i, H in enumerate(hyp) for c in range(ws[i])]
            blocks = []
            for p in pts:
                B = [k for k, (i, c) in enumerate(P) if p in hyp[i]]
                extra = [k for k in range(len(P)) if k not in B][:m - len(B)]
                blocks.append(sorted(B + extra))
            os.makedirs(outdir, exist_ok=True)
            with open(f'{outdir}/C{2*m}_{m}_{t}_b{len(pts)}.txt', 'w') as f:
                f.write(f'# C({2*m},{m},{t}) <= {len(pts)}: PG({t},2) hyperplane blow-up, class sizes {ws}\n')
                for B in blocks: f.write(' '.join(map(str, B)) + '\n')
    else: res[m] = st
print({m: ('OK' if isinstance(v, list) else v) for m, v in res.items()})
