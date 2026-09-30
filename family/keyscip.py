#!/usr/bin/env python3
"""Independent formulation (SCIP, bilinear constraints handled by SCIP itself) of the Key Lemma
counterexample search: R rows (7-subsets of [14]; duplicates allowed), weights w_i >= 0, sum 1,
sum_i w_i x_ij = 1/2 for all j (bilinear), pairwise |∩| >= 3, 3-wise ∩ nonempty, no 8 rows pairwise |∩|<=3.
Normalisation: row0 = {0..6} has maximum weight; row1 = {0,1,2,7,8,9,10} (a |∩|=3 partner of row0);
rows 2.. sorted by weight.  No column symmetry breaking (SCIP may detect symmetries itself).
Usage: keyscip.py R [--sqs] [--nopair]"""
import sys, itertools, argparse
from pyscipopt import Model, quicksum
ap = argparse.ArgumentParser(); ap.add_argument('R', type=int); ap.add_argument('--sqs', action='store_true')
ap.add_argument('--nopair', action='store_true'); ap.add_argument('--time', type=float, default=1e6)
a = ap.parse_args(); R = a.R; n = 14
M = Model(); M.setParam('parallel/maxnthreads', 1); M.setParam('limits/time', a.time)
x = [[M.addVar(vtype='B', name=f'x{i}_{j}') for j in range(n)] for i in range(R)]
w = [M.addVar(lb=0, ub=1, name=f'w{i}') for i in range(R)]
for i in range(R): M.addCons(quicksum(x[i]) == 7)
for j in range(n):
    M.addCons(x[0][j] == (1 if j < 7 else 0))
    if not a.nopair: M.addCons(x[1][j] == (1 if j in (0, 1, 2, 7, 8, 9, 10) else 0))
M.addCons(quicksum(w) == 1)
for k in range(1, R): M.addCons(w[0] >= w[k])
for k in range(2, R - 1): M.addCons(w[k] >= w[k + 1])
if a.nopair:
    M.addCons(w[1] >= w[2])
for j in range(n): M.addCons(quicksum(w[i] * x[i][j] for i in range(R)) == 0.5)
A = {}
for i, k in itertools.combinations(range(R), 2):
    A[i, k] = [M.addVar(vtype='B') for j in range(n)]
    for j in range(n):
        M.addConsAnd([x[i][j], x[k][j]], A[i, k][j])
    M.addCons(quicksum(A[i, k]) >= 3)
for i, k, l in itertools.combinations(range(R), 3):
    M.addCons(quicksum(A[i, k][j] * x[l][j] for j in range(n)) >= 1)
if not a.sqs:
    E = {}
    for p in itertools.combinations(range(R), 2):
        E[p] = M.addVar(vtype='B'); M.addCons(quicksum(A[p]) + E[p] >= 4)
    for sub in itertools.combinations(range(R), 8):
        M.addCons(quicksum(E[p] for p in itertools.combinations(sub, 2)) <= 27)
M.hideOutput(False)
M.optimize()
print('status', M.getStatus())
if M.getStatus() == 'optimal':
    for i in range(R):
        print(''.join(str(int(round(M.getVal(x[i][j])))) for j in range(n)), round(M.getVal(w[i]), 5))
