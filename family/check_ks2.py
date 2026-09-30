#!/usr/bin/env python3
"""Independent checker for keysmt2.py output (prefix.json + prefix.cnf).
(1) every lemma: each certificate row is re-derived from its label, its side condition is checked
    against the lemma's literal set, and the exact Farkas combination is verified
    (sum y_k a_k = 0, sum y_k b_k < 0, y_k > 0);
(2) the lemma clauses are exactly the negated literal sets, appended after the base clauses;
(3) the base clauses coincide with a fresh basecnf.build() and the variable map is the same.
Usage: check_ks2.py prefix"""
import sys, json, ast
from fractions import Fraction as Fr
pre = sys.argv[1]; D = json.load(open(pre + '.json')); R = D['R']
var = {tuple(v[:-1]): v[-1] for v in D['var']}
def row(kind, L):
    c = [Fr(0)] * R; t = kind[0]
    if t == 'nonneg': c[kind[1]] = Fr(-1); return c, Fr(0)
    if t == 'le1/8': c[kind[1]] = Fr(1); return c, Fr(1, 8)
    if t == 'sum<=1': return [Fr(1)] * R, Fr(1)
    if t == 'sum>=1': return [Fr(-1)] * R, Fr(-1)
    if t == 'w0>=': assert kind[1] != 0; c[kind[1]] = Fr(1); c[0] = Fr(-1); return c, Fr(0)
    if t == 'partner':
        k = kind[1]; assert k >= 2 and L.get(('c4', k)) == 0
        c[k] = Fr(1); c[1] = Fr(-1); return c, Fr(0)
    if t == 'third':
        k = kind[1]; assert D['maxthird'] and k >= 3 and L.get(('T3', k)) == 1
        c[k] = Fr(1); c[2] = Fr(-1); return c, Fr(0)
    if t == 'avoid0':
        k = kind[1]; assert D.get('avoid0') and D['case'].startswith('A') and k >= 4 and L.get(('x', k, 0)) == 0
        c[k] = Fr(1); c[3] = Fr(-1); return c, Fr(0)
    if t == 'U':
        j, P = kind[1], kind[2]; assert all(L.get(('x', i, j)) == 1 for i in P)
        for i in P: c[i] = Fr(1)
        return c, Fr(1, 2)
    if t == 'D':
        j, Q = kind[1], kind[2]; assert all(L.get(('x', i, j)) == 0 for i in range(R) if i not in Q)
        for i in Q: c[i] = Fr(-1)
        return c, Fr(-1, 2)
    raise ValueError(kind)
clauses = []
for lem in D['lemmas']:
    L = {tuple(l[:-1]): l[-1] for l in lem['lits']}
    tot = [Fr(0)] * R; rhs = Fr(0)
    for kind_s, y_s in lem['cert']:
        y = Fr(y_s); assert y > 0
        c, b = row(ast.literal_eval(kind_s), L)
        tot = [u + y * v for u, v in zip(tot, c)]; rhs += y * b
    assert all(v == 0 for v in tot) and rhs < 0, 'Farkas check failed'
    clauses.append(sorted((-var[k] if v else var[k]) for k, v in L.items()))
cnf = [list(map(int, l.split()[:-1])) for l in open(pre + '.cnf') if l.strip() and l[0] not in 'cp']
nb = D['nbase']
from basecnf import build
out = build(R, D['case'], D.get('sqs', False), D.get('distinct', False), False, False, D['not1pair'], True, D['maxthird'], False, D.get('colcard', False))
F, x, c4 = out[:3]; T3 = out[3] if D['maxthird'] else {}
var2 = {('x', i, j): x[i][j] for i in range(R) for j in range(14)}
var2.update({('c4', k): c4[0, k] for k in range(2, R)}); var2.update({('T3', k): v for k, v in T3.items()})
assert var2 == var, 'variable map mismatch'
assert [sorted(c) for c in F.clauses] == [sorted(c) for c in cnf[:nb]], 'base CNF mismatch'
assert [sorted(c) for c in cnf[nb:]] == clauses, 'lemma clauses mismatch'
print(f'{pre}: {len(clauses)} theory lemmas verified with exact Farkas certificates; base CNF ({nb} clauses) reproduced')
