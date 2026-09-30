#!/usr/bin/env python3
"""Attach exact rational Farkas certificates to the lemmas found by keyprop2.py
(prefix.raw.json -> prefix.json in the format read by check_ks2.py).  Usage: certify.py prefix"""
import sys, json
import keysmt2_lib as K
pre = sys.argv[1]; D = json.load(open(pre + '.raw.json')); R = D['R']
K.AVOID0[0] = D.get('avoid0', False)
base = K.base_rows(R); out = []
for n, lits in enumerate(D['lemma_lits']):
    L = {tuple(l[:-1]): l[-1] for l in lits}
    rows = base + K.cond_rows(R, L)
    y = K.farkas(R, rows)
    assert y is not None, f'lemma {n}: no exact certificate'
    out.append({'lits': lits, 'cert': [[str(rows[k][2]), str(y[k])] for k in range(len(rows)) if y[k]]})
D2 = {k: v for k, v in D.items() if k != 'lemma_lits'}; D2['lemmas'] = out
json.dump(D2, open(pre + '.json', 'w'))
print(f'{pre}: {len(out)} lemmas certified')
