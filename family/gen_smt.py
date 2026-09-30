#!/usr/bin/env python3
"""SMT-LIB2 (QF_LRA) instance for the Key Lemma counterexample search.
Boolean part = CNF (cnflib encodings): R rows = 7-subsets of [14] (duplicates allowed), pairwise |∩|>=3,
3-wise ∩ nonempty, no 8 rows pairwise |∩|<=3 (no SQS(8)-dual); row0={0..6}, row1={0,1,2,7,8,9,10}.
Real part: weights w_i >= 0, sum 1, w_0 >= w_k (k>=1), w_2>=w_3>=...; balance sum_i ite(x_ij, w_i, 0) = 1/2.
Also w_i <= 1/8 (valid).  Optional column lex within blocks {0,1,2},{3..6},{7..10},{11..13} over rows>=2
is NOT added (incompatible with weight-sorted rows?  It IS compatible: column swaps inside a block fix
rows 0,1 and do not change weights) -> added with --collex.
Usage: gen_smt.py R out.smt2 [--collex] [--sqs]"""
import sys, itertools, argparse
sys.path.insert(0, '../scripts')
from cnflib import CNF
ap = argparse.ArgumentParser(); ap.add_argument('R', type=int); ap.add_argument('out')
ap.add_argument('--collex', action='store_true'); ap.add_argument('--sqs', action='store_true')
ap.add_argument('--nopair', action='store_true'); ap.add_argument('--distinct', action='store_true'); ap.add_argument('--lexrows', action='store_true')
a = ap.parse_args(); R = a.R; n = 14
F = CNF()
x = [[F.new() for j in range(n)] for i in range(R)]
for i in range(R): F.exactly(x[i], 7)
r0 = [1]*7 + [0]*7; r1 = [1,1,1,0,0,0,0,1,1,1,1,0,0,0]
for j in range(n):
    F.add([x[0][j] if r0[j] else -x[0][j]])
    if not a.nopair: F.add([x[1][j] if r1[j] else -x[1][j]])
y = {}; e = {}
for i, k in itertools.combinations(range(R), 2):
    y[i, k] = [F.and_def([x[i][j], x[k][j]]) for j in range(n)]
    cnt = F._counter(y[i, k], 4)
    F._assert_true(cnt[3])
    ev = F.new(); e[i, k] = ev; F.add([ev, cnt[4]])
for i, k, l in itertools.combinations(range(R), 3):
    zs = []
    for j in range(n):
        z = F.new(); F.add([-z, y[i, k][j]]); F.add([-z, x[l][j]]); zs.append(z)
    F.add(zs)
if not a.sqs:
    for sub in itertools.combinations(range(R), 8):
        F.add([-e[p] for p in itertools.combinations(sub, 2)])
if a.lexrows:
    for i in range(2, R - 1): F.lex_geq(x[i], x[i + 1])
if a.distinct:
    for i, k in itertools.combinations(range(R), 2):
        d = []
        for j in range(n):
            v = F.new(); F.add([-v, x[i][j], x[k][j]]); F.add([-v, -x[i][j], -x[k][j]]); d.append(v)
        F.add(d)
if a.collex:
    blocks = [range(0,3), range(3,7), range(7,11), range(11,14)] if not a.nopair else [range(0,7), range(7,14)]
    lo = 1 if a.nopair else 2
    for blk in blocks:
        blk = list(blk)
        for j, j2 in zip(blk, blk[1:]):
            F.lex_geq([x[i][j] for i in range(lo, R)], [x[i][j2] for i in range(lo, R)])
with open(a.out, 'w') as f:
    f.write('(set-logic QF_LRA)\n')
    for v in range(1, F.nv + 1): f.write(f'(declare-const b{v} Bool)\n')
    for i in range(R): f.write(f'(declare-const w{i} Real)\n')
    lit = lambda l: f'b{l}' if l > 0 else f'(not b{-l})'
    for cl in F.clauses:
        f.write('(assert (or ' + ' '.join(lit(l) for l in cl) + (' false' if len(cl) < 2 else '') + '))\n')
    for i in range(R): f.write(f'(assert (and (>= w{i} 0) (<= w{i} (/ 1 8))))\n')
    f.write('(assert (= (+ ' + ' '.join(f'w{i}' for i in range(R)) + ') 1))\n')
    if not a.lexrows:
        for k in range(1, R): f.write(f'(assert (>= w0 w{k}))\n')
        for k in range(2 if not a.nopair else 1, R - 1): f.write(f'(assert (>= w{k} w{k+1}))\n')
    for j in range(n):
        f.write('(assert (= (+ ' + ' '.join(f'(ite b{x[i][j]} w{i} 0)' for i in range(R)) + ') (/ 1 2)))\n')
    f.write('(check-sat)\n(get-model)\n')
print('bool vars', F.nv, 'clauses', len(F.clauses))
