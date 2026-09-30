import itertools
N=14
ALL=[s for s in itertools.combinations(range(N),7)]
MASK=[sum(1<<i for i in s) for s in ALL]
IDX={m:i for i,m in enumerate(MASK)}
pc=lambda x: bin(x).count('1')
def sqs8_planes():
    pts=list(range(8))
    planes=set()
    for a,b,c in itertools.combinations(pts,3):
        d=a^b^c
        planes.add(frozenset({a,b,c,d}))
    return sorted(planes,key=sorted)
def sqs_dual():
    pl=sqs8_planes(); assert len(pl)==14
    return [sum(1<<j for j,P in enumerate(pl) if p in P) for p in range(8)]
