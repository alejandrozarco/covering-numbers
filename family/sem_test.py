#!/usr/bin/env python3
"""Semantic test of the base CNF (basecnf.build as used by klprop): for random x-assignments near CNF
solutions, 'CNF satisfiable under these x' must equal an independent Python evaluation of the
intended constraints (§5.2 of FAMILY.md).  Usage: sem_test.py R case [exact] [n]"""
import sys, random, itertools
from pysat.solvers import Solver
from basecnf import build
from cases import CASES
R, case = int(sys.argv[1]), sys.argv[2]; exact = len(sys.argv) > 3 and sys.argv[3] == 'exact'
n_iter = int(sys.argv[4]) if len(sys.argv) > 4 else 200
third = case == 't1'; not1pair = case == 't2'
out = build(R, case, False, exact, False, False, not1pair, True, third, False, True, True, False)
F, x = out[0], out[1]
fixed = CASES[case]['rows']; f0 = len(fixed); blocks = CASES[case]['blocks']
def lam(a, b): return sum(p & q for p, q in zip(a, b))
def intended(rows):
    if any(sum(r) != 7 for r in rows): return False
    if any(rows[i] != fixed[i] for i in range(f0)): return False
    for a, b in itertools.combinations(rows, 2):
        if lam(a, b) < 3: return False
    for a, b, c in itertools.combinations(rows, 3):
        if not any(p & q & r for p, q, r in zip(a, b, c)): return False
    for sub in itertools.combinations(range(R), 8):
        if all(lam(rows[i], rows[k]) <= 3 for i, k in itertools.combinations(sub, 2)): return False
    free = rows[f0:]
    if any(tuple(free[i]) < tuple(free[i + 1]) for i in range(len(free) - 1)): return False
    for blk in blocks:
        for j, j2 in zip(blk, blk[1:]):
            if tuple(r[j] for r in free) < tuple(r[j2] for r in free): return False
    if exact and len(set(map(tuple, rows))) < R: return False
    for j in range(14):
        c = sum(r[j] for r in rows)
        if c < 4 or c > R - 4: return False
    for i in range(R):
        if sum(1 for k in range(R) if k != i and lam(rows[i], rows[k]) == 3) < (6 if i == 0 else 5): return False
    for i, k in itertools.combinations(range(R), 2):
        if lam(rows[i], rows[k]) == 3 and not any(lam(rows[i], rows[l]) == 3 and lam(rows[k], rows[l]) == 3 for l in range(R) if l not in (i, k)): return False
    if not1pair:
        for k in range(2, R):
            if lam(rows[0], rows[k]) == 3 and lam(rows[1], rows[k]) == 3 and sum(rows[k][:3]) == 1: return False
    return True
S = Solver(name='cadical195', bootstrap_with=F.clauses)
random.seed(1); agree = [0, 0]; bad = 0; sols = 0
for it in range(n_iter):
    assum = [random.choice([1, -1]) * x[random.randrange(f0, R)][random.randrange(14)] for _ in range(3)]
    if not S.solve(assumptions=assum): continue
    m = set(l for l in S.get_model() if l > 0); sols += 1
    rows = [[1 if x[i][j] in m else 0 for j in range(14)] for i in range(R)]
    assert intended(rows), 'CNF solution violates intended constraints'
    for trial in range(5):
        r2 = [list(r) for r in rows]
        for _ in range(random.randint(1, 3)):
            i = random.randrange(f0, R); ones = [j for j in range(14) if r2[i][j]]; zeros = [j for j in range(14) if not r2[i][j]]
            r2[i][random.choice(ones)] = 0; r2[i][random.choice(zeros)] = 1
        want = intended(r2)
        got = S.solve(assumptions=[x[i][j] if r2[i][j] else -x[i][j] for i in range(R) for j in range(14)])
        agree[want] += 1
        if want != got: bad += 1; print('MISMATCH', want, got)
print(f'R={R} case={case} exact={exact}: {sols} solutions, perturbations intended-true {agree[1]}, false {agree[0]}, mismatches {bad}')
