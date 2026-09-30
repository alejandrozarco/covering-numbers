#!/usr/bin/env python3
"""Attach exact rational Farkas certificates to klprop.py lemmas: prefix.raw.json -> prefix.cert.json.
Usage: klcertify.py prefix"""
import sys, json
import kl_lib as K
pre = sys.argv[1]; D = json.load(open(pre + '.raw.json')); R = D['R']
base = K.base_rows(R, D.get('exact', False), (3 if D['third'] else 2) if D.get('wsort') else 0); out = []
for n, lits in enumerate(D['lemma_lits']):
    L = {tuple(l[:-1]): l[-1] for l in lits}
    rows = base + K.cond_rows(R, L, D['useE'], D['third'], D.get('useF', False))
    y = K.farkas(R, rows)
    assert y is not None, f'lemma {n}: no exact certificate'
    out.append([[str(rows[k][2]), str(y[k])] for k in range(len(rows)) if y[k]])
json.dump({k: v for k, v in D.items() if k != 'var'} | {'certs': out}, open(pre + '.cert.json', 'w'))
print(f'{pre}: {len(out)} lemmas certified')
