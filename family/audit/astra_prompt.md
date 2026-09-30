You are an independent, adversarial referee. Read-only: do not modify files; small test programs under /tmp only
(< 5 min, ≤ 2 threads). Never kill processes you did not start.
Subject: family/FAMILY.md (and the scripts it cites) claiming C(2m,m,3) = 14 iff 4 | m (m ≥ 4) and C(2m,m,3) = 15 for
all m ≥ 6 with 4 ∤ m, m ≠ 9 (covering numbers: min number of m-subsets of a 2m-set covering all 3-subsets).
Structure: (R) dual reformulation (14 blocks ⇒ each point in exactly 7 blocks, each block of size m ⇒ multiset of 2m
7-subsets of [14], 3-wise intersecting, each element in exactly m); (U14) blow-up of SQS(8); (U15) blow-up of PG(3,2);
(Rel) relaxation facts; (Red) reduction Key Lemma ⇒ theorem; (KL) Key Lemma, certified by a CDCL(T)+Farkas+DRAT/LRAT
pipeline (family/verify_kl.sh).
Find a gap: (1) check (R) in both directions incl. the link lower bound C(2m−1,m−1,2) ≥ 7 for all m ≥ 5, repeated
blocks/points, multiset subtleties; (2) the constructions U14/U15 (verify small cases computationally); (3) the
reduction proof §4 — does KL (½-balanced distributions on 3-wise intersecting families contain an SQS(8)-dual) really
force 4 | m, incl. integrality arguments; (4) the KL certification: are the case split and symmetry reductions sound
and exhaustive, do the certificates certify what is claimed (spot-check some with the checkers), what is still
uncertified; (5) m = 9 and small m exceptions. Verdict: CORRECT / CORRECT WITH GAPS (list) / FLAWED, with confidence.
