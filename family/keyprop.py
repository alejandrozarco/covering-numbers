#!/usr/bin/env python3
"""CDCL(T) for the Key Lemma counterexample search: CaDiCaL 1.9.5 (PySAT, IPASIR-UP external
propagator) + exact-Farkas LP theory lemmas, same model and certificate format as keysmt2.py
(checked by check_ks2.py).  The theory check runs on partial assignments (throttled) and on models.
Output: prefix.cnf (base + lemmas) for an independent CaDiCaL/DRAT re-solve, prefix.json (lemmas).
Usage: keyprop.py R prefix --case t1|t2 [--maxthird] [--not1pair] [--sqs] [--every K]"""
import sys, json, time, argparse
from pysat.solvers import Solver
from pysat.engines import Propagator
from basecnf import build
import keysmt2_lib as K

class LP(Propagator):
    def __init__(self, R, var, every):
        super().__init__()
        self.R = R; self.var = var; self.every = every
        self.key = {v: k for k, v in var.items()}
        self.val = {}; self.trail = []; self.lim = []
        self.pending = []; self.lemmas = []; self.since = 0; self.nchecks = 0
        self.base = K.base_rows(R)
    def on_assignment(self, lit, fixed=False):
        k = self.key[abs(lit)]; self.val[k] = 1 if lit > 0 else 0; self.trail.append(k); self.since += 1
    def on_new_level(self):
        self.lim.append(len(self.trail))
    def on_backtrack(self, to):
        if to < len(self.lim):
            n = self.lim[to]
            for k in self.trail[n:]: del self.val[k]
            del self.trail[n:]; del self.lim[to:]
    def conflict(self, assign):
        if not K.fast_infeasible(self.R, assign): return False
        rows = self.base + K.cond_rows(self.R, assign)
        y = K.farkas(self.R, rows)
        if y is None: return False           # numerically unclear: let the search continue
        L = K.used_lits(self.R, rows, y, assign)
        for key in list(L.keys()):
            trial = dict(L); trial.pop(key)
            if K.fast_infeasible(self.R, trial): L = trial
        rows2 = self.base + K.cond_rows(self.R, L); y2 = K.farkas(self.R, rows2)
        if y2 is None:
            L = K.used_lits(self.R, rows, y, assign); rows2 = self.base + K.cond_rows(self.R, L); y2 = K.farkas(self.R, rows2)
            if y2 is None: return False
        L = K.used_lits(self.R, rows2, y2, L)
        rows3 = self.base + K.cond_rows(self.R, L); idx = {r[2]: k for k, r in enumerate(rows3)}
        cert = sorted((idx[rows2[k][2]], y2[k]) for k in range(len(rows2)) if y2[k])
        clause = [(-self.var[k] if v else self.var[k]) for k, v in sorted(L.items())]
        self.lemmas.append({'lits': [[*k, v] for k, v in sorted(L.items())],
                            'cert': [[str(rows3[k][2]), str(v)] for k, v in cert]})
        self.pending.append(clause); return True
    def propagate(self):
        if self.since >= self.every and not self.pending:
            self.since = 0; self.nchecks += 1
            self.conflict(dict(self.val))
        return []
    def provide_reason(self, lit):
        return []
    def check_model(self, model):
        ms = set(l for l in model if l > 0)
        full = {k: (1 if v in ms else 0) for k, v in self.var.items()}
        return not self.conflict(full)
    def decide(self):
        return 0
    def add_clause(self):
        return self.pending.pop() if self.pending else []

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('R', type=int); ap.add_argument('prefix')
    ap.add_argument('--case', required=True); ap.add_argument('--maxthird', action='store_true')
    ap.add_argument('--not1pair', action='store_true'); ap.add_argument('--sqs', action='store_true')
    ap.add_argument('--every', type=int, default=4)
    a = ap.parse_args(); R = a.R
    out = build(R, a.case, a.sqs, False, False, False, a.not1pair, True, a.maxthird)
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
    for L in P.lemmas:
        F.add([(-var[tuple(l[:-1])] if l[-1] else var[tuple(l[:-1])]) for l in L['lits']])
    F.write(a.prefix + '.cnf', [f'keyprop R={R} case={a.case} maxthird={a.maxthird} not1pair={a.not1pair} base_clauses={nbase} lemmas={len(P.lemmas)} status={status}'])
    json.dump({'R': R, 'case': a.case, 'sqs': a.sqs, 'maxthird': a.maxthird, 'not1pair': a.not1pair, 'nbase': nbase,
               'status': status, 'var': [[*k, v] for k, v in var.items()], 'lemmas': P.lemmas}, open(a.prefix + '.json', 'w'))
main()
