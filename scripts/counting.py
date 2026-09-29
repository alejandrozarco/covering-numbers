#!/usr/bin/env python3
"""Arithmetic behind the degree-forcing (zero-slack) arguments.

For a t-(v,k,1) covering with b blocks and a point p, the blocks through p with p
deleted form a (t-1)-(v-1,k-1,1) covering (the link of p), so
    b(p) >= C(v-1,k-1,t-1)           and      k*b = sum_p b(p).
If k*b == v*C(v-1,k-1,t-1) (zero slack) every b(p) equals C(v-1,k-1,t-1) and every
link is an OPTIMAL (t-1)-covering.  The same argument one level down gives the
minimum degree s_min = C(v-2,k-2,t-2) of a point inside a link, and for t=3 the
pair degree b(pq) >= C(v-2,k-2,1) = ceil((v-2)/(k-2)).
All numbers are checked here with exact integer arithmetic.
"""
from math import comb


def cdiv(a, b):
    return -(-a // b)


def schonheim(v, k, t):
    if t == 0:
        return 1
    return cdiv(v * schonheim(v - 1, k - 1, t - 1), k)


def report(v, k, t, b, c_link, name):
    print(f"== {name}: is there a {t}-({v},{k},1) covering with b={b} blocks?")
    print(f"   Schonheim L({v},{k},{t}) = {schonheim(v, k, t)}")
    print(f"   Schonheim for link  L({v-1},{k-1},{t-1}) = {schonheim(v-1, k-1, t-1)};"
          f" value used C({v-1},{k-1},{t-1}) = {c_link}")
    lb = cdiv(v * c_link, k)
    print(f"   (1): C({v},{k},{t}) >= ceil({v}*{c_link}/{k}) = {lb}")
    assert lb == b
    inc = k * b
    need = v * c_link
    print(f"   incidences k*b = {inc};  v*C(link) = {need};  slack = {inc - need}")
    assert inc == need, "not zero slack"
    r = c_link
    print(f"   => every point has degree exactly r = {r}; every link is an optimal"
          f" {t-1}-({v-1},{k-1},1) covering with {r} blocks")
    # inside a link (t-1 = 2): points of the link have degree >= ceil((v-2)/(k-2))
    smin = cdiv(v - 2, k - 2)
    link_inc = r * (k - 1)
    print(f"   link: {r} blocks of size {k-1} on {v-1} points; incidences {link_inc};"
          f" min link-degree s_min = ceil({v-2}/{k-2}) = {smin};"
          f" excess {link_inc - (v-1)*smin} over (v-1)*s_min")
    assert link_inc >= (v - 1) * smin
    # pair degrees in the whole design: b(pq) = degree of q in link(p) >= smin
    pair_inc = b * comb(k, 2)
    print(f"   pair degrees b(pq) >= {smin}; sum_q b(pq) = (k-1)*r = {(k-1)*r} per point;"
          f" total pair incidences {pair_inc} vs {comb(v,2)}*{smin} = {comb(v,2)*smin}")
    assert (k - 1) * r == link_inc
    trip_inc = b * comb(k, 3)
    print(f"   triple incidences {trip_inc} vs C(v,3) = {comb(v,3)}")
    # number of blocks NOT through a fixed point p
    print(f"   blocks not through p: {b - r} (subsets of the other {v-1} points)")
    return r, smin


def link_lower_bound_2(v, k):
    """Schonheim bound for 2-coverings."""
    return cdiv(v * cdiv(v - 1, k - 1), k)


if __name__ == "__main__":
    # C(16,7,2): Schonheim gives 7; the recorded value 8 is re-certified by SAT
    # (scripts/c16_7_2_lb.py, proof checked).  C(19,9,2) = 7 is pure Schonheim.
    print("L(16,7,2) =", link_lower_bound_2(16, 7), "(recorded C(16,7,2)=8; certified separately)")
    print("L(19,9,2) =", link_lower_bound_2(19, 9), "(= recorded C(19,9,2)=7)")
    assert link_lower_bound_2(19, 9) == 7
    report(17, 8, 3, 17, 8, "C(17,8,3) = 17 ?")
    report(20, 10, 3, 14, 7, "C(20,10,3) = 14 ?")
    # other zero-slack gap-1 cases listed in JOURNAL.md (for the record)
    for (v, k, t, low, cl) in [(15, 6, 3, 30, 12), (15, 5, 3, 54, 18)]:
        print(f"-- C({v},{k},{t}) low={low}: v*C(link)={v*cl}, k*low={k*low}, slack={k*low-v*cl}"
              f" (C({v-1},{k-1},{t-1}) assumed {cl})")
