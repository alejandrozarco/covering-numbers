#!/usr/bin/env python3
"""Build the covering for a blowscan2 hit: replace geometric point x by w_x new points, take the structure's blocks
(hyperplanes) and pad each to k points with the smallest labels not yet in it. Point and block orders are the ones
blowscan2.py uses. usage: build_blowup.py hits.jsonl INDEX out.txt"""
import itertools, json, sys
def vecs(n, q): return list(itertools.product(range(q), repeat=n))
def normal(v, q):
    for c in v:
        if c:
            inv = pow(c, q - 2, q); return tuple(x * inv % q for x in v)
def structure(name):
    kind, rest = name.split("(", 1); n, q = map(int, rest.split(")")[0].split(","))
    assert name.endswith("hyperplanes")
    if kind == "PG":
        P = sorted({normal(v, q) for v in vecs(n + 1, q) if any(v)})
        return P, [[i for i, x in enumerate(P) if sum(a * b for a, b in zip(h, x)) % q == 0] for h in P]
    P = vecs(n, q); H = sorted({normal(h, q) for h in vecs(n, q) if any(h)})
    return P, [[i for i, x in enumerate(P) if sum(a * b for a, b in zip(h, x)) % q == c] for h in H for c in range(q)]
h = [json.loads(l) for l in open(sys.argv[1])][int(sys.argv[2])]
P, B = structure(h["struct"]); w = h["weights"]; v, k = h["v"], h["k"]
assert len(w) == len(P) and sum(w) == v
lab, nxt = [], 0
for x in range(len(P)): lab.append(list(range(nxt, nxt + w[x]))); nxt += w[x]
with open(sys.argv[3], "w") as f:
    f.write(f"# C({v},{k},{h['t']}) <= {len(B)}: weighted blow-up of {h['struct']} (blowscan2.py); weights in build log\n")
    for blk in B:
        S = sorted(p for x in blk for p in lab[x]); assert len(S) <= k
        pad = [p for p in range(v) if p not in set(S)][:k - len(S)]
        f.write(" ".join(map(str, sorted(S + pad))) + "\n")
print(h["struct"], f"C({v},{k},{h['t']}) <= {len(B)} (LJCR v1.2: {h['ljcr']}), max load {h['load']}")
