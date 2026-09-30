#!/usr/bin/env python3
"""SMT-LIB2 (QF_LRA): basecnf Boolean part + weights w_i in [0,1/8], sum 1, column balance
sum_i ite(x_ij, w_i, 0) = 1/2.  Usage: gen_smt2.py R case out.smt2 [--sqs] [--distinct]"""
import sys, argparse
from basecnf import build
ap = argparse.ArgumentParser(); ap.add_argument('R', type=int); ap.add_argument('case'); ap.add_argument('out')
ap.add_argument('--sqs', action='store_true'); ap.add_argument('--distinct', action='store_true'); ap.add_argument('--maxw', action='store_true', help='row0 has max weight'); ap.add_argument('--not1', action='store_true'); ap.add_argument('--maxpartner', action='store_true'); ap.add_argument('--not1pair', action='store_true'); ap.add_argument('--maxthird', action='store_true'); ap.add_argument('--avoid0', action='store_true'); ap.add_argument('--pos', action='store_true', help='all weights strictly positive'); ap.add_argument('--notrade', action='store_true'); ap.add_argument('--colcard', action='store_true'); ap.add_argument('--excess', action='store_true', help='add sum_k w_k(lambda_ik-3) = 1/2-4w_i per row')
a = ap.parse_args(); R = a.R
if a.excess: F, x, LAM = build(R, a.case, a.sqs, a.distinct, a.not1, True)
elif a.maxthird: F, x, C4, T3 = build(R, a.case, a.sqs, a.distinct, a.not1, False, a.not1pair, True, True, a.notrade, a.colcard)
else: F, x, C4 = build(R, a.case, a.sqs, a.distinct, a.not1, False, a.not1pair, True, False, a.notrade, a.colcard)
with open(a.out, 'w') as f:
    f.write('(set-logic QF_LRA)\n')
    for v in range(1, F.nv + 1): f.write(f'(declare-const b{v} Bool)\n')
    for i in range(R): f.write(f'(declare-const w{i} Real)\n')
    lit = lambda l: f'b{l}' if l > 0 else f'(not b{-l})'
    for cl in F.clauses:
        f.write('(assert (or ' + ' '.join(lit(l) for l in cl) + (' false' if len(cl) < 2 else '') + '))\n')
    for i in range(R): f.write(f'(assert (and ({">" if a.pos else ">="} w{i} 0) (<= w{i} (/ 1 8))))\n')
    f.write('(assert (= (+ ' + ' '.join(f'w{i}' for i in range(R)) + ') 1))\n')
    if a.avoid0:
        for k in range(4, R): f.write(f'(assert (<= (ite b{x[k][0]} 0 w{k}) w3))\n')
    if a.maxthird:
        for k in range(3, R): f.write(f'(assert (<= (ite b{T3[k]} w{k} 0) w2))\n')
    if a.maxpartner:
        for k in range(2, R): f.write(f'(assert (<= (ite b{C4[0, k]} 0 w{k}) w1))\n')
    if a.maxw:
        for k in range(1, R): f.write(f'(assert (>= w0 w{k}))\n')
    for j in range(14):
        f.write('(assert (= (+ ' + ' '.join(f'(ite b{x[i][j]} w{i} 0)' for i in range(R)) + ') (/ 1 2)))\n')
    if a.excess:
        for i in range(R):
            terms = []
            for k in range(R):
                if k == i: continue
                cnt = LAM[min(i, k), max(i, k)]
                for t in (4, 5, 6, 7):
                    l = cnt[t]
                    if l is None: terms.append(f'w{k}')
                    elif l is not False: terms.append(f'(ite b{l} w{k} 0)')
            f.write(f'(assert (= (+ 0 ' + ' '.join(terms) + f') (- (/ 1 2) (* 4 w{i}))))\n')
    f.write('(check-sat)\n')
print(F.nv, len(F.clauses))
