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

AVOID0 = [False]
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
    if AVOID0[0]:
        for k in range(4, R):
            if L.get(('x', k, 0)) == 0:
                c = [0]*R; c[k] = 1; c[3] = -1; rows.append((c, Fr(0), ('avoid0', k)))
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
        elif t == 'avoid0': used[('x', kind[1], 0)] = 0
    return used


# ---- fast feasibility oracle (C Phase-I simplex; used only as an oracle, certificates are exact) ----
import ctypes, os as _os
_lib = ctypes.CDLL(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'liblpfeas.dylib'))
_lib.lp_feasible.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_double),
                             ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
def infeasible_fast(R, rows):
    rs = [r for r in rows if r[2][0] != 'nonneg']
    m = len(rs)
    A = (ctypes.c_double * (m * R))(*[float(v) for r in rs for v in r[0]])
    b = (ctypes.c_double * m)(*[float(r[1]) for r in rs])
    return _lib.lp_feasible(R, m, A, b, None) == 0

import numpy as _np
_base_cache = {}
def _base_np(R):
    if R not in _base_cache:
        rs = [r for r in base_rows(R) if r[2][0] != 'nonneg']
        _base_cache[R] = (_np.array([[float(v) for v in r[0]] for r in rs]), _np.array([float(r[1]) for r in rs]))
    return _base_cache[R]
def fast_infeasible(R, L):
    """same semantics as infeasible(R, base_rows(R)+cond_rows(R, L)), built directly in numpy"""
    A0, b0 = _base_np(R)
    X = _np.full((R, 14), -1, dtype=_np.int8)
    extra = []; eb = []
    for key, v in L.items():
        if key[0] == 'x': X[key[1], key[2]] = v
        elif key[0] == 'c4' and v == 0:
            c = _np.zeros(R); c[key[1]] = 1; c[1] = -1; extra.append(c); eb.append(0.0)
        elif key[0] == 'T3' and v == 1:
            c = _np.zeros(R); c[key[1]] = 1; c[2] = -1; extra.append(c); eb.append(0.0)
    P = (X == 1).T.astype(float)          # 14 x R
    Q = (X != 0).T.astype(float)
    hasP = P.sum(1) > 0; notQ = Q.sum(1) < R
    blocks = [A0, P[hasP], -Q[notQ]]; bs = [b0, _np.full(hasP.sum(), .5), _np.full(notQ.sum(), -.5)]
    if extra: blocks.append(_np.array(extra)); bs.append(_np.array(eb))
    A = _np.ascontiguousarray(_np.vstack(blocks)); b = _np.ascontiguousarray(_np.concatenate(bs))
    return _lib.lp_feasible(R, A.shape[0], A.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                            b.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), None) == 0
