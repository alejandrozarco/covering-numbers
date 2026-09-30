#!/bin/bash
# trim (lrat-trim core), certify, check and store every refuted s=14 cube/sub-cube listed on stdin
# (one prefix name per line, e.g. c00100 or c00000_01) as kl_certs/A14_<name>.{cert.json,cnf}.xz
cd "$(dirname "$0")"
while read n; do
  [ -f kl_certs/A14_$n.cert.json.xz ] && continue
  nice -n 10 python3 trim_cube.py ks/$n && nice -n 10 python3 klcertify.py ks/${n}T > /dev/null \
   && nice -n 10 python3 klcheck.py ks/${n}T | cut -c1-70 \
   && xz -T1 -c ks/${n}T.cert.json > kl_certs/A14_$n.cert.json.xz && xz -T1 -c ks/${n}T.cnf > kl_certs/A14_$n.cnf.xz \
   || echo "FAIL $n"
done
