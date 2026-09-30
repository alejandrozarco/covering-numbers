#!/usr/bin/env python3
"""Prototype (KL14_IDEAS.md, idea T3): same search as klprop.py but with a custom decision order:
the solver is asked to decide the pairwise-intersection literals p_ik (|S_i cap S_k| >= 4) before the
x_ij literals, polarity 'p = 0' (lambda = 3) first.  Rationale: 86% of the s=13 lemmas are E1-type
(weight-packing over p-neighbourhoods); deciding p first should let the theory refute whole
intersection patterns before the rows are filled in.  Everything else (base CNF, oracle, lemma
recording, output files) is klprop's; the output is certifiable with klcertify/klcheck unchanged
(lemmas are semantic, independent of the decision order).
Usage: klprop_pfirst.py R prefix --case t1 --third --nbr --exact [--pol 0|1]"""
import sys, os, time, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import klprop
from pysat.solvers import Solver
POL = 0
if '--pol' in sys.argv:
    i = sys.argv.index('--pol'); POL = int(sys.argv[i + 1]); del sys.argv[i:i + 2]
class LPfirst(klprop.LP):
    def __init__(self, R, var, every):
        super().__init__(R, var, every)
        self.pvars = [var[('p', i, k)] for i in range(R) for k in range(i + 1, R)]
        self.pidx = {var[('p', i, k)]: i * R + k for i in range(R) for k in range(i + 1, R)}
    def decide(self):
        for v in self.pvars:
            if self.P[self.pidx[v]] < 0:
                return v if POL else -v
        return 0
def main():
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument('R', type=int); ap.add_argument('prefix')
    ap.add_argument('--case', required=True); ap.add_argument('--third', action='store_true')
    ap.add_argument('--nbr', action='store_true'); ap.add_argument('--exact', action='store_true'); ap.add_argument('--every', type=int, default=8)
    a = ap.parse_args(); R = a.R
    a.sqs = False; a.not1pair = False; a.noE = False; a.useF = False; a.notrade = False; a.wsort = False; a.cube = None
    klprop.lib.set_useE(1); klprop.lib.set_useF(0)
    if a.exact:
        import ctypes
        klprop.lib.set_pos.argtypes = [ctypes.c_double]; klprop.lib.set_pos(1e-5)
    F, var = klprop.variables(R, a); nbase = len(F.clauses)
    S = Solver(name='cadical195', bootstrap_with=F.clauses)
    Pr = LPfirst(R, var, a.every); S.connect_propagator(Pr)
    for v in var.values(): S.observe(v)
    t0 = time.time(); r = S.solve(); dt = time.time() - t0
    status = 'SAT' if r else 'UNSAT'
    print(f'pfirst pol={POL} R={R} case={a.case} {status} {dt:.1f}s lemmas={len(Pr.lemmas)} checks={Pr.nchecks}', flush=True)
    for L in Pr.lemmas: F.add([(-var[l[:-1]] if l[-1] else var[l[:-1]]) for l in L])
    meta = {'R': R, 'case': a.case, 'sqs': False, 'third': a.third, 'not1pair': False, 'useE': True, 'nbr': a.nbr, 'useF': False, 'exact': a.exact, 'wsort': False, 'notrade': False,
            'nbase': nbase, 'cube': None, 'status': status, 'time': dt, 'decide': f'pfirst pol={POL}'}
    F.write(a.prefix + '.cnf', ['klprop ' + json.dumps(meta)])
    json.dump(dict(meta, var=[[*k, v] for k, v in var.items()], lemma_lits=[[list(l) for l in L] for L in Pr.lemmas]), open(a.prefix + '.raw.json', 'w'))
if __name__ == '__main__': main()
