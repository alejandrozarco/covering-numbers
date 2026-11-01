#!/usr/bin/env python3
"""Extension CNF for C(18,9,3) <= 15, root point 0 of degree 7 with link class idx.

Design points 0..17, root 0.  WLOG (see HANDOFF.md, audit/fable_m9_report.md): all 15 blocks are distinct 9-sets,
some point (the root) has degree exactly 7, so its 7 blocks are {0} + L_i where L = (L_1..L_7)
is a (17,8,2) covering (a link class from links_17_8.json; link point q = design point q+1).
The other 8 blocks avoid 0.  Variables y[j][p] (j < 8, p = 1..17): p in new block j.
  (S) |new block j| = 9
  (D) deg(p) = deg_L(p) + #new blocks through p >= 7   (link of p is a (17,8,2) covering)
  (T) every triple of {1..17} not inside a link block lies in a new block
  (P) [redundant] every pair {p,q}: b_L(pq) + #new blocks with p,q >= 3
Symmetry (lex-leader for Aut(L) x S_8 acting on Y, row-major vector):
  (R) y[j] >=lex y[j+1];  (A) vec(Y) >=lex vec(gY) for generators g of Aut(L).
usage: gen_ext9.py links.json idx out.cnf
"""
import sys, json
from itertools import combinations
sys.path.insert(0, __file__.rsplit("/", 1)[0] + "/../scripts")
from cnflib import CNF

V, K, B, R = 18, 9, 15, 7
M = B - R
# degree-7 pair-degree sequences (excess partitions of 5 occurring in links_17_8.json), decreasing lex:
# (6,5) > (6,4,4) > (5,5,4) > (5,4,4,4) > (4^5).  For root sequence D, every degree-7 point r has
# degseq(r) <=lex D, which IMPLIES: max <= D[0] and #(entries = D[0]) <= ROOTMU[D] (the number of
# entries D[0] in D), and for D=(6,4,4) also: no entry 6 together with an entry 5.  These implied
# conditions are exactly equivalent to <=lex D on the five possible sequences.
ROOTMU = {}
for _D in [(6, 5), (6, 4, 4), (5, 5, 4), (5, 4, 4, 4), (4, 4, 4, 4, 4)]:
    ROOTMU[tuple(list(_D) + [3] * (17 - len(_D)))] = _D.count(_D[0])


