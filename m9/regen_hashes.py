#!/usr/bin/env python3
"""Regenerate every case CNF from source and compare with the cnf_sha256 of its record; the CNFs are not kept.
usage: regen_hashes.py OUT.jsonl TMPDIR   (resumes from OUT; one process, run at background priority)"""
import glob, hashlib, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); out, tmp = sys.argv[1], sys.argv[2]; os.makedirs(tmp, exist_ok=True)
rec = {}
for f in glob.glob(f"{HERE}/runs/*.jsonl"):
    for l in open(f):
        try: r = json.loads(l)
        except ValueError: continue
        if r.get("status") == "UNSATISFIABLE" and r.get("cnf_sha256"): rec.setdefault(r["case"], r)   # CnC records have no gen: same flags
cases = json.load(open(f"{HERE}/cases.json"))
done = {json.loads(l)["case"] for l in open(out)} if os.path.exists(out) else set()
with open(out, "a") as fo:
    for ci, (cls, q, nond7) in enumerate(cases):
        if ci in done: continue
        r = rec[ci]; cnf = f"{tmp}/c{ci}.cnf"
        cmd = ["python3", f"{HERE}/gen_ext9.py", f"{HERE}/links_17_8.json", str(cls), cnf, "--q", str(q)] + r.get("gen", "--n7 --root").split()
        if nond7: cmd += ["--nond7", ",".join(map(str, nond7))]
        subprocess.run(cmd, check=True, capture_output=True, cwd=HERE)
        h = hashlib.sha256(open(cnf, "rb").read()).hexdigest(); os.remove(cnf)
        fo.write(json.dumps({"case": ci, "ok": h == r["cnf_sha256"], "sha256": h}) + "\n"); fo.flush()
print("END")
