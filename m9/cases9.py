#!/usr/bin/env python3
"""List the (link class, q) cases: q = one representative (design point = link point + 1, the
smallest) of each Aut(L)-orbit of link points of link degree 3.  Writes cases.json."""
import json, pynauty
d = json.load(open('links_17_8.json')); n, b = d['n'], d['b']
cases = []
for i, cl in enumerate(d['classes']):
    masks = cl['masks']
    adj = {v: [] for v in range(n + b)}
    for q, m in enumerate(masks):
        for c in range(b):
            if m >> c & 1:
                adj[q].append(n + c)
    g = pynauty.Graph(n + b, adjacency_dict=adj, vertex_coloring=[set(range(n)), set(range(n, n + b))])
    orb = pynauty.autgrp(g)[3]
    # orbits of link points of link degree 3 (lambda_{root,q} = 3), largest first.
    # Case k: q = min of orbit k is a degree-7 point, and orbits 1..k-1 contain no degree-7
    # point (design points listed in nond7 have degree >= 8).  Since at most 9 points have
    # degree >= 8, cases with |nond7| > 9 are impossible and are not generated.
    orbs = {}
    for q in range(n):
        if bin(masks[q]).count('1') == 3:
            orbs.setdefault(orb[q], []).append(q + 1)
    ol = sorted(orbs.values(), key=lambda o: (-len(o), o))
    before = []
    for o in ol:
        if len(before) > 9:
            break
        cases.append([i, o[0], sorted(before)])
        before += o
json.dump(cases, open('cases.json', 'w'))
print(len(cases), 'cases')
