#!/usr/bin/env python3
"""Driver: decide whether a zero-slack 3-(v,k,1) covering with b blocks exists.

  1. link classification: optimal 2-(v-1,k-1,1) coverings with r blocks
     (enum_links + classify_links), cached in data/links_{v-1}_{k-1}.json
  2. one extension CNF per class (gen_ext.py --aut --pairs --root)
  3. CaDiCaL on each; UNSAT -> (if --proof) DRAT proof, drat-trim check that
     also emits LRAT, cake_lpr check of the LRAT; SAT -> decode, write block
     file, run the independent checker.
Results are appended to runs/{tag}/results.jsonl (resumable: finished classes
are skipped).
usage: run_case.py v k b r [--proof] [--timeout S] [--only i,j,..]
"""
import sys, os, json, subprocess, time, math, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAT = os.path.expanduser(os.environ.get("SAT_TOOLS", "~/sat"))  # dir containing cadical/, drat-trim/, cake_lpr/ builds
CADICAL = f"{SAT}/cadical/build/cadical"
DRATTRIM = f"{SAT}/drat-trim/drat-trim"
CAKE = f"{SAT}/cake_lpr/cake_lpr"
S = os.path.join(ROOT, "scripts")


def sh(cmd, **kw):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)


def sha(fn):
    h = hashlib.sha256()
    with open(fn, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def links(n, kk, r):
    """classification of optimal 2-(n,kk,1) coverings with r blocks"""
    out = os.path.join(ROOT, "data", f"links_{n}_{kk}.json")
    if os.path.exists(out):
        return json.load(open(out))
    smin = -(-(n - 1) // (kk - 1))
    excess = r * kk - n * smin
    fix = 1 if excess < n else 0     # then some point has degree exactly smin
    raw = os.path.join(ROOT, "data", f"links_{n}_{kk}_raw.txt")
    if not os.path.exists(raw):
        res = sh(f"nice -n 10 {S}/enum_links {n} {r} {kk} {smin} {fix} > {raw}")
        print(res.stderr.strip(), flush=True)
    res = sh(f"nice -n 10 python3 {S}/classify_links.py {n} {r} {kk} {smin} {raw} {out} {fix}")
    print(res.stdout.strip(), res.stderr.strip()[-2000:], flush=True)
    assert res.returncode == 0
    return json.load(open(out))


def main():
    v, k, b, r = map(int, sys.argv[1:5])
    proof = "--proof" in sys.argv
    timeout = None
    if "--timeout" in sys.argv:
        timeout = float(sys.argv[sys.argv.index("--timeout") + 1])
    only = None
    if "--only" in sys.argv:
        only = [int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(",")]
    tag = f"C{v}_{k}_3_b{b}"
    rdir = os.path.join(ROOT, "runs", tag)
    cdir = os.path.join(ROOT, "cnf", tag)
    pdir = os.path.join(ROOT, "proofs", tag)
    for d in (rdir, cdir, pdir):
        os.makedirs(d, exist_ok=True)
    data = links(v - 1, k - 1, r)
    ncl = len(data["classes"])
    print(f"{tag}: {ncl} link classes", flush=True)
    resf = os.path.join(rdir, "results.jsonl")
    done = set()
    if os.path.exists(resf):
        for line in open(resf):
            done.add(json.loads(line)["class"])
    m = b - r
    for idx in range(ncl):
        if idx in done or (only is not None and idx not in only):
            continue
        cnf = os.path.join(cdir, f"e{idx}.cnf")
        g = sh(f"python3 {S}/gen_ext.py {v} {k} {b} {os.path.join(ROOT, 'data', f'links_{v-1}_{k-1}.json')} {idx} {cnf} --aut --pairs --root")
        assert g.returncode == 0, g.stderr
        hdr = open(cnf).read(4096).split("p cnf ")[1].split("\n")[0].split()
        rec = {"class": idx, "vars": int(hdr[0]), "clauses": int(hdr[1]), "cnf_sha256": sha(cnf)}
        t0 = time.time()
        drat = os.path.join(pdir, f"e{idx}.drat")
        cmd = f"nice -n 10 {CADICAL} -q {cnf}" + (f" {drat}" if proof else "")
        if timeout:
            cmd = f"timeout {timeout} " + cmd
        res = sh(cmd)
        rec["solve_s"] = round(time.time() - t0, 3)
        status = [l for l in res.stdout.splitlines() if l.startswith("s ")]
        rec["status"] = status[0][2:] if status else f"UNKNOWN(rc={res.returncode})"
        if rec["status"] == "SATISFIABLE":
            model = set()
            for l in res.stdout.splitlines():
                if l.startswith("v "):
                    model.update(int(x) for x in l[2:].split() if int(x) > 0)
            blocks = [[0] + [q + 1 for q in B] for B in data["classes"][idx]["blocks"]]
            for j in range(m):
                blocks.append([p for p in range(1, v) if 1 + j * (v - 1) + (p - 1) in model])
            bf = os.path.join(rdir, f"covering_e{idx}.txt")
            with open(bf, "w") as f:
                f.write(f"# candidate 3-({v},{k},1) covering with {b} blocks from link class {idx}\n")
                for B in blocks:
                    f.write(" ".join(map(str, B)) + "\n")
            chk = sh(f"python3 {S}/check_covering.py {v} {k} 3 {bf}")
            rec["check"] = chk.stdout.strip()
            rec["covering_file"] = os.path.relpath(bf, ROOT)
            if os.path.exists(drat):
                os.remove(drat)
        elif rec["status"] == "UNSATISFIABLE" and proof:
            rec["drat_bytes"] = os.path.getsize(drat)
            lrat = os.path.join(pdir, f"e{idx}.lrat")
            t1 = time.time()
            dt = sh(f"nice -n 10 {DRATTRIM} {cnf} {drat} -L {lrat} -t 20000")
            rec["drat_trim_s"] = round(time.time() - t1, 3)
            rec["drat_trim"] = "VERIFIED" if "s VERIFIED" in dt.stdout else "FAILED:" + dt.stdout[-300:]
            t1 = time.time()
            ck = sh(f"nice -n 10 {CAKE} {cnf} {lrat}")
            rec["cake_lpr_s"] = round(time.time() - t1, 3)
            rec["cake_lpr"] = ck.stdout.strip().splitlines()[-1] if ck.stdout.strip() else "FAILED:" + ck.stderr[-300:]
            rec["lrat_bytes"] = os.path.getsize(lrat)
            rec["drat_sha256"] = sha(drat)
            # keep proofs compressed
            sh(f"xz -T1 -f {drat}; xz -T1 -f {lrat}")
        with open(resf, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec), flush=True)
        if rec["status"] == "SATISFIABLE" and "--stop-on-sat" in sys.argv:
            break


if __name__ == "__main__":
    main()
