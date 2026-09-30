#!/bin/bash
# Run the 32 cubes on p_{0,3..7} for case A exact s=14 with at most $1 concurrent klprop workers.
# Lemmas of (at most 3) already refuted cubes are seeded (--seed) into newly started cubes; only
# raw.json files not modified for >= 120 s are used (avoids reading a file being written).
# Crashed cubes (log with Traceback) are restarted.  Loops until all 32 cubes are refuted.
N=${1:-5}
mkdir -p runs/cube14
while true; do
  left=0
  for b in $(seq 0 31); do
    c=""; name="c"
    for i in 0 1 2 3 4; do v=$(( (b >> i) & 1 )); k=$((3+i)); c="$c${c:+:}p,0,$k,$v"; name="$name$v"; done
    f=runs/cube14/$name.log
    grep -q UNSAT $f 2>/dev/null && continue
    left=1
    grep -q Traceback $f 2>/dev/null && rm -f $f
    [ -f $f ] && continue
    while [ $(pgrep -f "klprop.py 14 ks/c" | wc -l) -ge $N ]; do sleep 5; done
    SEEDS=""
    for g in $(grep -l UNSAT runs/cube14/*.log 2>/dev/null); do
      n=$(basename $g .log); r=ks/$n.raw.json
      [ -f $r ] && [ $(( $(date +%s) - $(stat -f %m $r) )) -ge 120 ] && SEEDS="$SEEDS --seed $r"
      [ $(echo $SEEDS | wc -w) -ge 6 ] && break
    done
    nohup nice -n 10 python3 klprop.py 14 ks/$name --case t1 --third --nbr --exact --cube $c $SEEDS > $f 2>&1 &
  done
  [ $left = 0 ] && break
  sleep 30
done
