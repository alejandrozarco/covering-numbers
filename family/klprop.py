#!/usr/bin/env python3
"""Certified-pipeline search (v2) for Key Lemma counterexamples: CaDiCaL 1.9.5 (PySAT IPASIR-UP) +
floating-point oracle liblpcore3 (finds and minimises theory conflicts).  Output prefix.raw.json
(lemma literal sets) and prefix.cnf (base + lemmas); klcertify.py adds exact certificates.
Usage: klprop.py R prefix --case t1|t2|A<shape> [--third] [--not1pair] [--avoid0] [--noE] [--sqs]"""
import sys, json, time, argparse, ctypes, os
import numpy as np
from pysat.solvers import Solver
from pysat.engines import Propagator
from basecnf import build
_LIBN = 'liblpcore4.dylib' if any(a.startswith('--minmode') for a in sys.argv) else 'liblpcore3.dylib'
lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), _LIBN))
P8 = ctypes.POINTER(ctypes.c_int8)
USEF = '--useF' in sys.argv
class LP(Propagator):
    def __init__(self, R, var, every):
        super().__init__()
        self.R = R; self.var = var; self.every = every
        self.X = np.full(R * 14, -1, dtype=np.int8); self.P = np.full(R * R, -1, dtype=np.int8); self.T = np.full(R, -1, dtype=np.int8); self.Q = np.full(R * R * R, -1, dtype=np.int8)
        self.where = {}
        for key, v in var.items():
            if key[0] == 'x': self.where[v] = [(self.X, key[1] * 14 + key[2])]
            elif key[0] == 'p': self.where[v] = [(self.P, key[1] * R + key[2]), (self.P, key[2] * R + key[1])]
            elif key[0] == 'q':
                import itertools as _it
                self.where[v] = [(self.Q, a * R * R + b * R + c) for a, b, c in _it.permutations(key[1:4])]
            else: self.where[v] = [(self.T, key[1])]
        self.trail = []; self.lim = []; self.pending = []; self.lemmas = []; self.since = 0; self.nchecks = 0
    def on_assignment(self, lit, fixed=False):
        val = 1 if lit > 0 else 0
        for arr, i in self.where[abs(lit)]: arr[i] = val
        self.trail.append(abs(lit)); self.since += 1
    def on_new_level(self): self.lim.append(len(self.trail))
    def on_backtrack(self, to):
        if to < len(self.lim):
            n = self.lim[to]
            for v in self.trail[n:]:
                for arr, i in self.where[v]: arr[i] = -1
            del self.trail[n:]; del self.lim[to:]
    def conflict(self, X, P, T, Q):
        X = X.copy(); P = P.copy(); T = T.copy(); Q = Q.copy(); R = self.R
        args = [R, X.ctypes.data_as(P8), P.ctypes.data_as(P8), T.ctypes.data_as(P8), Q.ctypes.data_as(P8)]
        if not lib.minimize(*args): return False
        lits = [('x', i, j, int(X[i * 14 + j])) for i in range(R) for j in range(14) if X[i * 14 + j] >= 0]
        lits += [('p', i, k, int(P[i * R + k])) for i in range(R) for k in range(i + 1, R) if P[i * R + k] >= 0]
        lits += [('t', k, int(T[k])) for k in range(R) if T[k] >= 0]
        lits += [('q', i, k, l, int(Q[i * R * R + k * R + l])) for i in range(R) for k in range(i + 1, R) for l in range(k + 1, R) if Q[i * R * R + k * R + l] >= 0]
        self.lemmas.append(lits)
        self.pending.append([(-self.var[l[:-1]] if l[-1] else self.var[l[:-1]]) for l in lits]); return True
    def propagate(self):
        if self.since >= self.every and not self.pending:
            self.since = 0; self.nchecks += 1; self.conflict(self.X, self.P, self.T, self.Q)
        return []
    def provide_reason(self, lit): return []
    def check_model(self, model):
        ms = set(l for l in model if l > 0)
        R = self.R
        X = np.full(R * 14, -1, dtype=np.int8); P = np.full(R * R, -1, dtype=np.int8); T = np.full(R, -1, dtype=np.int8); Q = np.full(R * R * R, -1, dtype=np.int8)
        for v, locs in self.where.items():
            for arr, i in locs:
                tgt = X if arr is self.X else (P if arr is self.P else (T if arr is self.T else Q)); tgt[i] = 1 if v in ms else 0
        return not self.conflict(X, P, T, Q)
    def decide(self): return 0
    def add_clause(self): return self.pending.pop() if self.pending else []
