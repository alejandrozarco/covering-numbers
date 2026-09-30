#!/usr/bin/env python3
"""Auditor's fresh negative controls for verify_kl.py (run from family/; works on copies in
audit/kl_closure/tmp only).  Cheap setting: verify_kl.py --no-proof --dir=<copy>.
Baseline copy 'stub': every real certificate (all 41: B, A9..A13, 35 A14 cubes) with its lemma list
emptied and its CNF truncated to base + cube units (so klcheck is fast and the manifest/cover logic
is exercised on the REAL option sets and cube lists).  The baseline must PASS; each control changes
one thing and must FAIL with the specific expected line.
 (i)   drop one cube (A14_c10110)
 (ii)  relabel xA9 as A14 cube: (a) file renamed A14_c11111 replacing the real one;
       (b) same, metadata also edited to R=14, A14 options, cube p03..p07=1
 (iii) real A14_c11111 certificate with one Farkas multiplier changed (y -> y + 1/7)
 (iv)  contradictory cube: (a) extra cube with p_{0,3}=1 and p_{0,3}=0 added to the full set;
       (b) such a cube replacing A14_c11111; (c) A14_c11111 replaced by cube p03..p07=1 + x_{0,0}=0
       (contradicts the fixed row 0; CNF trivially UNSAT)"""
import os, sys, json, lzma, glob, shutil, subprocess, ast
from fractions import Fraction as Fr
FAM = os.getcwd(); TMP = os.path.join(FAM, 'audit/kl_closure/tmp')
real = {os.path.basename(p)[:-13]: p[:-13] for p in glob.glob('kl_certs/*.cert.json.xz')}
def load(n):
    D = json.load(lzma.open(real[n] + '.cert.json.xz'))
    cnf = lzma.open(real[n] + '.cnf.xz', 'rt').read().splitlines(True)
    return D, cnf
def stub(n):
    D, cnf = load(n); D = dict(D); k = D['nbase'] + len(D.get('cube') or [])
    body = [l for l in cnf if l.strip() and l[0] not in 'cp'][:k]
    D['lemma_lits'] = []; D['certs'] = []
    return D, body
def write(d, files):
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    for n, (D, body) in files.items():
        nv = max(abs(int(t)) for l in body for t in l.split()[:-1])
        with lzma.open(f'{d}/{n}.cert.json.xz', 'wt') as f: json.dump(D, f)
        with lzma.open(f'{d}/{n}.cnf.xz', 'wt') as f: f.write(f'p cnf {nv} {len(body)}\n' + ''.join(body))
def run(tag, files, expect):
    d = os.path.join(TMP, tag); write(d, files)
    r = subprocess.run(['nice', '-n', '10', 'python3', 'verify_kl.py', '--no-proof', f'--dir={d}'], capture_output=True, text=True)
    out = r.stdout; last = out.strip().splitlines()[-1]
    hit = [l for l in out.splitlines() if l.startswith('FAIL')]
    ok = (last == 'VERIFY_KL: PASS') if expect is None else (last == 'VERIFY_KL: FAIL' and any(expect in l for l in hit))
    print(f'[{"OK " if ok else "BAD"}] {tag}: {last}; exit {r.returncode}; FAIL lines: {[h[:150] for h in hit]}', flush=True)
    shutil.rmtree(d); return ok
base = {n: stub(n) for n in real}
res = [run('baseline_stub', base, None)]
f = dict(base); del f['A14_c10110']
res.append(run('i_drop_cube', f, 'FAIL cell A14'))
f = dict(base); f['A14_c11111'] = stub('xA9')
res.append(run('ii_a_relabel_xA9', f, 'FAIL cell A14'))
D, body = stub('xA9'); D = dict(D, R=14, exact=True, third=True, case='t1', cube=base['A14_c11111'][0]['cube'])
f = dict(base); f['A14_c11111'] = (D, body)
res.append(run('ii_b_relabel_xA9_meta', f, 'FAIL klcheck A14_c11111'))
# (iii) real certificate, one multiplier corrupted
D, cnf = load('A14_c11111'); body = [l for l in cnf if l.strip() and l[0] not in 'cp']
f = dict(base); f['A14_c11111'] = (D, body)
res.append(run('iii_baseline_real_c11111', f, None))
C = D['certs'] if isinstance(D['certs'], list) else ast.literal_eval(D['certs'])
C = [list(map(list, c)) for c in C]; C[0][0][1] = str(Fr(C[0][0][1]) + Fr(1, 7))
D2 = dict(D, certs=C); f['A14_c11111'] = (D2, body)
res.append(run('iii_farkas_multiplier', f, 'FAIL klcheck A14_c11111'))
# (iv) contradictory cubes
def cube_stub(cube, extra_units):
    D, body = stub('A14_c11111'); D = dict(D, cube=cube); nb = D['nbase']
    return D, body[:nb] + extra_units
D11, b11 = stub('A14_c11111'); units = b11[D11['nbase']:]
c03 = units[0].split()[0]; assert D11['cube'][0] == [['p', 0, 3], 1]
bad = cube_stub(D11['cube'] + [[['p', 0, 3], 0]], units + [f'{-int(c03)} 0\n'])
f = dict(base); f['A14_zcontra'] = bad
res.append(run('iv_a_add_contradictory_cube', f, 'repeats a literal'))
f = dict(base); f['A14_c11111'] = bad
res.append(run('iv_b_replace_by_contradictory_cube', f, 'repeats a literal'))
f = dict(base); f['A14_c11111'] = cube_stub(D11['cube'] + [[['x', 0, 0], 0]], units + ['-1 0\n'])
res.append(run('iv_c_cube_contradicting_base', f, 'FAIL cell A14'))
print('CONTROLS:', 'ALL AS EXPECTED' if all(res) else 'UNEXPECTED RESULT')
