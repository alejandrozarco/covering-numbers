#!/usr/bin/env python3
"""Lazy SMT (CDCL + exact Farkas theory lemmas) for the Key Lemma counterexample search.

Boolean part: basecnf.build(R, case, not1) (see basecnf.py / cases.py).
Theory part (weights w_i, real):  w >= 0, w <= 1/8, sum w = 1, w0 >= w_k (k>=1) (row 0 = max weight),
  and for every column j:  sum_{i: x_ij} w_i = 1/2.
Theory lemmas: a clause C over x-literals is added when the LP formed by the unconditional constraints
  and the constraints   U(j,P): sum_{i in P} w_i <= 1/2   (valid when x_ij = 1 for all i in P)
                        D(j,Q): sum_{i in Q} w_i >= 1/2   (valid when x_ij = 0 for all i not in Q)
  implied by the negation of C is infeasible; the exact rational Farkas multipliers are stored.
Output: final CNF (base + lemmas) for DRAT checking, and a JSON file with all lemmas + certificates.
Usage: keysmt.py R prefix [--sqs]"""
import sys, itertools, json, time, argparse
from fractions import Fraction as Fr
sys.path.insert(0, '../scripts')
from cnflib import CNF
import numpy as np, scipy.optimize as so
from pysat.solvers import Solver

from basecnf import build

def base_rows(R):
    """unconditional theory constraints as (coef list, rhs, kind) meaning coef.w <= rhs"""
    rows = []
    for i in range(R):
        c = [0]*R; c[i] = -1; rows.append((c, Fr(0), ('nonneg', i)))
        c = [0]*R; c[i] = 1; rows.append((c, Fr(1, 8), ('le1/8', i)))
    rows.append(([1]*R, Fr(1), ('sum<=1',))); rows.append(([-1]*R, Fr(-1), ('sum>=1',)))
    for k in range(1, R):
        c = [0]*R; c[k] = 1; c[0] = -1; rows.append((c, Fr(0), ('w0>=', k)))
    return rows

def cond_rows(R, lits):
    """lits: dict (i,j)->0/1 of fixed x-values. Returns conditional rows U(j,P), D(j,Q)."""
    rows = []
    for j in range(14):
        P = [i for i in range(R) if lits.get((i, j)) == 1]
        Q = [i for i in range(R) if lits.get((i, j)) != 0]
        if P:
            c = [0]*R
            for i in P: c[i] = 1
            rows.append((c, Fr(1, 2), ('U', j, tuple(P))))
        if len(Q) < R:
            c = [0]*R
            for i in Q: c[i] = -1
            rows.append((c, Fr(-1, 2), ('D', j, tuple(Q))))
    return rows

def lp_feasible(R, rows):
    A = np.array([r[0] for r in rows], float); b = np.array([float(r[1]) for r in rows])
    res = so.linprog(np.zeros(R), A_ub=A, b_ub=b, bounds=[(None, None)]*R, method='highs')
    return res.status != 2

def farkas(R, rows):
    """exact y>=0 with y^T A = 0, y^T b < 0, or None."""
    A = np.array([r[0] for r in rows], float); b = np.array([float(r[1]) for r in rows])
    m = len(rows)
    res = so.linprog(b, A_eq=A.T, b_eq=np.zeros(R), A_ub=np.ones((1, m)), b_ub=[1],
                     bounds=[(0, None)]*m, method='highs')
    if res.status != 0 or res.fun > -1e-9: return None
    yf = res.x
    for D in (1, 2, 4, 8, 16, 32, 64, 128, 256, 1024, 4096, 1 << 16, 1 << 20):
        y = [Fr(v).limit_denominator(D * 1000) if v > 1e-12 else Fr(0) for v in yf]
        if check(R, rows, y): return y
    # exact re-solve on support via Gaussian elimination
    S = [k for k in range(m) if yf[k] > 1e-12]
    y = exact_on_support(R, rows, S, yf)
    return y if y is not None and check(R, rows, y) else None

