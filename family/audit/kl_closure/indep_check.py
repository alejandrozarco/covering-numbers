#!/usr/bin/env python3
"""Auditor's independent check (does not import verify_kl.py / klcheck.py).
Usage (from family/): python3 audit/kl_closure/indep_check.py [certdir]
 (a) every certificate's options -> exactly one manifest cell (B, A9..A14), each cell present;
 (b) A14 cube coverage: union K of cube keys; brute force over 2^|K| assignments, each must satisfy
     >= 1 cube; also reports whether the cubes are pairwise disjoint (a partition) and consistent;
 (c) each A14 CNF = [fresh basecnf.build(14,'t1',..., exact A14 options, NO cube)] clause-for-clause
     (same order, sha256 of the base block compared) + |cube| unit clauses equal to the cube literals
     + exactly one clause per recorded lemma literal set, equal to its negation (no other clauses).
     Farkas multipliers are not re-checked here (klcheck does that in the full run)."""
import sys, os, json, lzma, glob, hashlib, itertools
sys.path.insert(0, os.getcwd())
from basecnf import build
D_ = sys.argv[1] if len(sys.argv) > 1 else 'kl_certs'
KEYS = ('case', 'R', 'exact', 'third', 'not1pair', 'sqs', 'useE', 'nbr', 'useF', 'wsort', 'notrade')
C = dict(sqs=False, useE=True, nbr=True, useF=False, wsort=False, notrade=False)
CELLS = {'B': dict(C, case='t2', R=14, exact=False, third=False, not1pair=True)}
for s in range(9, 15): CELLS[f'A{s}'] = dict(C, case='t1', R=s, exact=True, third=True, not1pair=False)
bad = []
def chk(c, m):
    print(('ok   ' if c else 'BAD  ') + m, flush=True)
    if not c: bad.append(m)
certs = {}
for f in sorted(glob.glob(f'{D_}/*.cert.json.xz')):
    certs[os.path.basename(f)[:-13]] = json.load(lzma.open(f))
cellof = {c: [] for c in CELLS}
for n, D in certs.items():
    o = {k: D.get(k, False) for k in KEYS}
    m = [c for c, sp in CELLS.items() if all(o[k] == v for k, v in sp.items())]
    chk(len(m) == 1, f'{n}: cell {m}, cube={bool(D.get("cube"))}')
    if len(m) == 1: cellof[m[0]].append(n)
for c, l in cellof.items():
    mono = [n for n in l if not certs[n].get('cube')]
    chk(bool(l) and (mono or c == 'A14'), f'cell {c}: {len(l)} certs, monolithic={mono}')
# (b) coverage of A14
A = cellof['A14']; cubes = []
for n in A:
    cu = {}
    for key, val in certs[n]['cube']:
        k = tuple(key); chk(k not in cu, f'{n}: literal {k} not repeated/contradictory') if k in cu else None; cu[k] = val
    cubes.append(cu)
K = sorted({k for cu in cubes for k in cu})
unc = [a for a in itertools.product((0, 1), repeat=len(K))
       if not any(all(a[K.index(k)] == v for k, v in cu.items()) for cu in cubes)]
chk(not unc, f'A14: {len(A)} cubes over K={K}: all 2^{len(K)} assignments covered (uncovered={len(unc)})')
tot = sum(2 ** (len(K) - len(cu)) for cu in cubes)
print(f'info A14 cube volume sum = {tot} vs 2^|K| = {2**len(K)} (equal and covered => partition)')
# (c) base CNF comparison
out = build(14, 't1', False, True, False, False, False, True, True, False, True, True, False, True)
F, x, c4 = out[:3]; T3 = out[3]
var = {('x', i, j): x[i][j] for i in range(14) for j in range(14)}
var.update({('p', i, k): v for (i, k), v in c4.items()}); var.update({('t', k): v for k, v in T3.items()})
base = [list(c) for c in F.clauses]
hb = hashlib.sha256(repr(base).encode()).hexdigest()
print(f'info fresh A14 base: {len(base)} clauses, sha256(repr) {hb[:16]}')
for n in A:
    D = certs[n]
    cnf = [list(map(int, l.split()[:-1])) for l in lzma.open(f'{D_}/{n}.cnf.xz', 'rt') if l.strip() and l[0] not in 'cp']
    nb = D['nbase']
    h = hashlib.sha256(repr(cnf[:nb]).encode()).hexdigest()
    cube = D['cube']; units = [[var[tuple(k)] if v else -var[tuple(k)]] for k, v in cube]
    LL = D['lemma_lits'] if isinstance(D['lemma_lits'], list) else __import__('ast').literal_eval(D['lemma_lits'])
    lem = [sorted(-var[tuple(l[:-1])] if l[-1] else var[tuple(l[:-1])] for l in L) for L in LL]
    rest = cnf[nb + len(cube):]
    chk(nb == len(base) and h == hb and cnf[nb:nb + len(cube)] == units
        and len(rest) == len(lem) and [sorted(c) for c in rest] == lem,
        f'{n}: base block == fresh A14 base ({h[:16]}), {len(cube)} cube units, {len(lem)} lemma clauses, nothing else')
print('INDEP_CHECK:', 'PASS' if not bad else f'FAIL ({len(bad)})')
