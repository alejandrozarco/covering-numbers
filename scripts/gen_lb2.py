#!/usr/bin/env python3
"""CNF for 'there is a 2-(v,k,1) covering with b blocks' (used with v=16,k=7,b=7
to certify C(16,7,2) >= 8, the only tabulated input of the C(17,8,3) argument).

x[i][p]: point p in block i (b x v matrix).  Each row has exactly k ones; every
pair of points has a common row (aux z -> x x).  Repeated blocks are allowed, so
UNSAT also excludes coverings with fewer than b blocks (pad with any blocks).
Symmetry breaking: the problem is invariant under all row permutations and all
column permutations; double-lex (rows lex-nonincreasing, columns
lex-nonincreasing) is sound for such matrix models (Flener et al. 2002: every
orbit contains a matrix with lex-ordered rows and columns).
Redundant (implied) constraint: every point lies in >= ceil((v-1)/(k-1)) rows.
usage: gen_lb2.py v k b out.cnf"""
import sys
from itertools import combinations
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from cnflib import CNF

v, k, b = map(int, sys.argv[1:4])
c = CNF()
x = [[c.new() for _ in range(v)] for _ in range(b)]
for i in range(b):
    c.exactly(x[i], k)
for p, q in combinations(range(v), 2):
    c.add([c.and_aux([x[i][p], x[i][q]]) for i in range(b)])
smin = -(-(v - 1) // (k - 1))
for p in range(v):
    c.atleast([x[i][p] for i in range(b)], smin)
for i in range(b - 1):
    c.lex_geq(x[i], x[i + 1])
for p in range(v - 1):
    c.lex_geq([x[i][p] for i in range(b)], [x[i][p + 1] for i in range(b)])
c.write(sys.argv[4], comments=[f"2-({v},{k},1) covering with {b} blocks? double-lex"])
print(f"vars {c.nv} clauses {len(c.clauses)}")
