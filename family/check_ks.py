#!/usr/bin/env python3
"""Independent checker for keysmt.py theory lemmas.
For every lemma: re-derives each used linear constraint from its label and the lemma's literal set,
checks it is valid under those literals, and checks the exact rational Farkas combination
(sum y_k a_k = 0, sum y_k b_k < 0, y >= 0).  Then checks that the lemma clauses (as negated literal
sets) appear verbatim in the final CNF after the base clauses, and that the base clauses coincide
with a fresh basecnf.build().  Usage: check_ks.py prefix"""
import sys, json, ast
from fractions import Fraction as Fr
pre = sys.argv[1]
D = json.load(open(pre + '.json')); R = D['R']; x = D['x']
def expected(kind, lits):
    """return (coef list, rhs) for label kind, or raise if not valid under lits"""
    c = [Fr(0)] * R; t = kind[0]
    if t == 'nonneg': c[kind[1]] = Fr(-1); return c, Fr(0)
    if t == 'le1/8': c[kind[1]] = Fr(1); return c, Fr(1, 8)
    if t == 'sum<=1': return [Fr(1)] * R, Fr(1)
    if t == 'sum>=1': return [Fr(-1)] * R, Fr(-1)
    if t == 'w0>=': c[kind[1]] = Fr(1); c[0] = Fr(-1); return c, Fr(0)
    if t == 'U':
        j, P = kind[1], kind[2]
        assert all((i, j, 1) in lits for i in P), 'U row not justified'
        for i in P: c[i] = Fr(1)
        return c, Fr(1, 2)
    if t == 'D':
        j, Q = kind[1], kind[2]
        assert all((i, j, 0) in lits for i in range(R) if i not in Q), 'D row not justified'
        for i in Q: c[i] = Fr(-1)
        return c, Fr(-1, 2)
    raise ValueError(kind)
clauses = []
for L in D['lemmas']:
    lits = set(tuple(l) for l in L['lits'])
    ys = [Fr(v) for v in L['y'].values()]
    assert len(ys) == len(L['rows'])
    tot = [Fr(0)] * R; rhs = Fr(0)
    for yk, row in zip(ys, L['rows']):
        assert yk > 0
        kind = ast.literal_eval(row[-1])
        c, b = expected(kind, lits)
        assert [Fr(v) for v in row[:R]] == c and Fr(row[R]) == b, 'stored row mismatch'
        tot = [a + yk * v for a, v in zip(tot, c)]; rhs += yk * b
    assert all(v == 0 for v in tot) and rhs < 0, 'Farkas check failed'
    clauses.append(sorted(-x[i][j] if v else x[i][j] for (i, j, v) in lits))
# CNF check
cnf = [list(map(int, l.split()[:-1])) for l in open(pre + '.cnf') if l and l[0] not in 'cp']
nb = D['nbase']
sys.path.insert(0, '.')
from basecnf import build
F, x2 = build(R, D['case'], False, False, D['not1'])
assert x2 == x and [sorted(c) for c in F.clauses] == [sorted(c) for c in cnf[:nb]], 'base CNF mismatch'
assert [sorted(c) for c in cnf[nb:]] == clauses, 'lemma clauses mismatch'
print(f'{pre}: {len(clauses)} lemmas verified (exact Farkas), base CNF ({nb} clauses) reproduced')
