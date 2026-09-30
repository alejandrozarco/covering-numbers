#!/usr/bin/env python3
"""Lazy SMT (CDCL + exact Farkas theory lemmas) for the Key Lemma counterexample search, with the
case normalisations A / B of FAMILY.md:
  A: basecnf case t1, row0 max weight, row1 max-weight |∩|=3 partner of row0, row2 max-weight row
     forming a t=1 triangle with rows 0,1        (--case t1 --maxthird)
  B: basecnf case t2, row0 max weight, row1 max-weight partner, no t=1 triangle through rows 0,1
     (--case t2 --not1pair)
Theory (weights w_i): w_i >= 0, w_i <= 1/8, sum w = 1, w_0 >= w_k,
  ('partner',k): w_k <= w_1   if |S0∩Sk| = 3        (literal -c4[0,k])
  ('third',k):   w_k <= w_2   if T3[k]              (case A only)
  ('U',j,P): sum_{i in P} w_i <= 1/2  if x_ij = 1 (i in P);  ('D',j,Q): sum_{i in Q} w_i >= 1/2 if x_ij = 0 (i not in Q)
Lemma = clause forbidding a literal set whose conditional rows + unconditional rows are LP-infeasible,
with exact Farkas multipliers stored for independent checking (check_ks2.py).
Usage: keysmt2.py R prefix --case t1|t2 [--maxthird] [--not1pair] [--sqs]"""
import sys, itertools, json, time, argparse
from fractions import Fraction as Fr
import numpy as np, scipy.optimize as so
from pysat.solvers import Solver
from basecnf import build

def base_rows(R):
    rows = []
    for i in range(R):
        c = [0]*R; c[i] = -1; rows.append((c, Fr(0), ('nonneg', i)))
        c = [0]*R; c[i] = 1; rows.append((c, Fr(1, 8), ('le1/8', i)))
    rows.append(([1]*R, Fr(1), ('sum<=1',))); rows.append(([-1]*R, Fr(-1), ('sum>=1',)))
    for k in range(1, R):
        c = [0]*R; c[k] = 1; c[0] = -1; rows.append((c, Fr(0), ('w0>=', k)))
    return rows

def cond_rows(R, L):
    """L: dict key->value; keys ('x',i,j) / ('c4',k) / ('T3',k)."""
    rows = []
    for j in range(14):
        P = [i for i in range(R) if L.get(('x', i, j)) == 1]
        Q = [i for i in range(R) if L.get(('x', i, j)) != 0]
        if P:
            c = [0]*R
            for i in P: c[i] = 1
            rows.append((c, Fr(1, 2), ('U', j, tuple(P))))
        if len(Q) < R:
            c = [0]*R
            for i in Q: c[i] = -1
            rows.append((c, Fr(-1, 2), ('D', j, tuple(Q))))
    for k in range(2, R):
        if L.get(('c4', k)) == 0:
            c = [0]*R; c[k] = 1; c[1] = -1; rows.append((c, Fr(0), ('partner', k)))
    for k in range(3, R):
        if L.get(('T3', k)) == 1:
            c = [0]*R; c[k] = 1; c[2] = -1; rows.append((c, Fr(0), ('third', k)))
    return rows

def infeasible(R, rows):
    A = np.array([r[0] for r in rows], float); b = np.array([float(r[1]) for r in rows])
    res = so.linprog(np.zeros(R), A_ub=A, b_ub=b, bounds=[(None, None)]*R, method='highs')
    return res.status == 2

def check(R, rows, y):
    if any(v < 0 for v in y): return False
    for i in range(R):
        if sum(y[k] * rows[k][0][i] for k in range(len(rows)) if y[k]) != 0: return False
    return sum(y[k] * rows[k][1] for k in range(len(rows)) if y[k]) < 0

