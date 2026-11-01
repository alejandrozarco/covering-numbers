#!/usr/bin/env python3
"""Positive/negative controls for gen_ext9.build: take 15-block (18,9,3) near-coverings (SA, exactly
one uncovered triple T), relabel so that a degree-7 root 0 (not on T) is the root, fix the new
blocks by unit clauses, omit only the clause of T, and compare CaDiCaL's verdict with an
independent evaluation of the constraints from their definitions, for every flag combination."""
import sys, itertools, subprocess, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ext9 as G
CAD = os.path.expanduser("~/sat/cadical/build/cadical")

def solve(c):
    fd, fn = tempfile.mkstemp(suffix=".cnf"); os.close(fd)
    c.write(fn)
    r = subprocess.run(f"nice -n 19 {CAD} -q {fn}", shell=True, capture_output=True, text=True)
    os.remove(fn)
    return "s SATISFIABLE" in r.stdout

def main():
    agree = total = nsat = 0
    for fn in sys.argv[1:]:
        lines = open(fn).read().split("\n")
        if not lines[0].startswith("final unc 1"):
            continue
        blocks = [set(map(int, l.split())) for l in lines[1:] if l.strip()]
        assert len(blocks) == 15 and all(len(b) == 9 for b in blocks)
        unc = [T for T in itertools.combinations(range(18), 3) if not any(set(T) <= b for b in blocks)]
        assert len(unc) == 1; T = set(unc[0])
        deg = [sum(p in b for b in blocks) for p in range(18)]
        lam = lambda a, b: sum(a in B and b in B for B in blocks)
        dseq = lambda r: tuple(sorted((lam(r, s) for s in range(18) if s != r), reverse=True))
        for root in [p for p in range(18) if deg[p] == 7 and p not in T]:
            others = [p for p in range(18) if p != root]
            lab = {root: 0}; lab.update({p: i + 1 for i, p in enumerate(others)})
            B2 = [{lab[p] for p in b} for b in blocks]
            L = [sorted(p - 1 for p in b - {0}) for b in B2 if 0 in b]
            N = [b for b in B2 if 0 not in b]
            if len(L) != 7 or len(N) != 8:
                continue
            Tl = frozenset(lab[p] for p in T)
            d2 = {lab[p]: deg[p] for p in range(18)}
            l2 = lambda a, b: sum(a in B and b in B for B in B2)
            D = tuple(sorted((l2(0, s) for s in range(1, 18)), reverse=True))
            if D not in G.ROOTMU:
                continue
            P = range(1, 18)
            for q in [p for p in P if d2[p] == 7 and l2(0, p) == 3][:2] + [None]:
                for n7, root_, nd in itertools.product([False, True], [False, True], [(), None]):
                    if nd is None:   # nond7 = first 3 points of degree >= 8, or 3 points incl. a degree-7 one
                        cand = [p for p in P if d2[p] >= 8][:2] + [p for p in P if d2[p] == 7 and p != q][:1]
                        nd = tuple(cand)
                    # independent evaluation
                    ok = all(d2[p] >= 7 for p in P)
                    ok &= all(l2(a, b) >= 3 for a, b in itertools.combinations(P, 2))
                    if q is not None:
                        ok &= d2[q] == 7
                    if n7:
                        ok &= sum(d2[p] == 7 for p in P) >= 8
                    ok &= all(d2[p] >= 8 for p in nd)
                    if root_:
                        Mx = D[0]; mu = G.ROOTMU[D]
                        for r in P:
                            if d2[r] == 7:
                                ls = [l2(r, s) for s in range(18) if s != r]
                                ok &= max(ls) <= Mx and ls.count(Mx) <= mu
                    c, y, _ = G.build(L, [], q, n7, root_, False, nd, skip={Tl})
                    rows = sorted(([1 if p in b else 0 for p in P] for b in N), reverse=True)
                    for j in range(8):
                        for i, p in enumerate(P):
                            c.add([y[j][i] if rows[j][i] else -y[j][i]])
                    res = solve(c)
                    total += 1; agree += (res == ok); nsat += res
                    if res != ok:
                        print("DISAGREE", fn, root, q, n7, root_, nd, res, ok)
            break
    print(f"controls: {total}, agree {agree}, SAT {nsat}")

main()
