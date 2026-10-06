#!/usr/bin/env python3
"""Link classification via nauty's genbg (independent of enum_links/classify_links).

A t'-(n,kk,1) covering with r blocks, in dual form, is a bipartite graph with
first class = r blocks (degree exactly kk) and second class = n points (degree >= dmin);
for t' = 2 "every pair of points is covered" is exactly genbg's -Y1 (two vertices of the
second class have >= 1 common neighbour).  genbg generates every such bicoloured graph
exactly once up to colour-preserving isomorphism (McKay's canonical augmentation), so the
output is a complete, irredundant list of covering classes.  Validated against the
enum_links/classify_links pipeline: (16,7,2;8) 185, (19,9,2;7) 2132, (15,7,2;7) 68,
(9,4,2;8) 17 classes.
For t' = 3 we run genbg with -Y{ceil((n-2)/(kk-2))} (necessary: the blocks through two points
p,q, minus p,q, must cover the other n-2 points with (kk-2)-sets) and then FILTER for "every
three points have a common block".

Output JSON in the classify_links.py format (fields used by gen_ext.py: blocks, degseq,
aut_gens [pynauty generators on points 0..n-1 then blocks n..n+r-1], masks, aut).
usage: genbg_links.py n kk r tprime dmin out.json [res/mod] [--from file.g6]
"""
import os, sys, json, subprocess
from collections import Counter
import pynauty

GENBG = os.environ.get("GENBG", "genbg")   # nauty 2.9.3 was used


def g6_decode(s):
    s = s.strip()
    data = [ord(c) - 63 for c in s]
    if data[0] == 63:          # n >= 63 (not used here)
        n = (data[1] << 12) | (data[2] << 6) | data[3]
        data = data[4:]
    else:
        n = data[0]
        data = data[1:]
    bits = []
    for x in data:
        for i in range(5, -1, -1):
            bits.append((x >> i) & 1)
    adj = [set() for _ in range(n)]
    pos = 0
    for j in range(1, n):
        for i in range(j):
            if bits[pos]:
                adj[i].add(j)
                adj[j].add(i)
            pos += 1
    return n, adj


def graph_of(masks, b):
    n = len(masks)
    adj = {i: [] for i in range(n + b)}
    for q, m in enumerate(masks):
        for c in range(b):
            if (m >> c) & 1:
                adj[q].append(n + c)
    return pynauty.Graph(n + b, directed=False, adjacency_dict=adj,
                         vertex_coloring=[set(range(n)), set(range(n, n + b))])


def main():
    n, kk, r, tp, dmin = map(int, sys.argv[1:6])
    out = sys.argv[6]
    rest = sys.argv[7:]
    src = None
    if "--from" in rest:
        src = rest[rest.index("--from") + 1]
    resmod = [a for a in rest if "/" in a and not a.startswith("/") and a != src]
    if src:
        lines = open(src).read().split()
    else:
        cmd = [GENBG if n + r <= 32 else GENBG + "L", "-q", f"-Y{1 if tp == 2 else -(-(n - 2) // (kk - 2))}", f"-d{kk}:{dmin}", f"-D{kk}:{r}", str(r), str(n),
               f"{r * kk}:{r * kk}"] + resmod
        lines = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.split()
    res = []
    nfilt = 0
    certs = set()
    for s in lines:
        N, adj = g6_decode(s)
        assert N == n + r
        blocks = [sorted(q - r for q in adj[c]) for c in range(r)]   # genbg: blocks first
        assert all(len(B) == kk for B in blocks)
        masks = [sum(1 << c for c in range(r) if (r + q) in adj[c]) for q in range(n)]
        if tp == 3:
            from itertools import combinations
            if any(masks[a] & masks[b2] & masks[c] == 0 for a, b2, c in combinations(range(n), 3)):
                nfilt += 1
                continue
        # sanity: pairs covered
        from itertools import combinations
        assert all(masks[a] & masks[b2] for a, b2 in combinations(range(n), 2))
        g = graph_of(masks, r)
        cert = pynauty.certificate(g)
        assert cert not in certs, "genbg produced isomorphic duplicates?!"
        certs.add(cert)
        gens, g1, g2, orbits, numorb = pynauty.autgrp(g)
        aut = int(round(g1 * 10 ** g2))
        degs = sorted((bin(m).count("1") for m in masks), reverse=True)
        res.append({"masks": masks, "blocks": blocks, "aut": aut, "degseq": degs,
                    "distinct_blocks": len(set(map(tuple, blocks))) == r,
                    "aut_gens": [list(x) for x in gens]})
    res.sort(key=lambda x: (x["degseq"], x["masks"]))
    print(f"genbg objects {len(lines)}, filtered (not {tp}-wise) {nfilt}, classes {len(res)}")
    for d, c in sorted(Counter(tuple(x["degseq"]) for x in res).items()):
        print("  degseq", d, ":", c)
    print("  (M,mu):", dict(Counter((x["degseq"][0], x["degseq"].count(x["degseq"][0])) for x in res)))
    print("  classes with repeated blocks:", sum(not x["distinct_blocks"] for x in res))
    json.dump({"n": n, "b": r, "k": kk, "tprime": tp, "source": "genbg", "classes": res}, open(out, "w"))


if __name__ == "__main__":
    main()
