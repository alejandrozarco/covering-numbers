#!/usr/bin/env python3
"""Independent checker for the Key Lemma theory lemmas (does not import kl_lib / klprop).
For every lemma (literal set L, certificate = list of (label, y > 0)):
  each label is turned into its linear constraint a·w <= b here, its side condition is checked
  against L, and sum y·a = 0, sum y·b < 0 is verified in exact rational arithmetic.
Then: the CNF = base clauses (fresh basecnf.build with the recorded options) + the lemma clauses
(¬L mapped through the variable map, rebuilt here from basecnf) exactly.
Usage: klcheck.py prefix      (reads prefix.cert.json and prefix.cnf)"""
import sys, json, ast
from fractions import Fraction as Fr
pre = sys.argv[1]; D = json.load(open(pre + '.cert.json')); R = D['R']
from basecnf import build
out = build(R, D['case'], D['sqs'], D.get('exact', False), False, False, D['not1pair'], True, D['third'], False, True, D.get('nbr', False), D.get('useF', False), not D.get('wsort', False))
F, x, c4 = out[:3]; T3 = out[3] if D['third'] else {}
var = {('x', i, j): x[i][j] for i in range(R) for j in range(14)}
var.update({('p', i, k): v for (i, k), v in c4.items()}); var.update({('t', k): v for k, v in T3.items()})
if D.get('useF', False): var.update({('q', i, k, l): v for (i, k, l), v in out[4].items()})
def P(L, i, k): return L.get(('p', min(i, k), max(i, k)))
def Qf(L, i, k, l): return L.get(('q',) + tuple(sorted((i, k, l))))
def row(lab, L):
    c = [Fr(0)] * R; t = lab[0]
    if t == 'nonneg': c[lab[1]] = Fr(-1); return c, Fr(0)
    if t == 'pos': assert D.get('exact'); c[lab[1]] = Fr(-1); return c, Fr(-1, 100000)
    if t == 'sorted':
        i = lab[1]; assert D.get('wsort') and (3 if D['third'] else 2) <= i < R - 1; c[i + 1] = Fr(1); c[i] = Fr(-1); return c, Fr(0)
    if t == 'le1/8': c[lab[1]] = Fr(1); return c, Fr(1, 8)
    if t == 'sum<=1': return [Fr(1)] * R, Fr(1)
    if t == 'sum>=1': return [Fr(-1)] * R, Fr(-1)
    if t == 'w0>=': k = lab[1]; assert 1 <= k < R; c[k] = Fr(1); c[0] = Fr(-1); return c, Fr(0)
    if t == 'U':
        j, S = lab[1], lab[2]; assert len(set(S)) == len(S) and all(L.get(('x', i, j)) == 1 for i in S)
        for i in S: c[i] = Fr(1)
        return c, Fr(1, 2)
    if t == 'D':
        j, S = lab[1], lab[2]; assert all(L.get(('x', i, j)) == 0 for i in range(R) if i not in S)
        for i in set(S): c[i] = Fr(-1)
        return c, Fr(-1, 2)
    if t == 'partner':
        k = lab[1]; assert 2 <= k < R and P(L, 0, k) == 0; c[k] = Fr(1); c[1] = Fr(-1); return c, Fr(0)
    if t == 'third':
        k = lab[1]; assert D['third'] and 3 <= k < R and L.get(('t', k)) == 1; c[k] = Fr(1); c[2] = Fr(-1); return c, Fr(0)
    if t == 'E1':
        i, K = lab[1], lab[2]; assert D['useE'] and i not in K and len(set(K)) == len(K) and all(P(L, i, k) == 1 for k in K)
        for k in K: c[k] = Fr(1)
        c[i] = Fr(4); return c, Fr(1, 2)
    if t == 'E2':
        i, Q = lab[1], lab[2]; assert D['useE'] and i not in Q and all(P(L, i, k) == 0 for k in range(R) if k != i and k not in Q)
        for k in set(Q): c[k] = Fr(-4)
        c[i] = Fr(-4); return c, Fr(-1, 2)
    if t == 'F1':
        i, k, K = lab[1], lab[2], lab[3]
        assert D.get('useF') and i != k and P(L, i, k) == 0 and len(set(K)) == len(K) and all(l not in (i, k) and Qf(L, i, k, l) == 1 for l in K)
        for l in K: c[l] = Fr(1)
        c[i] += 2; c[k] += 2; return c, Fr(1, 2)
    if t == 'F2':
        i, k, Q = lab[1], lab[2], lab[3]
        assert D.get('useF') and i != k and P(L, i, k) == 0 and all(Qf(L, i, k, l) == 0 for l in range(R) if l not in (i, k) and l not in Q)
        for l in set(Q) - {i, k}: c[l] = Fr(-2)
        c[i] -= 2; c[k] -= 2; return c, Fr(-1, 2)
    raise ValueError(lab)
clauses = []
assert len(D['certs']) == len(D['lemma_lits'])
for lits, cert in zip(D['lemma_lits'], D['certs']):
    L = {tuple(l[:-1]): l[-1] for l in lits}
    assert len(L) == len(lits) and all(v in (0, 1) for v in L.values())
    tot = [Fr(0)] * R; rhs = Fr(0)
    for lab_s, y_s in cert:
        y = Fr(y_s); assert y > 0
        a, b = row(ast.literal_eval(lab_s), L)
        tot = [u + y * v for u, v in zip(tot, a)]; rhs += y * b
    assert all(v == 0 for v in tot) and rhs < 0, 'Farkas identity fails'
    clauses.append(sorted(-var[k] if v else var[k] for k, v in L.items()))
cnf = [list(map(int, l.split()[:-1])) for l in open(pre + '.cnf') if l.strip() and l[0] not in 'cp']
nb = D['nbase']
assert nb == len(F.clauses) and [sorted(c) for c in F.clauses] == [sorted(c) for c in cnf[:nb]], 'base CNF mismatch'
rest = cnf[nb:]
if D.get('cube'):
    for n, (key, val) in enumerate(D['cube']):
        key = tuple(key); assert rest[n] == [var[key] if val else -var[key]], 'cube unit mismatch'
    rest = rest[len(D['cube']):]
assert [sorted(c) for c in rest] == clauses, 'lemma clauses mismatch'
print(f'PASS {pre}' + (f' [cube {D["cube"]}]' if D.get('cube') else '') + f': {len(clauses)} theory lemmas (exact Farkas) + base CNF ({nb} clauses) reproduced')
