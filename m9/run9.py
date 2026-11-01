#!/usr/bin/env python3
"""Driver: solve extension cases (class, q) from cases.json.
usage: run9.py out.jsonl idx1,idx2,...|shard:k/N [--proof] [--timeout S] [--solver cadical]
With --proof: DRAT proof, drat-trim (-> LRAT), cake_lpr; proofs deleted after verification
(hashes recorded).  Resumable: cases already in out.jsonl are skipped."""
import sys, os, json, subprocess, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
SAT = os.environ.get("SAT_TOOLS", os.path.expanduser("~/sat"))
CADICAL = os.environ.get("CADICAL", f"{SAT}/cadical/build/cadical")
DRATTRIM = os.environ.get("DRATTRIM", f"{SAT}/drat-trim/drat-trim")
CAKE = os.environ.get("CAKE", f"{SAT}/cake_lpr/cake_lpr")
# idle capacity only (user, 2026-10-03): background QoS on macOS; on Linux set M9_NICE="nice -n 19 chrt -i 0"
NICE = os.environ.get("M9_NICE", "nice -n 19 taskpolicy -b")
LRATCHECK = os.environ.get("LRATCHECK", f"{SAT}/drat-trim/lrat-check")
# If HERE/lrat.mode exists: CaDiCaL writes LRAT directly (no drat-trim, whose memory use was 13-15 GB on 5-7 GB
# proofs); the LRAT is checked by cake_lpr and by lrat-check (2026-10-05).
LRAT_MODE = os.path.exists(os.path.join(HERE, "lrat.mode"))


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def sha(fn):
    h = hashlib.sha256()
    with open(fn, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def main():
    out = sys.argv[1]; sel = sys.argv[2]
    proof = "--proof" in sys.argv
    extra = sys.argv[sys.argv.index("--gen") + 1] if "--gen" in sys.argv else "--n7 --root"
    cases = json.load(open(os.path.join(HERE, "cases.json")))
    if sel.startswith("shard:"):
        k, N = map(int, sel[6:].split("/"))
        idxs = [i for i in range(len(cases)) if i % N == k]
    else:
        idxs = [int(x) for x in sel.split(",")]
    done = set()
    if os.path.exists(out):
        done = {json.loads(l)["case"] for l in open(out)}
    tmp = os.path.join(HERE, "tmp"); os.makedirs(tmp, exist_ok=True)
    for ci in idxs:
        if ci in done:
            continue
        cls, q, nond7 = cases[ci]
        cnf = os.path.join(tmp, f"c{ci}.cnf")
        pre = os.path.join(os.environ.get("M9_PREGEN", "/nonexistent"), f"c{ci}.cnf")
        if os.path.exists(pre):   # CNF generated elsewhere (the server has no pynauty); its sha256 is recorded below
            import shutil; shutil.copy(pre, cnf); g = subprocess.CompletedProcess("", 0, "", "")
        else:
          g = sh(f"{NICE} python3 {HERE}/gen_ext9.py {HERE}/links_17_8.json {cls} {cnf} --q {q} {extra}" + (f" --nond7 {','.join(map(str, nond7))}" if nond7 else ""))
        assert g.returncode == 0, g.stderr
        rec = {"case": ci, "class": cls, "q": q, "nond7": nond7, "gen": extra, "cnf_sha256": sha(cnf)}
        drat = os.path.join(tmp, f"c{ci}.drat")
        t0 = time.time()
        tlim = int(float(sys.argv[sys.argv.index("--timeout") + 1])) if "--timeout" in sys.argv else 0
        if LRAT_MODE:
            drat = drat[:-5] + ".lrat"
        r = sh(f"{NICE} {CADICAL} -q" + (" --lrat --binary=false" if LRAT_MODE and proof else "")
               + (f" -t {tlim}" if tlim else "") + f" {cnf}" + (f" {drat}" if proof else ""))
        rec["wall_s"] = round(time.time() - t0, 2)
        st = [l for l in r.stdout.splitlines() if l.startswith("s ")]
        rec["status"] = st[0][2:] if st else f"UNKNOWN rc={r.returncode}"
        if rec["status"] == "SATISFIABLE":
            model = set()
            for l in r.stdout.splitlines():
                if l.startswith("v "):
                    model.update(int(x) for x in l[2:].split() if int(x) > 0)
            rec["model_pos"] = sorted(v for v in model if v <= 8 * 17)
            os.makedirs(os.path.join(HERE, "sat"), exist_ok=True)
            os.replace(cnf, os.path.join(HERE, "sat", f"c{ci}.cnf"))
        elif rec["status"] == "UNSATISFIABLE" and proof and LRAT_MODE:
            rec["lrat_bytes"] = os.path.getsize(drat); rec["lrat_sha256"] = sha(drat); rec["proof"] = "cadical-lrat"
            t1 = time.time()
            lc = sh(f"{NICE} {LRATCHECK} {cnf} {drat}")
            rec["lrat_check"] = "VERIFIED" if "c VERIFIED" in lc.stdout.splitlines() else "FAILED " + lc.stdout[-200:]
            heap = os.environ.get("CAKE_HEAP_MB", "12000")   # default 4096 MB is too small for 30-50 GB LRAT
            ck = sh(f"{NICE} {CAKE} --CML_HEAP_SIZE={heap} {cnf} {drat}")
            rec["cake_lpr"] = ck.stdout.strip().splitlines()[-1] if ck.stdout.strip() else "FAILED " + ck.stderr[-200:]
            rec["check_wall_s"] = round(time.time() - t1, 2)
            if "VERIFIED" in rec["cake_lpr"] and rec["lrat_check"] == "VERIFIED":
                os.remove(drat)
            else:   # keep proof and formula so the check can be redone without re-solving
                kd = os.path.join(HERE, "kept"); os.makedirs(kd, exist_ok=True)
                os.replace(drat, os.path.join(kd, os.path.basename(drat)))
                import shutil; shutil.copy(cnf, os.path.join(kd, os.path.basename(cnf)))
                rec["kept"] = os.path.join(kd, os.path.basename(drat))
        elif rec["status"] == "UNSATISFIABLE" and proof:
            rec["drat_bytes"] = os.path.getsize(drat); rec["drat_sha256"] = sha(drat)
            lrat = drat[:-5] + ".lrat"
            t1 = time.time()
            dt = sh(f"{NICE} {DRATTRIM} {cnf} {drat} -L {lrat} -t {os.environ.get('DRAT_TLIM', '200000')}")
            rec["drat_trim"] = "VERIFIED" if "s VERIFIED" in dt.stdout else "FAILED " + dt.stdout[-200:]
            ck = sh(f"{NICE} {CAKE} {cnf} {lrat}")
            rec["cake_lpr"] = ck.stdout.strip().splitlines()[-1] if ck.stdout.strip() else "FAILED " + ck.stderr[-200:]
            rec["check_wall_s"] = round(time.time() - t1, 2)
            for f in (drat, lrat):
                if os.path.exists(f):
                    os.remove(f)
        if rec["status"] != "UNSATISFIABLE" and os.path.exists(drat):
            os.remove(drat)          # partial proof of a timed-out case
        if os.path.exists(cnf):
            os.remove(cnf)
        with open(out, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec), flush=True)


if __name__ == "__main__":
    main()
