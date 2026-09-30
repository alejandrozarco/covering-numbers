# Delsarte LP in J(14,7): balanced distribution (V1-component 0), support pairwise |S∩T|>=3.
# minimize collision probability c = a_0.
import itertools, numpy as np
from fractions import Fraction
from math import comb
n,k=14,7
# Eberlein/Hahn: eigenvalue P_j(i) of A_i on V_j, via Eberlein polynomial
def E(i,j):  # eigenvalue of distance-i graph on V_j
    return sum((-1)**h*comb(j,h)*comb(k-j,i-h)*comb(n-k-j,i-h) for h in range(i+1))
P=[[E(i,j) for i in range(k+1)] for j in range(k+1)]  # P[j][i]
m=[comb(n,j)-(comb(n,j-1) if j>0 else 0) for j in range(k+1)]
v=[comb(k,i)*comb(n-k,i) for i in range(k+1)]
# Q_j(i) = m_j * P_j(i) / v_i
Q=[[Fraction(m[j]*P[j][i],v[i]) for i in range(k+1)] for j in range(k+1)]
if __name__=='__main__':
    import scipy.optimize as so
    allowed=[0,1,2,3,4]   # distance i = 7-|S∩T|
    for extra in [None]:
        c=np.zeros(k+1); c[0]=1
        A_eq=[[1]*(k+1)]; b_eq=[1]
        A_eq.append([float(Q[1][i]) for i in range(k+1)]); b_eq.append(0)
        for i in range(5,8):
            r=[0]*(k+1); r[i]=1; A_eq.append(r); b_eq.append(0)
        A_ub=[[-float(Q[j][i]) for i in range(k+1)] for j in range(2,k+1)]; b_ub=[0]*(k-1)
        res=so.linprog(c,A_ub=A_ub,b_ub=b_ub,A_eq=A_eq,b_eq=b_eq,bounds=[(0,None)]*(k+1),method='highs')
        print(res.status,res.fun,res.x)
    print('Q1',Q[1])
