#!/bin/bash
# run all case-A subcases at R rows with CDCL(T); log to runs/Asub_R.log
R=$1; shift
for c in $(cat runs/Acases.txt); do
  nice -n 10 python3 keyprop2.py $R ks/sub_${c}_$R --case $c --maxthird --avoid0 --colcard --every 8 "$@" | tail -1 | sed "s/^/$c /"
done > runs/Asub_$R.log 2>&1
