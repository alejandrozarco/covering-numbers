#!/usr/bin/env python3
"""Certified cube-and-conquer CLOSER (2026-09-02).

Built after measuring that three 'hard' cells were never hard: their ledgers recorded solver
failures as timeouts (probe_runner.py UNKNOWN->TIMEOUT; resolve.sh/cnc2/cnc3 UNKNOWN on any
non-verdict, no exit-code check). Rules enforced here:
  * CAP is recorded ONLY on TimeoutExpired; any other non-verdict is ERR and STOPS the run.
  * Every UNSAT leaf keeps its LRAT proof (gzipped); every split keeps its .icnf.
  * Capped cubes are re-split with march_cu and recursed; the denominator is the cube tree
    on disk (top icnf + splits/), never this ledger.
usage: cnc_close.py BASE.cnf TOP.icnf TAG CAP DEPTH PAR
"""
import sys, os, json, subprocess, time, gzip, shutil, threading
from concurrent.futures import ThreadPoolExecutor
CAD = os.path.expanduser(os.environ.get('CAD', '~/sat/cadical/build/cadical')); MARCH = os.path.expanduser(os.environ.get('MARCH', '~/sat/CnC/march_cu/march_cu'))
NOPROOF = os.environ.get('NOPROOF') == '1'; BUDGET = float(os.environ.get('BUDGET', '1e18'))   # sweep: no proofs, CPU budget in s
base, icnf, tag, cap, depth, par = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
OUT = f'close_{tag}'; os.makedirs(f'{OUT}/proofs', exist_ok=True); os.makedirs(f'{OUT}/splits', exist_ok=True)
LED = f'{OUT}/ledger.jsonl'
lines = open(base).read().splitlines(); hdr = next(l for l in lines if l.startswith('p cnf')); NV, NC = hdr.split()[2:4]
BODY = "\n".join(l for l in lines if l and l[0] not in 'pc') + "\n"
done = {}
if os.path.exists(LED):
    for l in open(LED):
        if l.strip(): d = json.loads(l); done[d['id']] = d['result']
led = open(LED, 'a'); lock = threading.Lock()
def record(row):
    with lock: led.write(json.dumps(row) + "\n"); led.flush(); done[row['id']] = row['result']
    print(row, flush=True)
def write_cnf(path, lits):
    with open(path, 'w') as f:
        f.write(f"p cnf {NV} {int(NC)+len(lits)}\n"); f.write(BODY); f.write("".join(f"{l} 0\n" for l in lits))
SPENT = [0.0]
def solve(c):
    cid, lits = c
    if SPENT[0] > BUDGET: record({'id': cid, 'result': 'BUDGET', 'secs': 0, 'nlits': len(lits)}); return 'BUDGET'
    if done.get(cid) == 'UNSAT': return 'UNSAT'
    cnf = f'{OUT}/tmp_{cid}.cnf'; proof = f'{OUT}/proofs/{cid}.lrat'
    write_cnf(cnf, lits); t0 = time.time(); r = None
    try:
        r = subprocess.run([CAD, '-q'] + ([] if NOPROOF else ['--lrat', '--binary=false']) + [cnf] + ([] if NOPROOF else [proof]), capture_output=True, text=True, timeout=cap)
        res = 'SAT' if 's SATISFIABLE' in r.stdout else ('UNSAT' if 's UNSATISFIABLE' in r.stdout else f'ERR_rc{r.returncode}')
    except subprocess.TimeoutExpired:
        res = 'CAP'
    el = round(time.time() - t0, 1); SPENT[0] += el
    if res == 'UNSAT' and os.path.exists(proof):
        with open(proof, 'rb') as fi, gzip.open(proof + '.gz', 'wb') as fo: shutil.copyfileobj(fi, fo)
    if os.path.exists(proof): os.remove(proof)
    if res == 'SAT':
        shutil.copy(cnf, f'{OUT}/WITNESS_{cid}.cnf'); open(f'{OUT}/WITNESS_{cid}.out', 'w').write(r.stdout)
    if res.startswith('ERR') and r is not None: open(f'{OUT}/ERR_{cid}.txt', 'w').write(r.stderr[-2000:])
    if os.path.exists(cnf): os.remove(cnf)
    record({'id': cid, 'result': res, 'secs': el, 'nlits': len(lits)}); return res
def split(c):
    cid, lits = c; cnf = f'{OUT}/splits/{cid}.cnf'; ic = f'{OUT}/splits/{cid}_d{depth}.icnf'
    if not (os.path.exists(ic) and os.path.getsize(ic) > 0):
        write_cnf(cnf, lits); subprocess.run([MARCH, cnf, '-d', str(depth), '-o', ic], capture_output=True, timeout=3600); os.remove(cnf)
    kids = [l.split()[1:-1] for l in open(ic) if l.startswith('a ')]
    if not kids:   # march found it trivially UNSAT or refused: solve the cube itself uncapped-ish at 4x cap
        return [(cid + '.solo', lits)]
    return [(f'{cid}.{j}', lits + k) for j, k in enumerate(kids)]
level = [(str(i), l.split()[1:-1]) for i, l in enumerate(x for x in open(icnf) if x.startswith('a '))]
print(f"instance {base}: {hdr} | top cubes {len(level)} | cap {cap}s | resplit depth {depth} | par {par}", flush=True)
lvl = 0
while level:
    print(f"=== LEVEL {lvl}: {len(level)} cubes ===", flush=True)
    with ThreadPoolExecutor(max_workers=par) as ex: results = list(ex.map(solve, level))
    sats = [c for c, r in zip(level, results) if r == 'SAT']; errs = [c for c, r in zip(level, results) if r.startswith('ERR')]
    caps = [c for c, r in zip(level, results) if r == 'CAP']
    if sats: print("*** WITNESS ***", [c[0] for c in sats], flush=True); break
    if errs: print("*** ERRORS, not timeouts -- stopping, see ERR_*.txt ***", [c[0] for c in errs][:10], flush=True); break
    nxt = []
    for c in caps: nxt += split(c)
    print(f"    level {lvl}: {len(level)-len(caps)} UNSAT, {len(caps)} capped -> {len(nxt)} children", flush=True)
    level = nxt; lvl += 1
    if lvl > 8: print("*** depth limit reached ***", flush=True); break
print("=== CLOSE DONE ===", flush=True)
