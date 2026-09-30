"""WLOG normalisations for the Key Lemma search (see FAMILY.md, Lemma N).
In any balanced 3-wise intersecting family there are S,T,U in the support with |S∩T|=|S∩U|=|T∩U|=3.
With S=row0, T=row1, U=row2 and H=S∩T, t=|S∩T∩U| in {1,2}, up to relabelling of [14]:"""
X  = [1]*7 + [0]*7                       # S = {0..6}
T  = [1,1,1,0,0,0,0,1,1,1,1,0,0,0]       # T = {0,1,2,7,8,9,10}; H={0,1,2}, S'={3..6}, T'={7..10}, O={11,12,13}
CASES = {
 # t=1: U∩H={0}, |U∩S'|=|U∩T'|=|U∩O|=2
 't1': dict(rows=[X, T, [1,0,0,1,1,0,0,1,1,0,0,1,1,0]],
            blocks=[[0],[1,2],[3,4],[5,6],[7,8],[9,10],[11,12],[13]]),
 # t=2: U∩H={0,1}, |U∩S'|=|U∩T'|=1, O ⊂ U
 't2': dict(rows=[X, T, [1,1,0,1,0,0,0,1,0,0,0,1,1,1]],
            blocks=[[0,1],[2],[3],[4,5,6],[7],[8,9,10],[11,12,13]]),
 'pair': dict(rows=[X, T], blocks=[[0,1,2],[3,4,5,6],[7,8,9,10],[11,12,13]]),
}

# ---- refinement of case t1 by a 4th row V: a maximum-weight set avoiding column 0 ----
# pair blocks of case t1 (S={0..6}, T={0,1,2,7,8,9,10}, U={0,3,4,7,8,11,12}; column 13 outside S∪T∪U)
PAIRS = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12)]
def v_shapes():
    """all count vectors (c12,c34,c56,c78,c910,c1112,c13) for V with 0 ∉ V, |V|=7, V meeting
    S∩T={0,1,2}, S∩U={0,3,4}, T∩U={0,7,8} and |V∩S|,|V∩T|,|V∩U| >= 3."""
    out = []
    import itertools
    for c in itertools.product(range(3), repeat=6):
        for c13 in (0, 1):
            if sum(c) + c13 != 7: continue
            c12, c34, c56, c78, c910, c1112 = c
            if min(c12, c34, c78) < 1: continue
            if c12 + c34 + c56 < 3 or c12 + c78 + c910 < 3 or c34 + c78 + c1112 < 3: continue
            out.append(c + (c13,))
    return out
def a_case(shape):
    V = [0] * 14; blocks = [[0]]
    for (a, b), cnt in zip(PAIRS, shape[:6]):
        if cnt >= 1: V[a] = 1
        if cnt == 2: V[b] = 1
        blocks += [[a], [b]] if cnt == 1 else [[a, b]]
    V[13] = shape[6]; blocks.append([13])
    return dict(rows=CASES['t1']['rows'] + [V], blocks=blocks)
for _s in v_shapes():
    CASES['A' + ''.join(map(str, _s))] = a_case(_s)
