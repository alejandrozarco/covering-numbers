#!/usr/bin/env python3
"""CDCL(T) search for Key Lemma counterexamples: CaDiCaL 1.9.5 via PySAT IPASIR-UP + a fast C
floating-point LP oracle (liblpcore) that detects and minimises theory conflicts on partial
assignments.  Lemmas are recorded as literal sets only; certify.py afterwards attaches exact rational
Farkas certificates (checked by check_ks2.py) and the final CNF (base + lemmas) is re-solved by
standalone CaDiCaL with a DRAT proof (drat-trim + cake_lpr).
Usage: keyprop2.py R prefix --case t1|t2 [--maxthird] [--not1pair] [--sqs] [--every K]"""
import sys, json, time, argparse, ctypes, os
import numpy as np
from pysat.solvers import Solver
from pysat.engines import Propagator
from basecnf import build
lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'liblpcore.dylib'))
P8 = ctypes.POINTER(ctypes.c_int8)

class LP(Propagator):
    def __init__(self, R, var, every):
        super().__init__()
        self.R = R; self.var = var; self.every = every
        self.X = np.full(R * 14, -1, dtype=np.int8); self.C4 = np.full(R, -1, dtype=np.int8); self.T3 = np.full(R, -1, dtype=np.int8)
        self.where = {}
        for key, v in var.items():
            if key[0] == 'x': self.where[v] = (self.X, key[1] * 14 + key[2])
            elif key[0] == 'c4': self.where[v] = (self.C4, key[1])
            else: self.where[v] = (self.T3, key[1])
        self.trail = []; self.lim = []; self.pending = []; self.lemmas = []; self.since = 0; self.nchecks = 0
    def on_assignment(self, lit, fixed=False):
        arr, i = self.where[abs(lit)]; arr[i] = 1 if lit > 0 else 0; self.trail.append(abs(lit)); self.since += 1
    def on_new_level(self):
        self.lim.append(len(self.trail))
    def on_backtrack(self, to):
        if to < len(self.lim):
            n = self.lim[to]
            for v in self.trail[n:]:
                arr, i = self.where[v]; arr[i] = -1
            del self.trail[n:]; del self.lim[to:]
    def conflict(self, X, C4, T3):
        X = X.copy(); C4 = C4.copy(); T3 = T3.copy()
        if not lib.minimize(self.R, X.ctypes.data_as(P8), C4.ctypes.data_as(P8), T3.ctypes.data_as(P8)):
            return False
        lits = []
        for i in range(self.R):
            for j in range(14):
                if X[i * 14 + j] >= 0: lits.append(('x', i, j, int(X[i * 14 + j])))
        for k in range(self.R):
            if C4[k] >= 0: lits.append(('c4', k, int(C4[k])))
            if T3[k] >= 0: lits.append(('T3', k, int(T3[k])))
        clause = [(-self.var[l[:-1]] if l[-1] else self.var[l[:-1]]) for l in lits]
        self.lemmas.append(lits); self.pending.append(clause); return True
    def propagate(self):
        if self.since >= self.every and not self.pending:
            self.since = 0; self.nchecks += 1
            self.conflict(self.X, self.C4, self.T3)
        return []
    def provide_reason(self, lit): return []
    def check_model(self, model):
        X = np.full(self.R * 14, -1, dtype=np.int8); C4 = np.full(self.R, -1, dtype=np.int8); T3 = np.full(self.R, -1, dtype=np.int8)
        ms = set(l for l in model if l > 0)
        for v, (arr, i) in self.where.items():
            tgt = X if arr is self.X else (C4 if arr is self.C4 else T3)
            tgt[i] = 1 if v in ms else 0
        return not self.conflict(X, C4, T3)
    def decide(self): return 0
    def add_clause(self): return self.pending.pop() if self.pending else []

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('R', type=int); ap.add_argument('prefix')
    ap.add_argument('--case', required=True); ap.add_argument('--maxthird', action='store_true')
    ap.add_argument('--not1pair', action='store_true'); ap.add_argument('--sqs', action='store_true')
    ap.add_argument('--every', type=int, default=4); ap.add_argument('--colcard', action='store_true'); ap.add_argument('--distinct', action='store_true'); ap.add_argument('--avoid0', action='store_true')
    a = ap.parse_args(); R = a.R
    lib.set_avoid0(1 if a.avoid0 else 0)
    out = build(R, a.case, a.sqs, a.distinct, False, False, a.not1pair, True, a.maxthird, False, a.colcard)
    F, x, c4 = out[:3]; T3 = out[3] if a.maxthird else {}
    var = {('x', i, j): x[i][j] for i in range(R) for j in range(14)}
    var.update({('c4', k): c4[0, k] for k in range(2, R)}); var.update({('T3', k): v for k, v in T3.items()})
    nbase = len(F.clauses)
    S = Solver(name='cadical195', bootstrap_with=F.clauses)
    P = LP(R, var, a.every); S.connect_propagator(P)
    for v in var.values(): S.observe(v)
    t0 = time.time(); r = S.solve(); dt = time.time() - t0
    status = 'SAT' if r else 'UNSAT'
    if r:
        m = set(l for l in S.get_model() if l > 0)
        print('COUNTEREXAMPLE', [''.join('1' if x[i][j] in m else '0' for j in range(14)) for i in range(R)])
    print(f'R={R} case={a.case} {status} {dt:.1f}s lemmas={len(P.lemmas)} checks={P.nchecks}', flush=True)
    for L in P.lemmas: F.add([(-var[l[:-1]] if l[-1] else var[l[:-1]]) for l in L])
    F.write(a.prefix + '.cnf', [f'keyprop2 R={R} case={a.case} maxthird={a.maxthird} not1pair={a.not1pair} base_clauses={nbase} lemmas={len(P.lemmas)} status={status}'])
    json.dump({'R': R, 'case': a.case, 'sqs': a.sqs, 'maxthird': a.maxthird, 'not1pair': a.not1pair, 'colcard': a.colcard, 'distinct': a.distinct, 'avoid0': a.avoid0, 'nbase': nbase,
               'status': status, 'time': dt, 'var': [[*k, v] for k, v in var.items()],
               'lemma_lits': [[list(l) for l in L] for L in P.lemmas]}, open(a.prefix + '.raw.json', 'w'))
main()
