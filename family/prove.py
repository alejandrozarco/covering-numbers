#!/usr/bin/env python3
"""Solve a CNF with CaDiCaL; if UNSAT, check the DRAT proof with drat-trim (emitting LRAT) and the
LRAT with cake_lpr.  Appends a JSON record to the given results file.  Usage: prove.py cnf results.jsonl [timeout]"""
import sys, os, subprocess, time, json, hashlib
SAT = os.path.expanduser(os.environ.get('SAT_TOOLS', '~/claude_projects/sat'))  # dir with cadical/, drat-trim/, cake_lpr/
CAD, DT, CAKE = f'{SAT}/cadical/build/cadical', f'{SAT}/drat-trim/drat-trim', f'{SAT}/cake_lpr/cake_lpr'
cnf, out = sys.argv[1], sys.argv[2]; to = int(sys.argv[3]) if len(sys.argv) > 3 else 36000
sha = lambda f: hashlib.sha256(open(f, 'rb').read()).hexdigest()
drat = cnf + '.drat'; lrat = cnf + '.lrat'
rec = {'cnf': cnf, 'cnf_sha256': sha(cnf)}
t0 = time.time()
r = subprocess.run(f'nice -n 10 {CAD} -q --binary=false -t {to} {cnf} {drat}', shell=True, capture_output=True, text=True)
rec['solve_s'] = round(time.time() - t0, 2)
st = [l for l in r.stdout.splitlines() if l.startswith('s ')]
rec['status'] = st[0][2:] if st else 'UNKNOWN'
if rec['status'] == 'SATISFIABLE':
    rec['model'] = ' '.join(l[2:] for l in r.stdout.splitlines() if l.startswith('v '))
    os.remove(drat)
elif rec['status'] == 'UNSATISFIABLE':
    rec['drat_bytes'] = os.path.getsize(drat); rec['drat_sha256'] = sha(drat)
    t1 = time.time()
    d = subprocess.run(f'nice -n 10 {DT} {cnf} {drat} -L {lrat} -t 50000', shell=True, capture_output=True, text=True)
    rec['drat_trim'] = 'VERIFIED' if 's VERIFIED' in d.stdout else 'FAILED ' + d.stdout[-200:]
    rec['drat_trim_s'] = round(time.time() - t1, 2)
    t1 = time.time()
    c = subprocess.run(f'nice -n 10 {CAKE} {cnf} {lrat}', shell=True, capture_output=True, text=True)
    rec['cake_lpr'] = (c.stdout.strip().splitlines() or ['FAILED'])[-1]
    rec['cake_lpr_s'] = round(time.time() - t1, 2)
    rec['lrat_bytes'] = os.path.getsize(lrat)
    subprocess.run(f'xz -T1 -f {drat}; rm -f {lrat}', shell=True)
else:
    if os.path.exists(drat): os.remove(drat)
open(out, 'a').write(json.dumps({k: v for k, v in rec.items() if k != 'model'}) + '\n')
if 'model' in rec: open(cnf + '.model', 'w').write(rec['model'] + '\n')
print(json.dumps({k: v for k, v in rec.items() if k != 'model'}))