def build(link_blocks, aut_gens, q=None, n7=False, root=False, root2=False, nond7=(), skip=()):
    L = [frozenset(q + 1 for q in Bl) for Bl in link_blocks]
    assert len(L) == R and all(len(Bl) == K - 1 for Bl in L)
    P = list(range(1, V))
    c = CNF()
    y = [[c.new() for _ in P] for _ in range(M)]
    for j in range(M):
        c.exactly(y[j], K)
    for p in P:
        need = R - sum(p in Bl for Bl in L)
        if need > 0:
            c.atleast([y[j][p - 1] for j in range(M)], need)
    if q is not None:   # (Q) point q (deg_L(q) = 3) has degree exactly 7
        assert sum(q in Bl for Bl in L) == 3
        c.exactly([y[j][q - 1] for j in range(M)], 4)
    for p in nond7:     # (X) earlier q-orbits contain no degree-7 point: deg(p) >= 8
        need = R - sum(p in Bl for Bl in L)
        c.atleast([y[j][p - 1] for j in range(M)], need + 1)
    if n7:              # (N) >= 8 of the points 1..17 have degree exactly 7
        flags = []
        for p in P:
            need = R - sum(p in Bl for Bl in L)
            f = c.new()   # f -> new(p) <= need
            col = [y[j][p - 1] for j in range(M)]
            s = c._counter(col, need + 1)
            c.add([-f, -s[need + 1]])
            flags.append(f)
        c.atleast(flags, 8)
    ntrip = 0
    for T in combinations(P, 3):
        if any(set(T) <= Bl for Bl in L) or frozenset(T) in skip:   # skip: test hook only
            continue
        ntrip += 1
        c.add([c.and_aux([y[j][p - 1] for p in T]) for j in range(M)])
    # pair counters: cnt[(a,b)][t] <-> at least t new blocks contain a and b
    degL = {p: sum(p in Bl for Bl in L) for p in P}
    lamL = {}
    Dseq = sorted(degL.values(), reverse=True)
    Mx = Dseq[0]; mu = Dseq.count(Mx)
    cnt = {}
    for a, b in combinations(P, 2):
        lamL[a, b] = sum(a in Bl and b in Bl for Bl in L)
        cnt[a, b] = c._counter([c.and_def([y[j][a - 1], y[j][b - 1]]) for j in range(M)], M)
        need = 3 - lamL[a, b]
        if need > 0:
            c._assert_true(cnt[a, b][need])
    if root:
        # (O) root choice: WLOG the root maximises (lex) the descending pair-degree sequence
        # among degree-7 points; impose the implied conditions described at ROOTMU.
        def lam_ge(r, s, t):   # literal / constant for lambda_rs >= t
            if r == s:
                raise ValueError
            a, b = min(r, s), max(r, s)
            u = t - lamL[a, b]
            if u <= 0:
                return True
            if u > M:
                return False
            return cnt[a, b][u]
        for r in P:
            need = R - degL[r]
            d7 = -c._counter([y[j][r - 1] for j in range(M)], need + 1)[need + 1]  # new(r) <= need
            ge = {}
            for s in [0] + P:
                if s == r:
                    continue
                if s == 0:
                    ge[s] = {t: (degL[r] >= t) for t in range(3, 9)}
                else:
                    ge[s] = {t: lam_ge(r, s, t) for t in range(3, 9)}
            # max lambda <= Mx
            for s in ge:
                l = ge[s][Mx + 1]
                if l is True:
                    c.add([-d7])
                elif l is not False:
                    c.add([-d7, -l])
            if tuple(Dseq[:3]) == (6, 4, 4):   # also exclude (6,5): no 6 together with a 5
                for s1 in ge:
                    for s2 in ge:
                        if s1 == s2:
                            continue
                        a6, a5 = ge[s1][6], ge[s2][5]
                        if a6 is False or a5 is False:
                            continue
                        cl = [-d7] + ([-a6] if a6 is not True else []) + ([-a5] if a5 is not True else [])
                        c.add(cl)
            # at most ROOTMU[...] partners with lambda = Mx
            lits = []; const = 0
            for s in ge:
                l = ge[s][Mx]
                if l is True:
                    const += 1
                elif l is not False:
                    lits.append(l)
            lim = ROOTMU[tuple(Dseq)] - const
            if lim < 0:
                c.add([-d7])
            elif lim < len(lits):
                # d7 -> atmost(lits, lim)
                s2 = c._counter(lits, lim + 1)
                c.add([-d7, -s2[lim + 1]])
    if root2:
        # (O2) secondary root choice, only when Dseq = (4^5,3^12) (then every degree-7 point has
        # this sequence): among degree-7 points the root minimises (lex) the ascending sequence of
        # |B_i cap B_j| over the C(7,2) pairs of blocks through it.  Implied for every degree-7
        # point r: (i) every pair of blocks through r meets in >= xm points (xm = root minimum),
        # (ii) at most cm pairs of blocks through r meet in exactly xm points.
        assert tuple(Dseq) == (4,) * 5 + (3,) * 12
        # block list: root blocks ('L', a) with point sets {0} u L_a, new blocks ('N', j)
        rootx = [1 + len(L[a] & L[b]) for a, b in combinations(range(R), 2)]
        xm = min(rootx); cm = rootx.count(xm)
        # xle[(i,j)]: literal 'x_ij <= xm' for pairs involving a new block
        blocks = [('L', a) for a in range(R)] + [('N', j) for j in range(M)]
        def x_le(bi, bj):
            (ti, i), (tj, j) = bi, bj
            if ti == 'L' and tj == 'L':
                return 1 + len(L[i] & L[j]) <= xm
            if ti == 'L':      # root block i, new block j: intersection within L_i
                cs = c._counter([y[j][p - 1] for p in sorted(L[i])], xm + 1)
            else:
                cs = c._counter([c.and_def([y[i][p - 1], y[j][p - 1]]) for p in P], xm + 1)
            return -cs[xm + 1]           # true iff intersection <= xm
        def inblk(r, bl):
            t, i = bl
            return (r in L[i]) if t == 'L' else y[i][r - 1]
        xl = {}
        for bi, bj in combinations(blocks, 2):
            xl[bi, bj] = x_le(bi, bj)
        # 'intersection < xm' literal: need separate counter at level xm
        def x_lt(bi, bj):
            (ti, i), (tj, j) = bi, bj
            if ti == 'L' and tj == 'L':
                return 1 + len(L[i] & L[j]) < xm
            if ti == 'L':
                cs = c._counter([y[j][p - 1] for p in sorted(L[i])], xm)
            else:
                cs = c._counter([c.and_def([y[i][p - 1], y[j][p - 1]]) for p in P], xm)
            return -cs[xm]
        for r in P:
            need = R - degL[r]
            d7 = -c._counter([y[j][r - 1] for j in range(M)], need + 1)[need + 1]
            eq = []
            for bi, bj in combinations(blocks, 2):
                a, b = inblk(r, bi), inblk(r, bj)
                if a is False or b is False:
                    continue
                guard = [-d7] + ([-a] if a is not True else []) + ([-b] if b is not True else [])
                lt = x_lt(bi, bj)
                if lt is True:
                    c.add(guard)
                elif lt is not False:
                    c.add(guard + [-lt])
                le = xl[bi, bj]
                if le is False:
                    continue
                # e -> (a and b and le); we only need e >= (a and b and le) for an at-most bound
                e = c.new()
                c.add([e] + guard[1:] + ([-le] if le is not True else []) )
                eq.append(e)
            s2 = c._counter(eq, cm + 1)
            if s2[cm + 1] is not False:
                c.add([-d7, -s2[cm + 1]])
    for j in range(M - 1):
        c.lex_geq(y[j], y[j + 1])
    vec = [y[j][p - 1] for j in range(M) for p in P]
    for g in aut_gens:
        ginv = {g[p]: p for p in P}
        gvec = [y[j][ginv[p] - 1] for j in range(M) for p in P]
        if gvec != vec:
            c.lex_geq(vec, gvec)
    return c, y, ntrip


