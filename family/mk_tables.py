#!/usr/bin/env python3
"""Regenerate the result tables in FAMILY.md from runs/kl_v2.jsonl, runs/direct_proofs.jsonl and the
.raw.json metadata of the KL instances."""
import json, re, os, hashlib
recs = {}
for l in open('runs/kl_v2.jsonl'):
    r = json.loads(l); recs[os.path.basename(r['cnf'])[:-4]] = r
rows = ['| instance | model | search (klprop) | lemmas | CaDiCaL re-solve | DRAT bytes | drat-trim | cake_lpr | CNF SHA-256 (prefix) |', '|---|---|---|---|---|---|---|---|---|']
for p in ['v2B14', 'xA9', 'xA10', 'xA11', 'xA12', 'xA13', 'xA14']:
    if p not in recs: rows.append(f'| {p} | | pending | | | | | | |'); continue
    r = recs[p]; meta = json.load(open(f'ks/{p}.raw.json')) if os.path.exists(f'ks/{p}.raw.json') else {}
    model = ('case B, dup R=14' if p.startswith('v2B') else f'case A, exact s={meta.get("R")}')
    rows.append(f'| {p} | {model} | {meta.get("time", 0):.0f} s | {len(meta.get("lemma_lits", []))} | {r["solve_s"]} s | {r["drat_bytes"]} | {r["drat_trim"]} | {r["cake_lpr"]} | {r["cnf_sha256"][:16]} |')
kl = '\n'.join(rows)
drows = ['| m | CNF | solve | DRAT bytes | drat-trim | cake_lpr | CNF SHA-256 (prefix) |', '|---|---|---|---|---|---|---|']
for l in open('runs/direct_proofs.jsonl'):
    r = json.loads(l); m = re.search(r'm(\d+)', r['cnf']).group(1)
    drows.append(f'| {m} | {r["cnf"]} | {r["solve_s"]} s | {r["drat_bytes"]} | {r["drat_trim"]} | {r["cake_lpr"]} | {r["cnf_sha256"][:16]} |')
s = open('FAMILY.md').read()
s = re.sub(r'<!--KL-->.*?<!--/KL-->', '<!--KL-->\n' + kl + '\n<!--/KL-->', s, flags=re.S)
s = re.sub(r'<!--DIRECT-->.*?<!--/DIRECT-->', '<!--DIRECT-->\n' + '\n'.join(drows) + '\n<!--/DIRECT-->', s, flags=re.S)
open('FAMILY.md', 'w').write(s); print('tables updated')