def variables(R, a):
    a.nbr = getattr(a, 'nbr', False); a.useF = getattr(a, 'useF', False)
    a.exact = getattr(a, 'exact', False)
    a.wsort = getattr(a, 'wsort', False)
    a.notrade = getattr(a, 'notrade', False)
    out = build(R, a.case, a.sqs, a.exact, False, False, a.not1pair, True, a.third, a.notrade, True, a.nbr, a.useF, not a.wsort)
    F, x, c4 = out[:3]; T3 = out[3] if a.third else {}
    Qv = out[4] if a.useF else {}
    var = {('x', i, j): x[i][j] for i in range(R) for j in range(14)}
    var.update({('p', i, k): v for (i, k), v in c4.items()}); var.update({('t', k): v for k, v in T3.items()})
    var.update({('q', i, k, l): v for (i, k, l), v in Qv.items()})
    return F, var
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('R', type=int); ap.add_argument('prefix')
    ap.add_argument('--case', required=True); ap.add_argument('--third', action='store_true')
    ap.add_argument('--not1pair', action='store_true'); ap.add_argument('--sqs', action='store_true')
    ap.add_argument('--noE', action='store_true'); ap.add_argument('--nbr', action='store_true'); ap.add_argument('--useF', action='store_true'); ap.add_argument('--notrade', action='store_true'); ap.add_argument('--minmode', type=int, default=0, help='1: dual-support lemmas only, 2: + column deletion (liblpcore4)'); ap.add_argument('--seed', action='append', default=[], help='raw.json of another run: its lemmas are added (and re-recorded) as clauses'); ap.add_argument('--cube', default=None, help='unit literals key,value[:key,value...] e.g. p,0,3,0:x,3,13,1'); ap.add_argument('--wsort', action='store_true', help='rows after the fixed ones sorted by weight (instead of lex)'); ap.add_argument('--exact', action='store_true', help='rows distinct, all weights >= 1e-5 (vertex supports of size exactly R)'); ap.add_argument('--every', type=int, default=8)
    a = ap.parse_args(); R = a.R
    lib.set_useE(0 if a.noE else 1); lib.set_useF(1 if a.useF else 0)
    if a.minmode: lib.set_minmode(a.minmode)
    if a.wsort: lib.set_wsort(3 if a.third else 2)
    if a.exact:
        lib.set_pos.argtypes = [ctypes.c_double]; lib.set_pos(1e-5)
    F, var = variables(R, a); nbase = len(F.clauses)
    cube = None
    if a.cube:
        cube = []
        for item in a.cube.split(':'):
            parts = item.split(','); key = (parts[0],) + tuple(int(v) for v in parts[1:-1]); val = int(parts[-1])
            cube.append([list(key), val]); F.add([var[key] if val else -var[key]])
    S = Solver(name='cadical195', bootstrap_with=F.clauses)
    Pr = LP(R, var, a.every)
    nseed = 0
    for sf in a.seed:
        SD = json.load(open(sf)); assert SD['R'] == R
        for L in SD['lemma_lits']:
            L = [tuple(l) for l in L]
            if all(l[:-1] in var for l in L):
                Pr.lemmas.append(L); S.add_clause([(-var[l[:-1]] if l[-1] else var[l[:-1]]) for l in L]); nseed += 1
    S.connect_propagator(Pr)
    for v in var.values(): S.observe(v)
    t0 = time.time(); r = S.solve(); dt = time.time() - t0
    status = 'SAT' if r else 'UNSAT'
    if r:
        m = set(l for l in S.get_model() if l > 0)
        print('COUNTEREXAMPLE', [''.join('1' if var['x', i, j] in m else '0' for j in range(14)) for i in range(R)])
    print(f'R={R} case={a.case} {status} {dt:.1f}s lemmas={len(Pr.lemmas)} (seeded {nseed}) checks={Pr.nchecks}', flush=True)
    for L in Pr.lemmas: F.add([(-var[l[:-1]] if l[-1] else var[l[:-1]]) for l in L])
    meta = {'R': R, 'case': a.case, 'sqs': a.sqs, 'third': a.third, 'not1pair': a.not1pair, 'useE': not a.noE, 'nbr': a.nbr, 'useF': a.useF, 'exact': a.exact, 'wsort': a.wsort, 'notrade': a.notrade,
            'nbase': nbase, 'cube': cube, 'status': status, 'time': dt}
    F.write(a.prefix + '.cnf', ['klprop ' + json.dumps(meta)])
    json.dump(dict(meta, var=[[*k, v] for k, v in var.items()], lemma_lits=[[list(l) for l in L] for L in Pr.lemmas]),
              open(a.prefix + '.raw.json', 'w'))
if __name__ == '__main__': main()
