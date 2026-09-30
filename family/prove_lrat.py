#!/usr/bin/env python3
"""Solve a CNF with CaDiCaL writing an LRAT proof directly (--lrat), check it with cake_lpr
(verified checker).  For proofs too large for drat-trim in the resource limits.
Usage: prove_lrat.py cnf results.jsonl"""
import sys, os, subprocess, time, json, hashlib
SAT = os.path.expanduser(os.environ.get('SAT_TOOLS', '~/claude_projects/sat'))  # dir with cadical/, drat-trim/, cake_lpr/
cnf, out = sys.argv[1], sys.argv[2]; lrat = cnf + '.lrat'
def sha(f):
    h = hashlib.sha256()
    with open(f, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
rec = {'cnf': cnf, 'cnf_sha256': sha(cnf), 'mode': 'cadical-lrat+cake_lpr'}
t0 = time.time()
r = subprocess.run(f'nice -n 10 {SAT}/cadical/build/cadical -q --lrat=true --binary=false {cnf} {lrat}', shell=True, capture_output=True, text=True)
rec['solve_s'] = round(time.time() - t0, 2)
st = [l for l in r.stdout.splitlines() if l.startswith('s ')]; rec['status'] = st[0][2:] if st else 'UNKNOWN'
if rec['status'] == 'UNSATISFIABLE':
    rec['lrat_bytes'] = os.path.getsize(lrat); rec['lrat_sha256'] = sha(lrat)
    t1 = time.time()
    c = subprocess.run(f'nice -n 10 {SAT}/cake_lpr/cake_lpr {cnf} {lrat}', shell=True, capture_output=True, text=True)
    rec['cake_lpr'] = (c.stdout.strip().splitlines() or ['FAILED'])[-1]; rec['cake_lpr_s'] = round(time.time() - t1, 2)
    subprocess.run(f'xz -T1 -f {lrat}', shell=True)
open(out, 'a').write(json.dumps(rec) + '\n'); print(json.dumps(rec))
