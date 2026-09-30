#!/usr/bin/env python3
"""Weighted blow-up scan against LJCR v1.2.
A base structure (points X, blocks Y_1..Y_b) in which any t points lie in a common block gives, for integer weights
w_x >= 0 with sum v and max block load L = max_j sum_{x in Y_j} w_x:  C(v,k,t) <= b for every k >= L (pad blocks).
For each structure and v <= 99 we compute the minimum L by MILP and compare with every LJCR entry."""
import itertools, json, math, sys, time
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

def span(rows, q):
    """all codewords of the F_q span of rows (as tuples)."""
    words = {tuple([0] * len(rows[0]))}
    for r in rows:
        words = {tuple((a + c * b) % q for a, b in zip(w, r)) for w in words for c in range(q)}
    return words

def check_steiner(pts, blocks, t):
    cnt = {}
    for B in blocks:
        for T in itertools.combinations(sorted(B), t):
            cnt[T] = cnt.get(T, 0) + 1
    return len(cnt) == len(list(itertools.combinations(range(pts), t))) and set(cnt.values()) == {1}

def any_t_in_block(pts, blocks, t):
    need = set(itertools.combinations(range(pts), t))
    for B in blocks:
        for T in itertools.combinations(sorted(B), t):
            need.discard(T)
        if not need:
            return True
    return not need

S = []  # (name, npoints, blocks, t)
def vec(n):
    return [v for v in itertools.product([0, 1], repeat=n)]
# PG(n,2) subspaces: points = nonzero vectors of F_2^{n+1}; d-dim projective subspaces (vector dim d+1), t = d+1
for n in range(2, 7):
    P = [v for v in vec(n + 1) if any(v)]
    idx = {v: i for i, v in enumerate(P)}
    # hyperplanes (d = n-1) only, plus lines/planes for small n
    for d in range(1, n):
        if d != n - 1 and n > 4:
            continue
        subs = set()
        # enumerate subspaces via spans of d+1 independent points (random-free exhaustive for small sizes)
        if d == n - 1:
            for h in P:
                subs.add(frozenset(idx[x] for x in P if sum(a * b for a, b in zip(h, x)) % 2 == 0))
        else:
            for gens in itertools.combinations(P, d + 1):
                sp = span([list(g) for g in gens], 2)
                if len(sp) == 2 ** (d + 1):
                    subs.add(frozenset(idx[x] for x in sp if any(x)))
        S.append((f"PG({n},2) {d}-flats", len(P), [sorted(s) for s in subs], d + 1))
# AG(n,2) d-flats: any d+1 points lie in a d-flat, t = d+1
for n in range(2, 7):
    P = vec(n)
    idx = {v: i for i, v in enumerate(P)}
    for d in range(1, n):
        if d != n - 1 and n > 4:
            continue
        subs = set()
        if d == n - 1:
            for h in P:
                if not any(h):
                    continue
                for c in (0, 1):
                    subs.add(frozenset(idx[x] for x in P if sum(a * b for a, b in zip(h, x)) % 2 == c))
        else:
            for gens in itertools.combinations([v for v in P if any(v)], d):
                sp = span([list(g) for g in gens], 2)
                if len(sp) != 2 ** d:
                    continue
                for a in P:
                    subs.add(frozenset(idx[tuple((x + y) % 2 for x, y in zip(a, s))] for s in sp))
        S.append((f"AG({n},2) {d}-flats", len(P), [sorted(s) for s in subs], d + 1))
# projective / affine planes over prime fields (t = 2)
for q in (3, 5, 7):
    P = []
    for v in itertools.product(range(q), repeat=3):
        if any(v) and next(c for c in v if c) == 1:
            P.append(v)
    idx = {v: i for i, v in enumerate(P)}
    L = [sorted(idx[x] for x in P if sum(a * b for a, b in zip(h, x)) % q == 0) for h in P]
    S.append((f"PG(2,{q})", len(P), L, 2))
    A = list(itertools.product(range(q), repeat=2)); ia = {v: i for i, v in enumerate(A)}
    lines = set()
    for p1, p2 in itertools.combinations(A, 2):
        dvec = ((p2[0] - p1[0]) % q, (p2[1] - p1[1]) % q)
        lines.add(frozenset(ia[((p1[0] + c * dvec[0]) % q, (p1[1] + c * dvec[1]) % q)] for c in range(q)))
    S.append((f"AG(2,{q})", len(A), [sorted(l) for l in lines], 2))
# binary Golay code (extended QR code, length 24) -> S(5,8,24) and derived designs
Q23 = {(i * i) % 23 for i in range(1, 23)}
base = [1 if (i in Q23 or i == 0) else 0 for i in range(23)]
rows = [[base[(i - s) % 23] for i in range(23)] for s in range(23)]
rows = [r + [sum(r) % 2] for r in rows] + [[1] * 24]
# reduce to a basis
basis = []
for r in rows:
    cand = basis + [r]
    if len(span(cand, 2)) > len(span(basis, 2)) if basis else True:
        basis.append(r)
    if len(basis) == 12:
        break
