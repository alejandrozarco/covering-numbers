#!/usr/bin/env python3
"""Direct CNF for C(2m,m,3) <= b  (default b=14) in dual form.
Rows i=0..2m-1 (covering points), columns j=0..b-1 (blocks); x[i][j] = point i in block j.
Constraints: row sums = r (=7 for b=14), column sums = m (block size m), every triple of rows has a
common column.  Optional: pairwise row intersections >= lam (implied for b=14, m>=5: lam=3).
Symmetry: double-lex (rows non-increasing lex, columns non-increasing lex) -- sound for full
row x column symmetry of the model (all constraints invariant under both permutation groups).
Usage: gen_direct.py m out.cnf [--b 14] [--r 7] [--nolam] [--nolex]"""
import sys, itertools, argparse
sys.path.insert(0, '../scripts')
from cnflib import CNF
ap = argparse.ArgumentParser()
ap.add_argument('m', type=int); ap.add_argument('out')
ap.add_argument('--b', type=int, default=14); ap.add_argument('--r', type=int, default=7)
ap.add_argument('--rmin', type=int, default=None, help='row sum >= rmin instead of == r')
ap.add_argument('--cmax', action='store_true', help='column sums <= m instead of == m')
ap.add_argument('--lam', type=int, default=3); ap.add_argument('--nolam', action='store_true')
ap.add_argument('--nolex', action='store_true')
ap.add_argument('--tri', default=None, help='t1|t2: rows 0,1,2 = a triangle (pairwise |∩|=3) with |S0∩S1∩S2| = 1 resp. 2; for t2 additionally NO triangle with triple intersection 1 exists');
ap.add_argument('--pair', action='store_true', help='fix row0={0..6}, row1={0,1,2,7,8,9,10}; lex on rows>=2, columns lex within blocks (b=14 only)')
a = ap.parse_args()
m, b = a.m, a.b; n = 2 * m
F = CNF()
x = [[F.new() for j in range(b)] for i in range(n)]
for i in range(n):
    if a.rmin is None: F.exactly(x[i], a.r)
    else: F.atleast(x[i], a.rmin)
for j in range(b):
    col = [x[i][j] for i in range(n)]
    if a.cmax: F.atmost(col, m)
    else: F.exactly(col, m)
# pair ands
y = {}; C4 = {}
for i, k in itertools.combinations(range(n), 2):
    y[i, k] = [F.and_def([x[i][j], x[k][j]]) for j in range(b)]
    if not a.nolam:
        if a.tri:   # needs the '>= lam+1' indicator
            cnt = F._counter(y[i, k], a.lam + 1); F._assert_true(cnt[a.lam]); C4[i, k] = cnt[a.lam + 1]
        else:       # encoding used for the stored certificates proofs/direct_m*.cnf
            F.atleast(y[i, k], a.lam)
for i, k, l in itertools.combinations(range(n), 3):
    zs = []
    for j in range(b):
        z = F.new(); F.add([-z, y[i, k][j]]); F.add([-z, x[l][j]]); zs.append(z)
    F.add(zs)
if a.tri:
    assert b == 14 and a.r == 7 and a.rmin is None and not a.nolam
    from cases import CASES
    cs = CASES[a.tri]; fx = cs['rows']
    for i, r in enumerate(fx):
        for j in range(b): F.add([x[i][j] if r[j] else -x[i][j]])
    for i in range(len(fx), n - 1): F.lex_geq(x[i], x[i + 1])
    for blk in cs['blocks']:
        for j, j2 in zip(blk, blk[1:]):
            F.lex_geq([x[i][j] for i in range(len(fx), n)], [x[i][j2] for i in range(len(fx), n)])
    if a.tri == 't2':
        for i, k, l in itertools.combinations(range(n), 3):
            ts = [F.and_def([y[i, k][j], x[l][j]]) for j in range(b)]
            ct = F._counter(ts, 2)
            F.add([C4[i, k], C4[i, l], C4[k, l], ct[2]])
elif a.pair:
    assert b == 14 and a.r == 7 and a.rmin is None
    r0 = [1]*7 + [0]*7; r1 = [1,1,1,0,0,0,0,1,1,1,1,0,0,0]
    for j in range(b):
        F.add([x[0][j] if r0[j] else -x[0][j]]); F.add([x[1][j] if r1[j] else -x[1][j]])
    for i in range(2, n - 1):
        F.lex_geq(x[i], x[i + 1])
    for blk in (range(0,3), range(3,7), range(7,11), range(11,14)):
        blk = list(blk)
        for j, j2 in zip(blk, blk[1:]):
            F.lex_geq([x[i][j] for i in range(2, n)], [x[i][j2] for i in range(2, n)])
elif not a.nolex:
    for i in range(n - 1):
        F.lex_geq(x[i], x[i + 1])
    for j in range(b - 1):
        F.lex_geq([x[i][j] for i in range(n)], [x[i][j + 1] for i in range(n)])
F.write(a.out, [f'C(2m,m,3)<= {b}, m={m} dual direct encoding', ' '.join(sys.argv)])
print(F.nv, len(F.clauses))
