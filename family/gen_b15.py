#!/usr/bin/env python3
"""CNF: does C(2m,m,3) <= 15 hold?  Dual form: 2m rows = subsets S_p of [15] (the blocks through p),
|S_p| >= 7, column sums <= m, pairwise |S_p ∩ S_q| >= 3, every 3 rows share a column.
Normalisation (m = 9, or generally when some row has size 7 and a |∩|=3 partner):
row0 = {0..6} (a row of size 7: exists since sum of row sizes <= 15m < 8*2m),
row1 = a |∩|=3 partner of row0 of size s1: {0,1,2} ∪ {7,...,7+s1-4}
(exists: sum_q λ_pq = sum_{j∈S_p}(|B_j|-1) <= 7(m-1), 2m-1 partners each >= 3, so some have λ = 3
 when 7(m-1) < 4(2m-1), i.e. always).  Rows >= 2 lex, columns lex inside blocks.
Usage: gen_b15.py m s1 out.cnf"""
import sys, itertools
sys.path.insert(0, '../scripts')
from cnflib import CNF
m, s1, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]; n = 2 * m; b = 15
F = CNF(); x = [[F.new() for j in range(b)] for i in range(n)]
for i in range(n): F.atleast(x[i], 7)
for j in range(b): F.atmost([x[i][j] for i in range(n)], m)
r0 = set(range(7)); r1 = {0, 1, 2} | set(range(7, 7 + s1 - 3))
for j in range(b):
    F.add([x[0][j] if j in r0 else -x[0][j]]); F.add([x[1][j] if j in r1 else -x[1][j]])
y = {}
for i, k in itertools.combinations(range(n), 2):
    y[i, k] = [F.and_def([x[i][j], x[k][j]]) for j in range(b)]
    F.atleast(y[i, k], 3)
for i, k, l in itertools.combinations(range(n), 3):
    zs = []
    for j in range(b):
        z = F.new(); F.add([-z, y[i, k][j]]); F.add([-z, x[l][j]]); zs.append(z)
    F.add(zs)
for i in range(2, n - 1): F.lex_geq(x[i], x[i + 1])
blocks = [list(range(0, 3)), list(range(3, 7)), list(range(7, 7 + s1 - 3)), list(range(7 + s1 - 3, 15))]
for blk in blocks:
    for j, j2 in zip(blk, blk[1:]):
        F.lex_geq([x[i][j] for i in range(2, n)], [x[i][j2] for i in range(2, n)])
F.write(out, [f'C(2m,m,3)<=15 m={m} row1 size {s1}'])
print(F.nv, len(F.clauses))
