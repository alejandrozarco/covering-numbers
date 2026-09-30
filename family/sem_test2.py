#!/usr/bin/env python3
"""Component test: solutions of the base CNF built WITHOUT one optional component (nbr / colcard /
distinct / not1pair) are classified by an independent Python predicate for that component; the CNF WITH
the component must be satisfiable under the same x exactly when the predicate holds.
Usage: sem_test2.py R case component n"""
import sys, random, itertools
from pysat.solvers import Solver
from basecnf import build
R, case, comp, n = int(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4])
third = case == 't1'; not1pair = case == 't2'
def mk(on):
    kw = dict(nbr=True, colcard=True, distinct=(comp == 'distinct'), not1pair=not1pair)
    if comp in kw: kw[comp] = on
    out = build(R, case, False, kw['distinct'], False, False, kw['not1pair'], True, third, False, kw['colcard'], kw['nbr'], False)
    return out[0], out[1]
Foff, x = mk(False); Fon, x2 = mk(True); assert x == x2
def lam(a, b): return sum(p & q for p, q in zip(a, b))
def pred(rows):
    if comp == 'nbr':
        for i in range(R):
            if sum(1 for k in range(R) if k != i and lam(rows[i], rows[k]) == 3) < (6 if i == 0 else 5): return False
        for i, k in itertools.combinations(range(R), 2):
            if lam(rows[i], rows[k]) == 3 and not any(lam(rows[i], rows[l]) == 3 and lam(rows[k], rows[l]) == 3 for l in range(R) if l not in (i, k)): return False
        return True
    if comp == 'colcard': return all(4 <= sum(r[j] for r in rows) <= R - 4 for j in range(14))
    if comp == 'distinct': return len(set(map(tuple, rows))) == R
    if comp == 'not1pair': return not any(lam(rows[0], rows[k]) == 3 and lam(rows[1], rows[k]) == 3 and sum(rows[k][:3]) == 1 for k in range(2, R))
Soff = Solver(name='cadical195', bootstrap_with=Foff.clauses); Son = Solver(name='cadical195', bootstrap_with=Fon.clauses)
random.seed(2); cnt = {True: 0, False: 0}; bad = 0
for it in range(n):
    assum = [random.choice([1, -1]) * x[random.randrange(2, R)][random.randrange(14)] for _ in range(4)]
    if not Soff.solve(assumptions=assum): continue
    m = set(l for l in Soff.get_model() if l > 0)
    rows = [[1 if x[i][j] in m else 0 for j in range(14)] for i in range(R)]
    want = pred(rows); got = Son.solve(assumptions=[x[i][j] if rows[i][j] else -x[i][j] for i in range(R) for j in range(14)])
    cnt[want] += 1; bad += (want != got)
print(f'{comp} R={R} case={case}: predicate true {cnt[True]}, false {cnt[False]}, mismatches {bad}')
