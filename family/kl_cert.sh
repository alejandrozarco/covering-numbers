#!/bin/bash
# certified Key Lemma run: kl_cert.sh R A|B
R=$1; C=$2; P=ks/cert_${C}${R}
if [ $C = A ]; then F="--case t1 --maxthird"; else F="--case t2 --not1pair"; fi
nice -n 10 python3 keyprop2.py $R $P $F --every 8 && nice -n 10 python3 certify.py $P && nice -n 10 python3 check_ks2.py $P && nice -n 10 python3 prove.py $P.cnf runs/kl_cert.jsonl 36000
