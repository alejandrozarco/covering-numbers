from common import *
A=sqs_dual()
print([pc(a) for a in A], [pc(a&b) for a,b in itertools.combinations(A,2)][:5], min(pc(a&b&c) for a,b,c in itertools.combinations(A,3)))
Aset=set(A)
comp=[]
for m in MASK:
    if m in Aset: continue
    if all(pc(m&a)>=3 for a in A) and all(m&a&b for a,b in itertools.combinations(A,2)):
        comp.append(m)
print('compatible with SQS dual:',len(comp))
from collections import Counter
print(Counter(tuple(sorted(pc(m&a) for a in A)) for m in comp))
