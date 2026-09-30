#!/usr/bin/env python3
"""Negative controls for klcheck.py on the smallest certified instance (xA9): each tampering must FAIL."""
import json, subprocess, tempfile, os, shutil, lzma
d = tempfile.mkdtemp(); src = 'kl_certs/xA9'
cert = json.loads(lzma.open(src + '.cert.json.xz').read()); cnf = lzma.open(src + '.cnf.xz').read().decode()
def run(C, N, name):
    p = os.path.join(d, 'x'); json.dump(C, open(p + '.cert.json', 'w')); open(p + '.cnf', 'w').write(N)
    r = subprocess.run(['python3', 'klcheck.py', p], capture_output=True, text=True)
    ok = r.returncode != 0
    print(('PASS' if ok else 'FAIL'), 'negative control:', name); return ok
p = os.path.join(d, 'x'); json.dump(cert, open(p + '.cert.json', 'w')); open(p + '.cnf', 'w').write(cnf)
res = [subprocess.run(['python3', 'klcheck.py', p], capture_output=True).returncode == 0]
print(('PASS' if res[0] else 'FAIL'), 'positive control: untampered certificate accepted')
C = json.loads(json.dumps(cert)); C['certs'][0][0][1] = C['certs'][0][0][1] + '1'; res.append(run(C, cnf, 'multiplier changed'))
C = json.loads(json.dumps(cert)); C['lemma_lits'][0] = C['lemma_lits'][0][1:]; res.append(run(C, cnf, 'literal dropped from a lemma'))
C = json.loads(json.dumps(cert)); C['certs'][0] = C['certs'][0][1:]; res.append(run(C, cnf, 'certificate row dropped'))
lines = cnf.split('\n'); i = next(k for k, l in enumerate(lines) if l and l[0] not in 'cp'); lines[i] = lines[i].split()[0] + ' 0'
res.append(run(cert, '\n'.join(lines), 'base clause altered'))
C = json.loads(json.dumps(cert)); C['third'] = False; res.append(run(C, cnf, 'metadata flag flipped'))
shutil.rmtree(d)
print('NEGATIVE CONTROLS:', 'PASS' if all(res) else 'FAIL')
