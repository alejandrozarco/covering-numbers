"""Boolean part of the Key Lemma search (shared by the SMT and lazy-SMT drivers).
R rows x[i][j]: 7-subsets of [14] (duplicates allowed unless distinct=True), pairwise |∩| >= 3,
any 3 rows share a column, no 8 rows pairwise |∩| <= 3 (no SQS(8)-dual; skipped if sqs=True),
fixed leading rows and column lex inside blocks per the chosen case (cases.py),
rows after the fixed ones lex non-increasing, columns inside each block lex non-increasing
(read over the non-fixed rows)."""
import sys, itertools
sys.path.insert(0, '../scripts')
from cnflib import CNF
from cases import CASES

def build(R, case='t1', sqs=False, distinct=False, not1=False, lamcnt=False, not1pair=False, ret_c4=False, third=False, notrade=False, colcard=False, nbr=False, tripq=False, rowlex=True):
    """not1: add 'no triangle (rows 0,k,l pairwise |∩|=3) with |S0∩Sk∩Sl| = 1' (case t2 with row0 of max weight)"""
    n = 14; F = CNF(); c = CASES[case]; fixed = c['rows']; f0 = len(fixed)
    x = [[F.new() for j in range(n)] for i in range(R)]
    for i in range(R): F.exactly(x[i], 7)
    for i, r in enumerate(fixed):
        for j in range(n): F.add([x[i][j] if r[j] else -x[i][j]])
    y = {}; e = {}; c4 = {}; LAM = {}
    for i, k in itertools.combinations(range(R), 2):
        y[i, k] = [F.and_def([x[i][j], x[k][j]]) for j in range(n)]
        cnt = F._counter(y[i, k], 7 if lamcnt else 4); F._assert_true(cnt[3])
        if lamcnt: LAM[i, k] = cnt
        ev = F.new(); e[i, k] = ev; F.add([ev, cnt[4]]); c4[i, k] = cnt[4]
    for i, k, l in itertools.combinations(range(R), 3):
        zs = []
        for j in range(n):
            z = F.new(); F.add([-z, y[i, k][j]]); F.add([-z, x[l][j]]); zs.append(z)
        F.add(zs)
    Qv = {}
    if tripq:
        # Qv[i,k,l] <-> |S_i ∩ S_k ∩ S_l| >= 2   (full equivalence)
        for i, k, l in itertools.combinations(range(R), 3):
            ts = [F.and_def([y[i, k][j], x[l][j]]) for j in range(n)]
            Qv[i, k, l] = F._counter(ts, 2)[2]
    if nbr:
        # every support row S_i has lambda=3 partners of total weight >= 1/2 + 3 w_i > 1/2, each <= 1/8:
        # >= 5 rows k with |S_i∩S_k| = 3; row 0 (max weight w0 >= 1/R >= 1/14): mass >= 5/7 => >= 6.
        for i in range(R):
            F.atleast([-c4[min(i, k), max(i, k)] for k in range(R) if k != i], 6 if i == 0 else 5)
        # every lambda=3 pair (i,k) has a common lambda=3 neighbour l (mass >= 3(w_i+w_k) > 0)
        cc = lambda a, b: c4[min(a, b), max(a, b)]
        for i, k in itertools.combinations(range(R), 2):
            F.add([cc(i, k)] + [F.and_def([-cc(i, l), -cc(k, l)]) for l in range(R) if l not in (i, k)])
    if colcard:
        # every column lies in >= 4 rows and misses >= 4 rows (weights <= 1/8, column weight 1/2 both ways)
        for j in range(n):
            col = [x[i][j] for i in range(R)]
            F.atleast(col, 4); F.atmost(col, R - 4)
    if not1:
        for k, l in itertools.combinations(range(1, R), 2):
            ts = [F.and_def([y[0, k][j], x[l][j]]) for j in range(n)]
            ct = F._counter(ts, 2)
            F.add([c4[0, k], c4[0, l], c4[k, l], ct[2]])
    T3 = {}
    if third:
        # T3[k] <-> (|S0∩Sk| = |S1∩Sk| = 3 and |S0∩S1∩Sk| = 1)  (S0∩S1 = columns 0,1,2)
        for k in range(3, R):
            ct = F._counter([x[k][0], x[k][1], x[k][2]], 2)
            ex1 = F.new(); F.add([-ex1, -ct[2]])            # ex1 -> at most 1 of H (at least 1 holds anyway)
            F.add([ex1, ct[2]])
            T3[k] = F.and_def([-c4[0, k], -c4[1, k], ex1])
    if not1pair:
        # no row l with |S0∩Sl|=|S1∩Sl|=3 and |S0∩S1∩Sl|=1  (S0∩S1 = columns 0,1,2 in every case)
        for l in range(2, R):
            ct = F._counter([x[l][0], x[l][1], x[l][2]], 2)
            F.add([c4[0, l], c4[1, l], ct[2]])
    if not sqs:
        for sub in itertools.combinations(range(R), 8):
            F.add([-e[p] for p in itertools.combinations(sub, 2)])
    if rowlex:
        for i in range(f0, R - 1): F.lex_geq(x[i], x[i + 1])
    for blk in c['blocks']:
        for j, j2 in zip(blk, blk[1:]):
            F.lex_geq([x[i][j] for i in range(f0, R)], [x[i][j2] for i in range(f0, R)])
    if notrade:
        # vertex supports are linearly independent: forbid 1_a + 1_b = 1_c + 1_d  (a<b, c<d, all distinct)
        OR = {}
        for i, k in itertools.combinations(range(R), 2):
            OR[i, k] = []
            for j in range(n):
                o = F.new(); F.add([-o, x[i][j], x[k][j]]); F.add([o, -x[i][j]]); F.add([o, -x[k][j]]); OR[i, k].append(o)
        def xor(a, b):
            v = F.new(); F.add([-v, a, b]); F.add([-v, -a, -b]); return v   # v -> a xor b
        prs = list(itertools.combinations(range(R), 2))
        for p, q in itertools.combinations(prs, 2):
            if set(p) & set(q): continue
            F.add([xor(y[p][j], y[q][j]) for j in range(n)] + [xor(OR[p][j], OR[q][j]) for j in range(n)])
    if distinct:
        for i, k in itertools.combinations(range(R), 2):
            d = []
            for j in range(n):
                v = F.new(); F.add([-v, x[i][j], x[k][j]]); F.add([-v, -x[i][j], -x[k][j]]); d.append(v)
            F.add(d)
    if lamcnt: return F, x, LAM
    if tripq: return F, x, c4, T3, Qv
    if ret_c4: return (F, x, c4, T3) if third else (F, x, c4)
    return F, x