def stab_gens(masks, n, b, fixed):
    """generators of the stabiliser of link point `fixed` in Aut(link), via nauty"""
    import pynauty
    adj = {i: [] for i in range(n + b)}
    for q, m in enumerate(masks):
        for c in range(b):
            if (m >> c) & 1:
                adj[q].append(n + c)
    col = [{fixed}, set(range(n)) - {fixed}, set(range(n, n + b))]
    g = pynauty.Graph(n + b, adjacency_dict=adj, vertex_coloring=col)
    return [list(x) for x in pynauty.autgrp(g)[0]]


def main():
    data = json.load(open(sys.argv[1])); idx = int(sys.argv[2]); out = sys.argv[3]
    q = int(sys.argv[sys.argv.index("--q") + 1]) if "--q" in sys.argv else None   # design point
    n7 = "--n7" in sys.argv
    nond7 = [int(x) for x in sys.argv[sys.argv.index("--nond7") + 1].split(",")] if "--nond7" in sys.argv else []
    cl = data["classes"][idx]; n = data["n"]
    raw = cl["aut_gens"] if q is None else stab_gens(cl["masks"], n, data["b"], q - 1)
    gens = []
    for g in raw:
        gp = {p + 1: g[p] + 1 for p in range(n)}
        assert sorted(gp.values()) == list(range(1, n + 1))
        assert {frozenset(gp[x + 1] for x in Bl) for Bl in cl["blocks"]} == {frozenset(x + 1 for x in Bl) for Bl in cl["blocks"]}
        if q is not None:
            assert gp[q] == q
        gens.append(gp)
    c, y, ntrip = build(cl["blocks"], gens, q, n7, "--root" in sys.argv, "--root2" in sys.argv, nond7)
    c.write(out, comments=[f"C(18,9,3)<=15 extension, root degree 7, link class {idx}, q={q}, n7={n7} root={'--root' in sys.argv} nond7={nond7}",
                           f"link blocks (link point q = design point q+1): {cl['blocks']}",
                           f"y[j][p] = {y[0][0]} + j*17 + (p-1), j<8, p=1..17; uncovered triples {ntrip}"])
    print(f"class {idx} q={q}: vars {c.nv} clauses {len(c.clauses)} triples {ntrip}")


if __name__ == "__main__":
    main()
