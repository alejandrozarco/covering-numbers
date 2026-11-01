#!/bin/bash
# Cube-and-conquer for the C(18,9,3) cases that exceed 16 h (server). Per case: march_cu depth 12, every cube
# solved with an LRAT proof (cap 7200 s, capped cubes re-split at depth 4), then verify_cnc.py --check-all: the cube
# tree closes, every leaf proof passes lrat-trim + lrat-check + cake_lpr, and the negation of all leaves is UNSAT with
# a proof checked the same way (cover). Only then a record goes to m9/runs/E_cnc.jsonl. nice 19, PAR cubes at a time.
# usage: cnc_hard.sh PAR case1 case2 ...      markers: cnc/c<case>/DONE or FAIL; cnc/ALL.DONE
# env CNCDIR (default cnc) and CNCREC (default m9/runs/E_cnc.jsonl) keep a rerun apart from the original run. Leaf checks
# run one at a time (VPAR): cake_lpr + lrat-trim in parallel left the server with 190 MB free, 2026-10-31.
B=/mnt/ssd/covering-m9; PAR=$1; shift; D=${CNCDIR:-$B/cnc}; REC=${CNCREC:-$B/m9/runs/E_cnc.jsonl}
M=~/sat/CnC/march_cu/march_cu
for c in "$@"; do
  W=$D/c$c; mkdir -p $W; cd $W; [ -f DONE ] && continue
  [ -f base.cnf ] || cp $B/m9/pregen/c$c.cnf base.cnf
  [ -s top.icnf ] || nice -n 19 $M base.cnf -d ${TOPD:-12} -o top.icnf > march.log 2>&1
  nice -n 19 python3 -u $B/sweep/cnc_sweep.py base.cnf top.icnf run 7200 4 $PAR > run.log 2>&1
  if grep -q "WITNESS\|ERRORS" run.log; then touch FAIL; echo "$c: SAT or error, see $W/run.log" >> $D/ALERT; continue; fi
  DELETE_VERIFIED=1 VPAR=${VPAR:-1} nice -n 19 python3 -u $B/sweep/verify_cnc.py base.cnf top.icnf close_run --check-all > verify.log 2>&1; rc=$?
  if [ $rc = 0 ] && grep -q "COVER VERIFIED" verify.log && grep -q "PROOFS: .* 0 FAILED" verify.log; then
    python3 - "$c" <<'P' >> $REC
import json, sys, hashlib, collections
c = int(sys.argv[1]); R = [json.loads(l) for l in open('close_run/ledger.jsonl')]
n = collections.Counter(r['result'] for r in R)
print(json.dumps({"case": c, "status": "UNSATISFIABLE", "proof": "cnc-lrat", "cnf_sha256": hashlib.sha256(open('base.cnf','rb').read()).hexdigest(),
  "cubes": dict(n), "cube_seconds": round(sum(r['secs'] for r in R)), "lrat_check": "VERIFIED", "cake_lpr": "s VERIFIED UNSAT",
  "cover": "VERIFIED", "verified_leaves_sha256": hashlib.sha256(open('close_run/verified_leaves.jsonl','rb').read()).hexdigest(),
  "verify_log": open('verify.log').read()[-600:]}))
P
    touch DONE; rm -rf close_run/proofs
  else touch FAIL; echo "$c: verify rc $rc" >> $D/ALERT; fi
done
touch $D/ALL.DONE
