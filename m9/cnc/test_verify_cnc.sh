#!/bin/bash
# Regression for the Astra audit of 2026-11-01. Satisfiable F=(x), cubes x and -x; checkers are stubs that reject only
# leaf 0. A restarted verifier must not accept. usage: test_verify_cnc.sh [verify_cnc.py]   (exit 0 = pass)
V=$(realpath "${1:-$(dirname "$0")/verify_cnc.py}"); T=$(mktemp -d); cd $T; mkdir bin tmpv d d/proofs d/splits
printf '#!/bin/bash\necho "s UNSATISFIABLE"; touch "${@: -1}"\n' > bin/cad
printf '#!/bin/bash\ntouch "$3"; exit 20\n' > bin/trim
printf '#!/bin/bash\nexit 0\n' > bin/check
printf '#!/bin/bash\ngrep -q "^1 0$" "${@: -2:1}" && grep -q "^p cnf 1 2" "${@: -2:1}" && [ "$(grep -c "^1 0$" "${@: -2:1}")" = 2 ] && { echo FAIL; exit 1; }; echo "s VERIFIED UNSAT"\n' > bin/cake
chmod +x bin/*; printf 'p cnf 1 1\n1 0\n' > base.cnf; printf 'a 1 0\na -1 0\n' > top.icnf
printf '{"id":"0","result":"UNSAT"}\n{"id":"1","result":"UNSAT"}\n' > d/ledger.jsonl
echo x | gzip > d/proofs/0.lrat.gz; echo x | gzip > d/proofs/1.lrat.gz
run() { VTMP=$T/tmpv CADICAL=$T/bin/cad LRAT_TRIM=$T/bin/trim LRAT_CHECK=$T/bin/check CAKE=$T/bin/cake python3 $V base.cnf top.icnf d --check-all > out.txt 2>&1; echo $?; }
r1=$(run); r2=$(run)
echo "first run rc $r1, restart rc $r2 (both must be 3)"
python3 - <<'P'
import json
R = {}
for l in open('d/verified_leaves.jsonl'): r = json.loads(l); R[r['id']] = r
R['0']['verified'] = True; R['1']['base_sha256'] = '0' * 64
open('d/verified_leaves.jsonl', 'w').write(''.join(json.dumps(r) + '\n' for r in R.values()))
P
rm -f d/proofs/*.gz; r3=$(run); echo "stale row, proofs gone rc $r3 (must be 5)"; cd /; rm -rf $T
[ "$r1" = 3 ] && [ "$r2" = 3 ] && [ "$r3" = 5 ] && echo PASS || { echo FAIL; exit 1; }
