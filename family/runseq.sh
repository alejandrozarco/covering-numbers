#!/bin/bash
# run z3 on a list of smt files sequentially, logging to runs/z3_<base>.log
for f in "$@"; do b=$(basename $f .smt2); nice -n 10 python3 runsmt.py $f > runs/z3_$b.log 2>&1; done