G24 = span(basis, 2)
octads = [frozenset(i for i, c in enumerate(w) if c) for w in G24 if sum(w) == 8]
ok24 = len(G24) == 4096 and min(sum(w) for w in G24 if any(w)) == 8 and len(octads) == 759
if ok24 and check_steiner(24, octads, 5):
    S.append(("S(5,8,24)", 24, [sorted(o) for o in octads], 5))
    d1 = [sorted(i for i in o if i != 23) for o in octads if 23 in o]
    S.append(("S(4,7,23)", 23, d1, 4))
    d2 = [sorted(i for i in o if i != 22) for o in d1 if 22 in o]
    S.append(("S(3,6,22)", 22, d2, 3))
else:
    print("Golay-24 construction failed check", len(G24), len(octads), file=sys.stderr)
# ternary Golay code (extended QR code mod 11, length 12) -> S(5,6,12), S(4,5,11), S(3,4,10)
chi = {0: 0, 1: 1, 4: 1, 2: 2, 3: 2}   # quadratic character mod 5, -1 written as 2
Sm = [[0] + [1] * 5] + [[1] + [chi[(j - i) % 5] for j in range(5)] for i in range(5)]
rows3 = [[1 if c == r else 0 for c in range(6)] + Sm[r] for r in range(6)]
cur = span(rows3, 3)
found12 = None
if len(cur) == 729 and min(sum(1 for c in w if c) for w in cur if any(w)) == 6:
    hex_ = {frozenset(i for i, c in enumerate(w) if c) for w in cur if sum(1 for c in w if c) == 6}
    if len(hex_) == 132 and check_steiner(12, hex_, 5):
        found12 = hex_
if found12:
    S.append(("S(5,6,12)", 12, [sorted(h) for h in found12], 5))
    e1 = [sorted(i for i in h if i != 11) for h in found12 if 11 in h]
    S.append(("S(4,5,11)", 11, e1, 4))
    e2 = [sorted(i for i in h if i != 10) for h in e1 if 10 in h]
    S.append(("S(3,4,10)", 10, e2, 3))
else:
    print("ternary Golay construction failed", file=sys.stderr)

for name, n, B, t in S:
    assert any_t_in_block(n, B, t) if math.comb(n, t) < 3e6 else True, name
print(f"{len(S)} structures:", ", ".join(f"{nm} [{len(B)} blocks, t={t}]" for nm, n, B, t in S), flush=True)

lj = json.load(open(sys.argv[1]))
entries = []
for key, val in lj.items():
    v, k, t = map(int, key[2:-1].split(","))
    entries.append((v, k, t, val["size"]))

def minload(n, B, v):
    """min L s.t. integer w >= 0, sum w = v, every block load <= L."""
    nv = n + 1
    c = np.zeros(nv); c[-1] = 1
    A = np.zeros((len(B) + 1, nv)); lo = np.full(len(B) + 1, -np.inf); hi = np.zeros(len(B) + 1)
    for j, blk in enumerate(B):
        A[j, blk] = 1; A[j, -1] = -1
    A[-1, :n] = 1; lo[-1] = hi[-1] = v
    r = milp(c, constraints=LinearConstraint(A, lo, hi), integrality=np.ones(nv),
             bounds=Bounds(0, np.inf), options={"time_limit": 20})
    if r.status != 0 or r.x is None:
        return None, None
    return int(round(r.x[-1])), [int(round(x)) for x in r.x[:n]]

hits = []
t0 = time.time()
for name, n, B, t in S:
    b = len(B)
    rel = [(v, k, tt, sz) for (v, k, tt, sz) in entries if tt <= t and sz > b and k < v]
    vs = sorted({e[0] for e in rel})
    for v in vs:
        L, w = minload(n, B, v)
        if L is None:
            continue
        for (vv, k, tt, sz) in rel:
            if vv == v and k >= L:
                hits.append(dict(struct=name, v=v, k=k, t=tt, ljcr=sz, new=b, load=L, weights=w))
    print(f"{name}: {len(vs)} v-values checked, hits so far {len(hits)}, {time.time()-t0:.0f}s", flush=True)
json.dump(hits, open(sys.argv[2], "w"))
print("TOTAL HITS", len(hits))
for h in sorted(hits, key=lambda h: h['new'] - h['ljcr'])[:40]:
    print(f"C({h['v']},{h['k']},{h['t']}) <= {h['new']} (LJCR {h['ljcr']}) via {h['struct']}, load {h['load']}")
