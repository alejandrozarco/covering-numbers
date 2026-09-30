#!/bin/bash
# Cube profile (KL14_IDEAS.md §4.1): the 4 sign patterns of (p_{0,3}, p_{0,4}) at s=R, run sequentially with the
# pipeline's klprop.py (multi-literal --cube), output under kl14_proto/.  Compare the summed CPU with the unsplit
# baseline (kl14_proto/lexA<R>) and see which cubes are cheap.
cd "$(dirname "$0")/.."
R=$1
for c in 1,1 1,0 0,1 0,0; do
  a=${c%,*}; b=${c#*,}
  /usr/bin/time -p nice -n 10 python3 klprop.py $R kl14_proto/cube${R}_p03_${a}_p04_${b} --case t1 --third --nbr --exact --cube p,0,3,$a:p,0,4,$b 2>&1 | grep -E "^R=|^user" | tr '\n' ' ' | sed "s/^/cube p03=$a p04=$b: /"; echo
done
