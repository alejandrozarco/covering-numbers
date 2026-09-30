#!/usr/bin/env python3
"""Adversarial controls for the manifest logic of verify_kl.py (run with --no-proof):
(a) the s=9 certificate relabelled as xA14 must not cover cell A14;
(b) a lone contradictory cube certificate for s=14 must not cover A14.
(a) and (b) are the two attacks reported in audit/astra_report.md."""
import os, json, lzma, shutil, subprocess, tempfile
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
def run(files):
    d = tempfile.mkdtemp()
    for name, (cj, cn) in files.items():
        open(f'{d}/{name}.cert.json.xz', 'wb').write(lzma.compress(json.dumps(cj).encode()))
        open(f'{d}/{name}.cnf.xz', 'wb').write(lzma.compress(cn.encode()))
    r = subprocess.run(['python3', 'verify_kl.py', '--no-proof', f'--dir={d}'], capture_output=True, text=True)
    shutil.rmtree(d); return r.stdout
ld = lambda n: (json.loads(lzma.open(f'kl_certs/{n}.cert.json.xz').read()), lzma.open(f'kl_certs/{n}.cnf.xz').read().decode())
c9 = ld('xA9')
out = run({'xA14': c9})
print('(a)', 'PASS' if 'FAIL cell A14' in out else 'FAIL', '- relabelled s=9 certificate does not cover A14')
# (b) contradictory cube: meta R=14 exact case t1, cube x_{0,0}=0 (row 0 fixed to contain 0), no lemmas
import sys; sys.path.insert(0, here)
from basecnf import build
F, x = build(14, 't1', False, True, False, False, False, True, True, False, True, True, False)[:2]
cj = dict(c9[0]); cj.update(R=14, cube=[[['x', 0, 0], 0]], lemma_lits=[], certs=[], nbase=len(F.clauses))
cn = 'p cnf %d %d\n' % (F.nv, len(F.clauses) + 1) + ''.join(' '.join(map(str, c)) + ' 0\n' for c in F.clauses) + f'{-x[0][0]} 0\n'
out = run({'fake14': (cj, cn)})
print('(b)', 'PASS' if 'FAIL cell A14' in out and 'PASS klcheck fake14' in out else 'FAIL', '- contradictory lone cube passes klcheck but does not cover A14')
print(out[-300:] if '--verbose' in sys.argv else '')

# (c)/(d) cover-check controls on the real A14 cube certificates (only if the full set is present)
import glob
a14 = sorted(os.path.basename(p)[:-len('.cert.json.xz')] for p in glob.glob('kl_certs/A14_*.cert.json.xz'))
if len(a14) >= 35:
    full = {n: ld(n) for n in a14}
    out = run(full)
    print('(c0)', 'PASS' if 'PASS cell A14 covered' in out else 'FAIL', '- the complete A14 cube set covers A14')
    part = {n: v for n, v in full.items() if n != 'A14_c00000_01'}
    out = run(part)
    print('(c)', 'PASS' if 'FAIL cell A14' in out else 'FAIL', '- A14 without sub-cube c00000_01 is rejected')
    dup = dict(full); dup['A14_dup'] = full['A14_c00000_10']
    out = run(dup)
    print('(d)', 'PASS' if 'PASS cell A14 covered' in out else 'FAIL', '- an extra duplicate cube (overlap) is harmless: cell still covered')
