#!/usr/bin/env python3
"""Independent checker (shares no code with the generators): reads a block file
(one block per line, whitespace-separated point labels 0..v-1) and verifies it is
a t-(v,k,1) covering: all blocks have size k, labels in range, every t-subset of
{0..v-1} lies in some block.  usage: check_covering.py v k t blocks.txt"""
import sys
from itertools import combinations

v, k, t = map(int, sys.argv[1:4])
blocks = []
for line in open(sys.argv[4]):
    line = line.split("#")[0].strip()
    if not line:
        continue
    B = sorted(set(int(x) for x in line.split()))
    assert len(B) == k, f"block {B} has size {len(B)}"
    assert all(0 <= x < v for x in B)
    blocks.append(B)
covered = set()
for B in blocks:
    covered.update(combinations(B, t))
missing = [T for T in combinations(range(v), t) if T not in covered]
distinct = len(set(map(tuple, blocks)))
print(f"{len(blocks)} blocks ({distinct} distinct) of size {k} on {v} points;"
      f" uncovered {t}-sets: {len(missing)}")
print("VALID COVERING" if not missing else f"NOT A COVERING, e.g. {missing[:3]}")
sys.exit(0 if not missing else 1)
