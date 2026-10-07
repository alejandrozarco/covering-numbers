#!/usr/bin/env python3
"""Weighted blow-up scan, part 2: geometries over GF(3), GF(5), GF(7) and more flat dimensions over GF(2).
Same method as blowscan.py: a structure (points X, blocks Y_j) in which any t points lie in a common block gives,
for integer weights w_x >= 0 with sum v and max block load L, C(v,k,t) <= #blocks for every k >= L.
Flats: in PG(n,q) any d+1 points lie in a d-flat; in AG(n,q) any d+1 points lie in an affine d-flat.
MILP limit 120 s per (structure, v); instances that do not finish optimal are logged as SKIPPED (not silently).
usage: blowscan2.py coverdata.json out.json [prefixes]  (writes out.json.hits.jsonl as it goes, out.json, out.json.DONE)"""
import itertools, json, sys, time
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

def vecs(n, q): return list(itertools.product(range(q), repeat=n))
def normal(v, q):
    for c in v:
        if c:
            inv = pow(c, q - 2, q); return tuple(x * inv % q for x in v)
def rank(rows, q):
    M = [list(r) for r in rows]; r = 0; cols = len(M[0]) if M else 0
    for c in range(cols):
        piv = next((i for i in range(r, len(M)) if M[i][c] % q), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]; inv = pow(M[r][c], q - 2, q); M[r] = [x * inv % q for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] % q:
                f = M[i][c]; M[i] = [(a - f * b) % q for a, b in zip(M[i], M[r])]
        r += 1
    return r

def pg_flats(n, q, d):
    P = sorted({normal(v, q) for v in vecs(n + 1, q) if any(v)}); idx = {p: i for i, p in enumerate(P)}
    if d == n - 1:
        return P, [sorted(idx[x] for x in P if sum(a * b for a, b in zip(h, x)) % q == 0) for h in P]
    subs = set()
    for gens in itertools.combinations(P, d + 1):
        if rank(gens, q) < d + 1: continue
        sp = set()
        for co in itertools.product(range(q), repeat=d + 1):
            w = tuple(sum(c * g[i] for c, g in zip(co, gens)) % q for i in range(n + 1))
            if any(w): sp.add(idx[normal(w, q)])
        subs.add(frozenset(sp))
    return P, [sorted(s) for s in subs]

def ag_hyperplanes(n, q):
    P = vecs(n, q); idx = {p: i for i, p in enumerate(P)}
    H = sorted({normal(h, q) for h in vecs(n, q) if any(h)})
    return P, [sorted(idx[x] for x in P if sum(a * b for a, b in zip(h, x)) % q == c) for h in H for c in range(q)]

S = []
for q, ns in ((3, (2, 3, 4)), (5, (2, 3)), (7, (2,))):
    for n in ns:
        P, B = pg_flats(n, q, n - 1); S.append((f"PG({n},{q}) hyperplanes", len(P), B, n))
        P, B = ag_hyperplanes(n, q); S.append((f"AG({n},{q}) hyperplanes", len(P), B, n))
P, B = pg_flats(3, 3, 1); S.append(("PG(3,3) lines", len(P), B, 2))
P, B = pg_flats(5, 2, 2); S.append(("PG(5,2) planes", len(P), B, 3))
P, B = pg_flats(4, 2, 2); S.append(("PG(4,2) planes", len(P), B, 3))
for nm, n, B, t in S:   # sanity: any t points lie in a block (exhaustive where cheap)
    if len(list(itertools.combinations(range(n), t))) < 2e6:
        cov = [set(b) for b in B]
        assert all(any(set(T) <= c for c in cov) for T in itertools.combinations(range(n), t)), nm
print(f"{len(S)} structures:", ", ".join(f"{nm} [{n} pts, {len(B)} blocks, t={t}]" for nm, n, B, t in S), flush=True)

lj = json.load(open(sys.argv[1])); E = []
for key, val in lj.items():
    v, k, t = map(int, key[2:-1].split(",")); E.append((v, k, t, val["size"]))
def minload(n, B, v):
    nv = n + 1; c = np.zeros(nv); c[-1] = 1
    A = np.zeros((len(B) + 1, nv)); lo = np.full(len(B) + 1, -np.inf); hi = np.zeros(len(B) + 1)
    for j, blk in enumerate(B): A[j, blk] = 1; A[j, -1] = -1
    A[-1, :n] = 1; lo[-1] = hi[-1] = v
    r = milp(c, constraints=LinearConstraint(A, lo, hi), integrality=np.ones(nv), bounds=Bounds(0, np.inf),
             options={"time_limit": 120})
    if r.status != 0 or r.x is None: return None, None
    return int(round(r.x[-1])), [int(round(x)) for x in r.x[:n]]
hits, skipped, t0 = [], [], time.time()
only = sys.argv[3].split(",") if len(sys.argv) > 3 else None   # optional: comma-separated structure-name prefixes
inc = open(sys.argv[2] + ".hits.jsonl", "a")
for nm, n, B, t in S:
    if only and not any(nm.startswith(o) for o in only): continue
    rel = [e for e in E if e[2] <= t and e[3] > len(B) and e[1] < e[0]]
    for v in sorted({e[0] for e in rel}):
        L, w = minload(n, B, v)
        if L is None: skipped.append((nm, v)); continue
        for (vv, k, tt, sz) in rel:
            if vv == v and k >= L:
                h = dict(struct=nm, v=v, k=k, t=tt, ljcr=sz, new=len(B), load=L, weights=w); hits.append(h)
                inc.write(json.dumps(h) + "\n"); inc.flush()
    print(f"{nm}: hits so far {len(hits)}, skipped {len(skipped)}, {time.time()-t0:.0f}s", flush=True)
json.dump(dict(hits=hits, skipped=skipped), open(sys.argv[2], "w"))
open(sys.argv[2] + ".DONE", "w").write(f"{len(hits)} hits, {len(skipped)} skipped\n")
for h in sorted(hits, key=lambda h: h['new'] - h['ljcr'])[:40]:
    print(f"C({h['v']},{h['k']},{h['t']}) <= {h['new']} (LJCR {h['ljcr']}) via {h['struct']}, load {h['load']}")
