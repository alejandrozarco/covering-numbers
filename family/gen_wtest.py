#!/usr/bin/env python3
"""SMT: case A normalisation (max weights), SQS allowed, and NO row equal to the SQS-completion
W = {0,5,6,9,10,11,12} of the triangle (rows 0,1,2).  Usage: gen_wtest.py R out.smt2 [extra gen_smt2 flags]"""
import sys, subprocess
R, out = sys.argv[1], sys.argv[2]
sys.argv = ['gen_smt2.py', R, 't1', out, '--sqs', '--maxw', '--maxpartner', '--maxthird'] + sys.argv[3:]
exec(open('gen_smt2.py').read())
W = [1,0,0,0,0,1,1,0,0,1,1,1,1,0]
s = open(out).read()
extra = ''.join('(assert (or ' + ' '.join((f'(not b{x[i][j]})' if W[j] else f'b{x[i][j]}') for j in range(14)) + '))\n' for i in range(3, int(R)))
open(out, 'w').write(s.replace('(check-sat)', extra + '(check-sat)'))