def exact_on_support(R, rows, S, yf):
    eqs = [[Fr(rows[k][0][i]) for k in S] + [Fr(0)] for i in range(R)]
    eqs.append([rows[k][1] for k in S] + [Fr(-1)])
    ncol = len(S); piv = []; r = 0; M = eqs
    for c in range(ncol):
        p = next((q for q in range(r, len(M)) if M[q][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        inv = 1 / M[r][c]; M[r] = [v * inv for v in M[r]]
        for q in range(len(M)):
            if q != r and M[q][c] != 0:
                f = M[q][c]; M[q] = [a - f * bb for a, bb in zip(M[q], M[r])]
        piv.append(c); r += 1
    if any(all(v == 0 for v in row[:-1]) and row[-1] != 0 for row in M): return None
    free = [c for c in range(ncol) if c not in piv]
    scale = -1 / sum(yf[k] * float(rows[k][1]) for k in S)
    val = {c: Fr(yf[S[c]] * scale).limit_denominator(10**6) for c in free}
    y = [Fr(0)] * len(rows)
    for idx, c in enumerate(piv):
        y[S[c]] = M[idx][-1] - sum(M[idx][f] * val[f] for f in free)
    for f in free: y[S[f]] = val[f]
    return y

def farkas(R, rows):
    A = np.array([r[0] for r in rows], float); b = np.array([float(r[1]) for r in rows]); m = len(rows)
    res = so.linprog(b, A_eq=A.T, b_eq=np.zeros(R), A_ub=np.ones((1, m)), b_ub=[1],
                     bounds=[(0, None)]*m, method='highs')
    if res.status != 0 or res.fun > -1e-9: return None
    yf = res.x
    for D in (1, 2, 4, 8, 16, 64, 256, 1024, 4096, 1 << 16, 1 << 20):
        y = [Fr(v).limit_denominator(D * 1000) if v > 1e-12 else Fr(0) for v in yf]
        if check(R, rows, y): return y
    S = [k for k in range(m) if yf[k] > 1e-12]
    y = exact_on_support(R, rows, S, yf)
    return y if y is not None and check(R, rows, y) else None

def used_lits(R, rows, y, L):
    used = {}
    for k, (c, rhs, kind) in enumerate(rows):
        if not y[k]: continue
        t = kind[0]
        if t == 'U':
            for i in kind[2]: used[('x', i, kind[1])] = 1
        elif t == 'D':
            for i in range(R):
                if i not in kind[2]: used[('x', i, kind[1])] = 0
        elif t == 'partner': used[('c4', kind[1])] = 0
        elif t == 'third': used[('T3', kind[1])] = 1
    return used

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('R', type=int); ap.add_argument('prefix')
    ap.add_argument('--case', required=True); ap.add_argument('--maxthird', action='store_true')
    ap.add_argument('--not1pair', action='store_true'); ap.add_argument('--sqs', action='store_true')
    a = ap.parse_args(); R = a.R
    out = build(R, a.case, a.sqs, False, False, False, a.not1pair, True, a.maxthird)
    F, x, c4 = out[:3]; T3 = out[3] if a.maxthird else {}
    var = {}
    for i in range(R):
        for j in range(14): var[('x', i, j)] = x[i][j]
    for k in range(2, R): var[('c4', k)] = c4[0, k]
    for k, v in T3.items(): var[('T3', k)] = v
    base = base_rows(R); nbase = len(F.clauses)
    S = Solver(name='cadical195', bootstrap_with=F.clauses)
    lemmas = []; t0 = time.time(); it = 0
    while True:
        it += 1
        if not S.solve(): status = 'UNSAT'; break
        mdl = set(l for l in S.get_model() if l > 0)
        full = {key: (1 if v in mdl else 0) for key, v in var.items()}
        rows = base + cond_rows(R, full)
        if not infeasible(R, rows):
            status = 'SAT'
            print('COUNTEREXAMPLE', [''.join(str(full['x', i, j]) for j in range(14)) for i in range(R)], flush=True)
            break
        y = farkas(R, rows); assert y is not None
        L = used_lits(R, rows, y, full)
        for key in list(L.keys()):                      # deletion-based minimisation
            trial = dict(L); trial.pop(key)
            if infeasible(R, base + cond_rows(R, trial)): L = trial
        rows = base + cond_rows(R, L); y = farkas(R, rows)
        if y is None:
            L = used_lits(R, base + cond_rows(R, full), farkas(R, base + cond_rows(R, full)), full)
            rows = base + cond_rows(R, L); y = farkas(R, rows)
        assert y is not None, 'no exact Farkas certificate'
        L = used_lits(R, rows, y, L)                    # literals actually used by the certificate
        rows2 = base + cond_rows(R, L)
        # re-index certificate on rows2 (rows used are a subset of rows2)
        idx = {r[2]: k for k, r in enumerate(rows2)}
        yy = {idx[rows[k][2]]: y[k] for k in range(len(rows)) if y[k]}
        clause = [(-var[key] if v else var[key]) for key, v in sorted(L.items())]
        S.add_clause(clause); F.add(clause)
        lemmas.append({'lits': [[*key, v] for key, v in sorted(L.items())],
                       'cert': [[str(rows2[k][2]), str(v)] for k, v in sorted(yy.items())]})
        if it % 500 == 0:
            print(f'  it {it}: lemma size {len(clause)}  ({time.time()-t0:.0f}s)', flush=True)
    print(f'R={R} case={a.case} status {status} after {it} iterations, {len(lemmas)} lemmas, {time.time()-t0:.1f}s', flush=True)
    F.write(a.prefix + '.cnf', [f'keysmt2 R={R} case={a.case} maxthird={a.maxthird} not1pair={a.not1pair} base_clauses={nbase} lemmas={len(lemmas)} status={status}'])
    json.dump({'R': R, 'case': a.case, 'sqs': a.sqs, 'maxthird': a.maxthird, 'not1pair': a.not1pair, 'nbase': nbase,
               'status': status, 'var': [[*k, v] for k, v in var.items()], 'lemmas': lemmas}, open(a.prefix + '.json', 'w'))
main()