def exact_on_support(R, rows, S, yf):
    # unknowns y_k (k in S); equations: sum_k y_k A[k][i] = 0 (i<R), sum_k y_k b_k = -1
    eqs = [[Fr(rows[k][0][i]) for k in S] + [Fr(0)] for i in range(R)]
    eqs.append([rows[k][1] for k in S] + [Fr(-1)])
    ncol = len(S); piv = []; r = 0
    M = eqs
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

def check(R, rows, y):
    if any(v < 0 for v in y): return False
    for i in range(R):
        if sum(y[k] * rows[k][0][i] for k in range(len(rows)) if y[k]) != 0: return False
    return sum(y[k] * rows[k][1] for k in range(len(rows)) if y[k]) < 0

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('R', type=int); ap.add_argument('prefix')
    ap.add_argument('--sqs', action='store_true'); ap.add_argument('--case', default='t1'); ap.add_argument('--not1', action='store_true'); a = ap.parse_args()
    R = a.R; F, x = build(R, a.case, a.sqs, False, a.not1)
    base = base_rows(R); nbase = len(F.clauses)
    S = Solver(name='cadical195', bootstrap_with=F.clauses)
    lemmas = []; t0 = time.time(); it = 0
    while True:
        it += 1
        if not S.solve(): status = 'UNSAT'; break
        mdl = set(l for l in S.get_model() if l > 0)
        full = {(i, j): (1 if x[i][j] in mdl else 0) for i in range(R) for j in range(14)}
        if lp_feasible(R, base + cond_rows(R, full)):
            status = 'SAT'
            print('COUNTEREXAMPLE', [''.join(str(full[i, j]) for j in range(14)) for i in range(R)]); break
        # deletion-based minimisation of the literal set (rows 0,1 are unit-fixed: drop them first)
        lits = dict(full)
        keys = list(lits.keys())
        # try dropping whole columns first, then single literals
        for j in range(14):
            trial = {k: v for k, v in lits.items() if k[1] != j}
            if not lp_feasible(R, base + cond_rows(R, trial)): lits = trial
        for k in keys:
            if k not in lits: continue
            trial = dict(lits); trial.pop(k)
            if not lp_feasible(R, base + cond_rows(R, trial)): lits = trial
        rows = base + cond_rows(R, lits)
        y = farkas(R, rows)
        if y is None:
            lits = dict(full)
            rows = base + cond_rows(R, lits); y = farkas(R, rows)
        assert y is not None, 'no exact Farkas certificate'
        # keep only the literals used by rows with y>0
        used = set()
        for k, (c, rhs, kind) in enumerate(rows):
            if y[k] and kind[0] == 'U':
                used |= {(i, kind[1], 1) for i in kind[2]}
            if y[k] and kind[0] == 'D':
                used |= {(i, kind[1], 0) for i in range(R) if i not in kind[2]}
        clause = [(-x[i][j] if v else x[i][j]) for (i, j, v) in sorted(used)]
        S.add_clause(clause); F.add(clause)
        lemmas.append({'lits': sorted(used), 'y': {str(k): str(y[k]) for k in range(len(rows)) if y[k]},
                       'rows': [list(map(str, rows[k][0])) + [str(rows[k][1]), str(rows[k][2])] for k in range(len(rows)) if y[k]]})
        if it % 100 == 0:
            print(f'  it {it}: lemma size {len(clause)}  ({time.time()-t0:.0f}s)', flush=True)
    print(f'R={R} status {status} after {it} iterations, {len(lemmas)} lemmas, {time.time()-t0:.1f}s', flush=True)
    F.write(a.prefix + '.cnf', [f'keysmt R={R} base_clauses={nbase} lemmas={len(lemmas)} status={status}'])
    json.dump({'R': R, 'case': a.case, 'not1': a.not1, 'nbase': nbase, 'status': status, 'x': x, 'lemmas': lemmas}, open(a.prefix + '.json', 'w'))
main()
