#!/usr/bin/env python3
"""CEGAR search for a counterexample to the Key Lemma:
   a family F' of s distinct 7-subsets of [14], pairwise |S∩T|>=3, 3-wise intersecting,
   containing no 8 members with all pairwise intersections exactly 3 (= no SQS(8)-dual),
   with (1/2)1 in conv(F') (balanced).
SAT model: rows = sets (strictly lex-decreasing), columns lex non-increasing (double lex).
Balance is replaced by valid Farkas cuts: for y>=0 integer, "some row has y(S) <= y([14])/2".
Initial cuts: y = 1_W for all W with |W| <= K (both W and complement direction).
Loop: SAT -> LP check; balanced => counterexample; else add Farkas cut from the LP dual.
Usage: keylemma.py s [--K 5] [--out final.cnf] [--cuts cuts.json]"""
import sys, itertools, json, argparse, time
from fractions import Fraction
sys.path.insert(0, '../scripts')
from cnflib import CNF
import numpy as np, scipy.optimize as so
from pysat.solvers import Solver
ap = argparse.ArgumentParser()
ap.add_argument('s', type=int); ap.add_argument('--K', type=int, default=5)
ap.add_argument('--out', default=None); ap.add_argument('--cuts', default=None)
ap.add_argument('--nosqs', action='store_true', help='drop the no-SQS clauses (control)')
ap.add_argument('--maxit', type=int, default=100000)
a = ap.parse_args()
s = a.s; n = 14
F = CNF()
x = [[F.new() for j in range(n)] for i in range(s)]
for i in range(s): F.exactly(x[i], 7)
y = {}; e = {}
for i, k in itertools.combinations(range(s), 2):
    y[i, k] = [F.and_def([x[i][j], x[k][j]]) for j in range(n)]
    cnt = F._counter(y[i, k], 4)        # cnt[t] <-> at least t common
    F._assert_true(cnt[3])              # |S∩T| >= 3
    ev = F.new(); e[i, k] = ev
    F.add([ev, cnt[4]])                 # |S∩T| <= 3  ->  e
for i, k, l in itertools.combinations(range(s), 3):
    zs = []
    for j in range(n):
        z = F.new(); F.add([-z, y[i, k][j]]); F.add([-z, x[l][j]]); zs.append(z)
    F.add(zs)
if not a.nosqs:
    for sub in itertools.combinations(range(s), 8):
        F.add([-e[p] for p in itertools.combinations(sub, 2)])
# symmetry breaking: rows strictly decreasing, columns non-increasing
for i in range(s - 1):
    F.lex_geq(x[i], x[i + 1])
    d = []
    for j in range(n):
        v = F.new(); a1, b1 = x[i][j], x[i + 1][j]
        F.add([-v, a1, b1]); F.add([-v, -a1, -b1]); d.append(v)   # v -> a xor b
    F.add(d)
for j in range(n - 1):
    F.lex_geq([x[i][j] for i in range(s)], [x[i][j + 1] for i in range(s)])

def farkas_cut(yw):
    """clause: exists row i with sum_j yw[j] x[i][j] <= floor(sum(yw)/2)."""
    tot = sum(yw); bound = tot // 2
    gs = []
    for i in range(s):
        lits = []
        for j in range(n): lits += [x[i][j]] * yw[j]
        c = F._counter(lits, bound + 1)
        g = F.new(); F.add([-g, -c[bound + 1]] if c[bound + 1] not in (None, False) else ([-g] if c[bound+1] is None else []))
        if c[bound+1] is False: pass
        gs.append(g)
    F.add(gs)
cuts = []
for K in range(1, a.K + 1):
    for W in itertools.combinations(range(n), K):
        yw = [1 if j in W else 0 for j in range(n)]
        farkas_cut(yw); cuts.append(yw)
        yc = [1 - v for v in yw]        # complement: some row with |S∩W| >= K/2
        farkas_cut(yc); cuts.append(yc)
print(f's={s}: base vars {F.nv} clauses {len(F.clauses)} initial cuts {len(cuts)}', flush=True)

def lp_check(rows):
    M = np.array([[(r >> j) & 1 for r in rows] for j in range(n)], float)
    res = so.linprog(np.zeros(len(rows)), A_eq=np.vstack([M, np.ones(len(rows))]), b_eq=[.5] * n + [1],
                     bounds=[(0, None)] * len(rows), method='highs')
    if res.status == 0: return True, res.x
    # Farkas: find y>=0 maximizing min_S (y(S) - y/2), normalise sum y = 1
    # vars y_0..13, t ; max t s.t. t - sum_j y_j (1_S[j] - 1/2) <= 0
    A = []; 
    for r in rows: A.append([-(((r >> j) & 1) - 0.5) for j in range(n)] + [1])
    res = so.linprog([0] * n + [-1], A_ub=A, b_ub=[0] * len(rows), A_eq=[[1] * n + [0]], b_eq=[1],
                     bounds=[(0, None)] * n + [(None, None)], method='highs')
    yv = res.x[:n]
    for D in range(1, 200):
        yi = [int(round(v * D)) for v in yv]
        if all(sum(yi[j] for j in range(n) if (r >> j) & 1) * 2 > sum(yi) for r in rows):
            return False, yi
    raise RuntimeError('no small integer Farkas vector')

solver = Solver(name='cadical195', bootstrap_with=F.clauses)
ncl = len(F.clauses); it = 0; t0 = time.time()
while it < a.maxit:
    it += 1
    if not solver.solve():
        print(f'UNSAT after {it-1} Farkas cuts ({time.time()-t0:.1f}s)'); status = 'UNSAT'; break
    mdl = set(l for l in solver.get_model() if l > 0)
    rows = [sum(1 << j for j in range(n) if x[i][j] in mdl) for i in range(s)]
    ok, info = lp_check(rows)
    if ok:
        print('BALANCED COUNTEREXAMPLE', [format(r, '014b') for r in rows], info); status = 'SAT'; break
    farkas_cut(info); cuts.append(info)
    for cl in F.clauses[ncl:]: solver.add_clause(cl)
    ncl = len(F.clauses)
    if it % 200 == 0: print(f'  it {it} last y {info} ({time.time()-t0:.1f}s)', flush=True)
if a.out:
    F.write(a.out, [f'keylemma s={s} K={a.K} cuts={len(cuts)} status={status}'])
if a.cuts:
    json.dump({'s': s, 'K': a.K, 'cuts': cuts, 'status': status}, open(a.cuts, 'w'))
