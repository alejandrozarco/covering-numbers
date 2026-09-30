#!/usr/bin/env python3
"""Exact MIP for the Key Lemma counterexample:
 14 rows (7-subsets of [14], duplicates allowed), weights w_i>=0 (sum 1, each <=1/8, sorted desc),
 weighted element marginals exactly 1/2, pairwise |∩|>=3, 3-wise ∩ nonempty,
 no 8 rows with all pairwise intersections <=3 (=> no SQS(8)-dual).  [--sqs: drop that, control]
 Symmetry: row0 = {0..6} (max weight); columns lex-sorted within {0..6} and within {7..13}."""
import highspy, itertools, sys, argparse
ap=argparse.ArgumentParser(); ap.add_argument('--sqs',action='store_true'); ap.add_argument('--rows',type=int,default=14)
ap.add_argument('--time',type=float,default=3600); ap.add_argument('--nocollex',action='store_true'); ap.add_argument('--pair',action='store_true',help='row1 = a lambda=3 partner of row0, fixed canonically')
ap.add_argument('--lexrows',action='store_true',help='rows>=2 lex non-increasing instead of weight-sorted (requires --pair)')
ap.add_argument('--distinct',action='store_true',help='rows pairwise distinct (strict lex); covers supports of size exactly R')
a=ap.parse_args()
R=a.rows; n=14
h=highspy.Highs(); h.setOptionValue('threads',1); h.setOptionValue('time_limit',a.time)
h.setOptionValue('random_seed',1)
inf=highspy.kHighsInf
nv=0; lb=[]; ub=[]; integ=[]
def var(l,u,i):
    global nv
    lb.append(l); ub.append(u); integ.append(i); nv+=1; return nv-1
x=[[var(0,1,1) for j in range(n)] for i in range(R)]
w=[var(0,1/8,0) for i in range(R)]
z=[[var(0,1/8,0) for j in range(n)] for i in range(R)]
A={}; E={}
for i,k in itertools.combinations(range(R),2):
    A[i,k]=[var(0,1,0) for j in range(n)]
    E[i,k]=var(0,1,1)
rows=[]
def con(coefs,l,u): rows.append((coefs,l,u))
for i in range(R): con({x[i][j]:1 for j in range(n)},7,7)
for j in range(n):
    v=1 if j<7 else 0; con({x[0][j]:1},v,v)
con({w[i]:1 for i in range(R)},1,1)
if a.lexrows:
    assert a.pair
    for i in range(2,R-1):
        c={}
        for j in range(n):
            c[x[i][j]]=c.get(x[i][j],0)+2**(n-1-j); c[x[i+1][j]]=c.get(x[i+1][j],0)-2**(n-1-j)
        con(c,1 if a.distinct else 0,inf)
for i in range(R-1):
    if a.lexrows: break
    if a.pair and i==0:
        for k in range(1,R): con({w[0]:1,w[k]:-1},0,inf)
        continue
    con({w[i]:1,w[i+1]:-1},0,inf)
if a.pair:
    r1=[1,1,1,0,0,0,0,1,1,1,1,0,0,0]
    for j in range(n): con({x[1][j]:1},r1[j],r1[j])
for i in range(R):
    for j in range(n):
        con({z[i][j]:1,w[i]:-1},-inf,0)
        con({z[i][j]:1,x[i][j]:-1/8},-inf,0)
        con({z[i][j]:1,w[i]:-1,x[i][j]:-1/8},-1/8,inf)
for j in range(n): con({z[i][j]:1 for i in range(R)},.5,.5)
for (i,k),av in A.items():
    for j in range(n):
        con({av[j]:1,x[i][j]:-1},-inf,0); con({av[j]:1,x[k][j]:-1},-inf,0)
        con({av[j]:1,x[i][j]:-1,x[k][j]:-1},-1,inf)
    con({v:1 for v in av},3,inf)
    c={v:1 for v in av}; c[E[i,k]]=1; con(c,4,inf)   # e_ik >= 4 - lambda
for i,k,l in itertools.combinations(range(R),3):
    bs=[var(0,1,0) for j in range(n)]
    for j in range(n):
        con({bs[j]:1,A[i,k][j]:-1},-inf,0); con({bs[j]:1,x[l][j]:-1},-inf,0)
    con({b:1 for b in bs},1,inf)
if not a.sqs:
    for sub in itertools.combinations(range(R),8):
        con({E[p]:1 for p in itertools.combinations(sub,2)},-inf,27)
if not a.nocollex:
    # columns lex non-increasing within each half, reading rows 1..R-1 (row 0 constant on each half)
    # encoded via weighted sums (valid lex for 0/1 vectors): sum_i 2^(R-1-i) x[i][j] >= same for j+1
    blocks=[range(0,3),range(3,7),range(7,11),range(11,14)] if a.pair else [range(0,7),range(7,14)]
    for half in blocks:
        hs=list(half)
        for j,j2 in zip(hs,hs[1:]):
            c={}
            for i in range(2 if a.pair else 1,R):
                c[x[i][j]]=c.get(x[i][j],0)+2**(R-1-i); c[x[i][j2]]=c.get(x[i][j2],0)-2**(R-1-i)
            con(c,0,inf)
lp=highspy.HighsLp()
lp.num_col_=nv; lp.num_row_=len(rows)
lp.col_cost_=[0.0]*nv; lp.col_lower_=lb; lp.col_upper_=ub
lp.row_lower_=[r[1] for r in rows]; lp.row_upper_=[r[2] for r in rows]
import numpy as np
starts=[];idx=[];vals=[]
# build row-wise then set as row-wise matrix
lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
for r in rows:
    starts.append(len(idx))
    for k,v in r[0].items(): idx.append(k); vals.append(float(v))
starts.append(len(idx))
lp.a_matrix_.start_=starts; lp.a_matrix_.index_=idx; lp.a_matrix_.value_=vals
lp.integrality_=[highspy.HighsVarType.kInteger if t else highspy.HighsVarType.kContinuous for t in integ]
h.passModel(lp)
print('vars',nv,'rows',len(rows),flush=True)
h.run()
st=h.getModelStatus(); print('status',h.modelStatusToString(st))
if st==highspy.HighsModelStatus.kOptimal:
    sol=h.getSolution().col_value
    for i in range(R):
        print(''.join(str(int(round(sol[x[i][j]]))) for j in range(n)), round(sol[w[i]],5))
