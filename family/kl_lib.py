"""Theory side of the certified Key Lemma search (v2): constraint rows derived from a literal set,
exact rational Farkas certificates.  Literal keys: ('x',i,j) row i contains column j;
('p',i,k) (i<k) |S_i∩S_k| >= 4; ('t',k) rows 0,1,k form a triangle with triple intersection 1.
Row labels (all of the form  a·w <= b):
  ('nonneg',i) -w_i<=0 | ('le1/8',i) w_i<=1/8 | ('sum<=1',) | ('sum>=1',) | ('w0>=',k) w_k-w_0<=0
  ('U',j,P)  sum_P w <= 1/2           needs x_ij=1 (i in P)
  ('D',j,Q)  -sum_Q w <= -1/2         needs x_ij=0 (i not in Q)
  ('partner',k) w_k-w_1<=0            needs p_0k=0
  ('third',k)   w_k-w_2<=0            needs t_k=1          (case A)
  ('E1',i,K) sum_K w + 4w_i <= 1/2    needs p_ik=1 (k in K)
  ('E2',i,Q) -4 sum_Q w - 4w_i <= -1/2  needs p_ik=0 (k not in Q, k != i)
  ('F1',i,k,K) sum_K w + 2w_i + 2w_k <= 1/2       needs p_ik=0, q_ikl=1 (l in K)
  ('F2',i,k,Q) -2 sum_Q w - 2w_i - 2w_k <= -1/2   needs p_ik=0, q_ikl=0 (l not in Q, l != i,k)
  q_ikl: |S_i∩S_k∩S_l| >= 2"""
from fractions import Fraction as Fr
import numpy as np, scipy.optimize as so
def pk(i, k): return ('p', min(i, k), max(i, k))
def base_rows(R, exact=False, wsort=0):
    rows = []
    if exact:
        for i in range(R):
            c = [0]*R; c[i] = -1; rows.append((c, Fr(-1, 100000), ('pos', i)))
    if wsort:
        for i in range(wsort, R - 1):
            c = [0]*R; c[i+1] = 1; c[i] = -1; rows.append((c, Fr(0), ('sorted', i)))
    for i in range(R):
        c = [0]*R; c[i] = -1; rows.append((c, Fr(0), ('nonneg', i)))
        c = [0]*R; c[i] = 1; rows.append((c, Fr(1, 8), ('le1/8', i)))
    rows.append(([1]*R, Fr(1), ('sum<=1',))); rows.append(([-1]*R, Fr(-1), ('sum>=1',)))
    for k in range(1, R):
        c = [0]*R; c[k] = 1; c[0] = -1; rows.append((c, Fr(0), ('w0>=', k)))
    return rows
def qk(i, k, l): return ('q',) + tuple(sorted((i, k, l)))
def cond_rows(R, L, useE=True, third=False, useF=False):
    rows = []
    for j in range(14):
        P = tuple(i for i in range(R) if L.get(('x', i, j)) == 1)
        Q = tuple(i for i in range(R) if L.get(('x', i, j)) != 0)
        if P:
            c = [0]*R
            for i in P: c[i] = 1
            rows.append((c, Fr(1, 2), ('U', j, P)))
        if len(Q) < R:
            c = [0]*R
            for i in Q: c[i] = -1
            rows.append((c, Fr(-1, 2), ('D', j, Q)))
    for k in range(2, R):
        if L.get(pk(0, k)) == 0:
            c = [0]*R; c[k] = 1; c[1] = -1; rows.append((c, Fr(0), ('partner', k)))
    if third:
        for k in range(3, R):
            if L.get(('t', k)) == 1:
                c = [0]*R; c[k] = 1; c[2] = -1; rows.append((c, Fr(0), ('third', k)))
    if useE:
        for i in range(R):
            K = tuple(k for k in range(R) if k != i and L.get(pk(i, k)) == 1)
            c = [0]*R
            for k in K: c[k] = 1
            c[i] = 4; rows.append((c, Fr(1, 2), ('E1', i, K)))
            Q = tuple(k for k in range(R) if k != i and L.get(pk(i, k)) != 0)
            if len(Q) < R - 1:
                c = [0]*R
                for k in Q: c[k] = -4
                c[i] = -4; rows.append((c, Fr(-1, 2), ('E2', i, Q)))
    if useF:
        for i in range(R):
            for k in range(i + 1, R):
                if L.get(pk(i, k)) != 0: continue
                K = tuple(l for l in range(R) if l not in (i, k) and L.get(qk(i, k, l)) == 1)
                c = [0]*R
                for l in K: c[l] = 1
                c[i] += 2; c[k] += 2; rows.append((c, Fr(1, 2), ('F1', i, k, K)))
                Q = tuple(l for l in range(R) if l not in (i, k) and L.get(qk(i, k, l)) != 0)
                c = [0]*R
                for l in Q: c[l] = -2
                c[i] -= 2; c[k] -= 2; rows.append((c, Fr(-1, 2), ('F2', i, k, Q)))
    return rows
def check(R, rows, y):
    if any(v < 0 for v in y): return False
    for i in range(R):
        if sum(y[k] * rows[k][0][i] for k in range(len(rows)) if y[k]) != 0: return False
    return sum(y[k] * rows[k][1] for k in range(len(rows)) if y[k]) < 0
def exact_on_support(R, rows, S, yf):
    M = [[Fr(rows[k][0][i]) for k in S] + [Fr(0)] for i in range(R)]
    M.append([rows[k][1] for k in S] + [Fr(-1)])
    ncol = len(S); piv = []; r = 0
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
