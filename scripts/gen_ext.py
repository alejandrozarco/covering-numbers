#!/usr/bin/env python3
"""Extension instance E(L): does the optimal link L extend to a 3-(v,k,1) covering
with b blocks (zero-slack case)?

Setting (see JOURNAL.md, counting.py): every point has degree exactly r = |L|,
so the blocks through the root point 0 are {0} + B (B in L) and the other
m = b - r blocks avoid 0.  Link point q (0-based) is design point q+1.

Variables y[j][p] (j < m new blocks, p = 1..v-1): p in new block j.
Constraints (all necessary):
  (S) |new block j| = k                                   (exact cardinality)
  (D) sum_j y[j][p] = r - deg_L(p)                        (b(p) = r exactly)
  (T) every triple of {1..v-1} not inside a link block lies in a new block
      (triples through 0 are covered by L, which covers all pairs)
  (P) [optional, redundant] every pair {p,q}: b_L(pq) + #new blocks with p,q
      >= smin = ceil((v-2)/(k-2))  -- implied by (T) (the blocks through p,q
      minus p,q must cover the other v-2 points with (k-2)-sets).
Symmetry breaking (sound, lex-leader for the group H = Aut(L) x S_m acting on Y,
all constraints being H-invariant; the lex-greatest member of every H-orbit of
solutions satisfies every constraint vec(Y) >= vec(hY), h in H):
  (R) y[j] >=lex y[j+1]           (h = adjacent transposition of new blocks)
  (A) [optional] vec(Y) >=lex vec(gY) for generators g of Aut(L) (point action),
      where vec reads Y row-major (j, then p) -- the same order as (R).
usage: gen_ext.py v k b links.json idx out.cnf [--pairs] [--aut]
"""
import sys, json
from itertools import combinations
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from cnflib import CNF


def build(v, k, b, link_blocks, pairs=False, aut_gens=None, pair_hi=None, mu=None, triples=True, exact_deg=True):
    r = len(link_blocks)
    m = b - r
    L = [frozenset(q + 1 for q in B) for B in link_blocks]
    assert all(len(B) == k - 1 for B in L)
    P = list(range(1, v))
    deg = {p: sum(p in B for B in L) for p in P}
    c = CNF()
    y = [[c.new() for _ in P] for _ in range(m)]   # y[j][p-1]
    for j in range(m):
        c.exactly(y[j], k)
    for p in P:
        if exact_deg:
            c.exactly([y[j][p - 1] for j in range(m)], r - deg[p])
        else:   # non-zero-slack search (e.g. b = 18 for C(17,8,3)): b(p) >= r only
            c.atleast([y[j][p - 1] for j in range(m)], r - deg[p])
    ntrip = 0
    for T in (combinations(P, 3) if triples else []):
        if any(set(T) <= B for B in L):
            continue
        ntrip += 1
        zs = [c.and_aux([y[j][p - 1] for p in T]) for j in range(m)]
        c.add(zs)
    if pairs:
        # (P) pair degrees: smin <= b(pq) <= pair_hi, and (M) every point has at most
        # mu partners q with b(pq) = pair_hi  (root-choice constraints, see header)
        smin = -(-(v - 2) // (k - 2))
        hi = pair_hi if pair_hi is not None else 10 ** 9
        topflag = {}
        for p, q in combinations(P, 2):
            bl = sum(p in B and q in B for B in L)
            lo_new = smin - bl
            hi_new = hi - bl
            if hi_new < 0:
                c.add([])
                continue
            ws = [c.and_def([y[j][p - 1], y[j][q - 1]]) for j in range(m)]
            if lo_new > m:
                c.add([])
                continue
            top = min(m, max(lo_new, hi_new + 1))
            s = c._counter(ws, top)
            if lo_new > 0:
                c._assert_true(s[lo_new])
            if hi_new + 1 <= m:
                c._assert_false(s[hi_new + 1])
            if mu is not None:
                # literal for b(pq) == hi  <=>  at least hi_new new blocks
                if hi_new <= 0:
                    topflag[(p, q)] = None          # constant true
                elif hi_new <= top:
                    topflag[(p, q)] = s[hi_new]
                else:
                    topflag[(p, q)] = False
        if mu is not None:
            for p in P:
                const = 1 if deg[p] == hi else 0    # partner 0: b(0p) = deg_L(p)
                lits = []
                for q in P:
                    if q == p:
                        continue
                    f = topflag[(min(p, q), max(p, q))]
                    if f is None:
                        const += 1
                    elif f is not False:
                        lits.append(f)
                c.atmost(lits, mu - const)
    for j in range(m - 1):
        c.lex_geq(y[j], y[j + 1])
    if aut_gens:
        vec = [y[j][p - 1] for j in range(m) for p in P]
        for g in aut_gens:          # g: permutation of design points 1..v-1 (dict)
            # (gY)[j][p] = Y[j][g^{-1} p]
            ginv = {g[p]: p for p in P}
            gvec = [y[j][ginv[p] - 1] for j in range(m) for p in P]
            if gvec != vec:
                c.lex_geq(vec, gvec)
    return c, y, ntrip


def main():
    v, k, b = map(int, sys.argv[1:4])
    data = json.load(open(sys.argv[4]))
    idx = int(sys.argv[5])
    out = sys.argv[6]
    pairs = "--pairs" in sys.argv
    aut = "--aut" in sys.argv
    cl = data["classes"][idx]
    n = data["n"]
    gens = None
    if aut:
        gens = []
        for g in cl["aut_gens"]:
            # pynauty generator on n points + b blocks; project to points, shift by 1
            gp = {q + 1: g[q] + 1 for q in range(n)}
            assert sorted(gp.values()) == list(range(1, n + 1))
            gens.append(gp)
    pair_hi = mu = None
    if "--root" in sys.argv:
        # root = point on a pair of maximum degree M maximising the number mu of
        # M-partners; M, mu read off the root link's degree sequence
        pair_hi = max(cl["degseq"])
        mu = cl["degseq"].count(pair_hi)
    c, y, ntrip = build(v, k, b, cl["blocks"], pairs or pair_hi is not None, gens, pair_hi, mu)
    c.write(out, comments=[f"extension instance v={v} k={k} b={b} link class {idx}",
                           f"link blocks (link points 0-based, design point = +1): {cl['blocks']}",
                           f"y[j][p] = {y[0][0]} + j*{v-1} + (p-1)  for j<{b-len(cl['blocks'])}, p=1..{v-1}",
                           f"options pairs={pairs} aut={aut} pair_hi={pair_hi} mu={mu}; uncovered triples {ntrip}"])
    print(f"class {idx}: vars {c.nv} clauses {len(c.clauses)} triples {ntrip}")


if __name__ == "__main__":
    main()
