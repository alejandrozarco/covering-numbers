#!/bin/bash
# Controlled timing: exact case-A instance at s=R, lex rows (baseline, = xA<R> settings) vs --wsort.
# Runs sequentially under the same load; output prefixes under kl14_proto/ (never touches ks/).
# Usage: run_wsort_test.sh R      (R = 11 or 12; ~1-10 min each under load)
cd "$(dirname "$0")/.."
R=$1
for v in lex wsort; do
  extra=""; [ $v = wsort ] && extra="--wsort"
  /usr/bin/time -p nice -n 10 python3 klprop.py $R kl14_proto/${v}A$R --case t1 --third --nbr --exact $extra 2>&1 | tail -3 | sed "s/^/$v /"
done
