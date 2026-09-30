#!/usr/bin/env python3
"""Blow-up of AG(t,2) (points F_2^t, blocks = affine hyperplanes, 2^(t+1)-2 of them):
any t points of AG(t,2) lie in a common affine hyperplane, so replacing each point by a class of
c = 2m/2^t points gives a (2m, m, t) covering with 2^(t+1)-2 blocks of size m, when 2^(t-1) | m.
t=3: AG(3,2) hyperplanes = the 14 blocks of SQS(8).   Usage: agblow.py t m outdir"""
import sys, itertools, os
t, m, outdir = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
assert (2 * m) % (2 ** t) == 0
c = 2 * m // 2 ** t; pts = range(2 ** t)
hyps = set()
for h in range(1, 2 ** t):
    for b in (0, 1):
        hyps.add(frozenset(p for p in pts if bin(p & h).count('1') % 2 == b))
assert len(hyps) == 2 ** (t + 1) - 2
os.makedirs(outdir, exist_ok=True)
fn = f'{outdir}/C{2*m}_{m}_{t}_b{len(hyps)}.txt'
with open(fn, 'w') as f:
    f.write(f'# C({2*m},{m},{t}) <= {len(hyps)}: AG({t},2) blow-up, class size {c}\n')
    for H in sorted(hyps, key=sorted):
        f.write(' '.join(str(p * c + i) for p in sorted(H) for i in range(c)) + '\n')
print(fn)
