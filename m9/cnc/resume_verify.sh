#!/bin/bash
# Re-run verification + record for one CnC case after an interrupted verify (verify_cnc.py skips leaves already verified
# whose rows are bound to this base CNF and cube). Same record as cnc_hard.sh. Env CNCDIR / CNCREC as in cnc_hard.sh.
# PAR=1: cake_lpr (12 GB heap) + lrat-trim (6 GB) in parallel left the server with 190 MB free (2026-10-31).
B=/mnt/ssd/covering-m9; PAR=${PAR:-1}; c=$1; D=${CNCDIR:-$B/cnc}; REC=${CNCREC:-$B/m9/runs/E_cnc.jsonl}
cd $D/c$c || exit 1; rm -f FAIL
DELETE_VERIFIED=1 VPAR=$PAR nice -n 19 python3 -u $B/sweep/verify_cnc.py base.cnf top.icnf close_run --check-all > verify.log 2>&1; rc=$?
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
[ "$D" != "$B/cnc" ] && ls $D/c*/DONE >/dev/null 2>&1 && [ $(ls $D/c*/DONE | wc -l) = $(ls -d $D/c*/ | wc -l) ] && touch $D/ALL.DONE
exit 0
