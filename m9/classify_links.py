#!/usr/bin/env python3
"""Isomorph rejection for the output of enum_links (dual representation).

Input lines: n masks (subset of the b blocks containing each point).
Two coverings are isomorphic iff the point-block incidence graphs are isomorphic
with points and blocks kept as separate colour classes; pynauty (nauty) gives a
canonical certificate.  For each class we record a representative, |Aut|, and
the number of enumerator leaves hitting it, and we check the orbit-stabiliser
identity
    leaves(class) = (b!/|A_b|) * t / C(b, smin)
where A_b = Aut restricted to blocks (= |Aut| / prod(multiplicity!)), t = number
of distinct smin-subsets that occur as point-sets.  This holds because the
enumerator lists every block-relabelled multiset that contains {0..smin-1}
exactly once.  Agreement over all classes is an independent consistency check
of both the enumeration and the canonical forms.

usage: classify_links.py n b k smin raw.txt out.json [fixfirst=1]
"""
import sys, json
from math import comb, factorial
from collections import Counter
import pynauty


def graph_of(masks, b):
    n = len(masks)
    adj = {i: [] for i in range(n + b)}
    for q, m in enumerate(masks):
        for c in range(b):
            if (m >> c) & 1:
                adj[q].append(n + c)
    g = pynauty.Graph(n + b, directed=False, adjacency_dict=adj,
                      vertex_coloring=[set(range(n)), set(range(n, n + b))])
    return g


def main():
    n, b, k, smin = map(int, sys.argv[1:5])
    raw, out = sys.argv[5], sys.argv[6]
    fix = int(sys.argv[7]) if len(sys.argv) > 7 else 1
    classes = {}
    nlines = 0
    with open(raw) as f:
        for line in f:
            masks = tuple(int(x) for x in line.split())
            assert len(masks) == n
            nlines += 1
            cert = pynauty.certificate(graph_of(masks, b))
            c = classes.get(cert)
            if c is None:
                classes[cert] = [masks, 1]
            else:
                c[1] += 1
            if nlines % 200000 == 0:
                print(f"  {nlines} lines, {len(classes)} classes", file=sys.stderr, flush=True)
    res = []
    total_check = 0
    for cert, (masks, cnt) in classes.items():
        gens, grpsize1, grpsize2, orbits, numorb = pynauty.autgrp(graph_of(masks, b))
        aut = int(round(grpsize1 * 10 ** grpsize2))
        mult = Counter(masks)
        kern = 1
        for v in mult.values():
            kern *= factorial(v)
        assert aut % kern == 0
        ab = aut // kern
        t = sum(1 for m in mult if bin(m).count("1") == smin)
        if fix:
            num = factorial(b) * t
            den = ab * comb(b, smin)
        else:                    # every relabelled multiset is listed once
            num, den = factorial(b), ab
        assert num % den == 0, (masks, aut, kern, t)
        expect = num // den
        ok = (expect == cnt)
        total_check += ok
        blocks = [[q for q in range(n) if (masks[q] >> c) & 1] for c in range(b)]
        degs = sorted((bin(m).count("1") for m in masks), reverse=True)
        res.append({"masks": list(masks), "blocks": blocks, "aut": aut, "aut_blocks": ab,
                    "leaves": cnt, "expected_leaves": expect, "degseq": degs,
                    "aut_gens": [list(g) for g in gens]})
    res.sort(key=lambda r: (r["degseq"], r["masks"]))
    print(f"lines {nlines}, classes {len(res)}, orbit-stabiliser OK for {total_check}/{len(res)}")
    ds = Counter(tuple(r["degseq"]) for r in res)
    for d, c in sorted(ds.items()):
        print("  degseq", d, ":", c)
    json.dump({"n": n, "b": b, "k": k, "smin": smin, "lines": nlines,
               "classes": res}, open(out, "w"))
    assert total_check == len(res)


if __name__ == "__main__":
    main()
