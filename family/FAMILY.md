# The family C(2m, m, 3): when is the Schönheim bound 14 attained?

Status date: 2026-09-30 (Key Lemma certified, commit 5fbc22b).  All paths relative to `family/`.

## 0. Summary

| statement | status |
|---|---|
| (R) for m ≥ 4: C(2m,m,3) = 14 ⇔ ∃ multiset of 2m 7-subsets of [14], any three sharing an element, every element in exactly m of them | **proved** (§1) |
| (U14) 4 \| m ⇒ C(2m,m,3) = 14 (blow-up of SQS(8)) | **proved** (§2) |
| (Rel) balanced relaxation: \|S∩T\| ≥ 3, μ(S) ≤ 1/8, SQS(8)-dual characterisation | **proved** (§3) |
| (Red) Key Lemma ⇒ [C(2m,m,3) = 14 ⇔ 4 \| m] for every m ≥ 4 | **proved** (§4) |
| (KL) every ½-balanced 3-wise intersecting family of 7-subsets of [14] contains an SQS(8)-dual | **certified** (§5.4: 41 certificates, 1 038 979 exact Farkas lemmas; `verify_kl.sh` PASS) |
| C(2m,m,3) ≥ 15 directly for m = 5,6,7,9 (and m = 10, session 1) | **certified** (DRAT; drat-trim + cake_lpr) (§6) |
| (U15) C(2m,m,3) ≤ 15 for every m ≥ 6, m ≠ 9 (blow-up of PG(3,2)) | **proved** (§7) |
| C(18,9,3) ∈ {15,16} | open (§7.3) |
| t = 4 (dropped for now): reduction, AG(4,2)/PG(4,2) constructions | partial (§8) |

Consequence (KL + §4 + §7): **C(2m,m,3) = 14 iff 4 | m (m ≥ 4); C(2m,m,3) = 15 for every m ≥ 6 with
4 ∤ m, m ≠ 9; C(18,9,3) ∈ {15,16}; C(10,5,3) = 17 (LJCR).**  This settles all LJCR entries
C(2m,m,3) ∈ [14,15] (m = 10,11,13,14,15,17,…; all = 15) and raises the LJCR lower bound of
C(18,9,3) from 14 to 15 (also certified directly, §6).

## 1. Reformulation (R)

Let m ≥ 4, v = 2m, k = m.  Schönheim: C(2m,m,3) ≥ ⌈(2m/m)⌈(2m−1)/(m−1)⌈(2m−2)/(m−2)⌉⌉⌉.
Since (2m−2)/(m−2) = 2 + 2/(m−2) ∈ (2,3] for m ≥ 4, the inner ceiling is 3; 3(2m−1)/(m−1) = 6 + 3/(m−1)
∈ (6,7], so the middle ceiling is 7, and the bound is 14.

**(⇒)** Let B_1,…,B_14 be m-subsets of a 2m-set V covering all triples.  For p ∈ V the link
{B_j∖{p} : p ∈ B_j} is a 2-covering of V∖{p} (2m−1 points) by (m−1)-sets.  In it every point q lies in
at least ⌈(2m−2)/(m−2)⌉ = 3 link blocks (the link blocks through q, minus q, cover the other 2m−2
points with (m−2)-sets), so Σ(link block sizes) ≥ 3(2m−1), i.e. deg(p) ≥ ⌈3(2m−1)/(m−1)⌉ = 7.
Since Σ_p deg(p) = 14m, every point has degree exactly 7.  Put S_p = {j : p ∈ B_j} ⊂ [14]: |S_p| = 7,
element j lies in |B_j| = m of the S_p, and a triple {p,q,r} is covered iff S_p∩S_q∩S_r ≠ ∅.
**(⇐)** Given such a multiset (S_p)_{p ∈ V}, B_j := {p : j ∈ S_p} are 14 m-subsets covering every triple.

Equivalently: w : ([14] choose 7) → Z_{≥0} with Σw = 2m, every element-degree Σ_{S∋j} w_S = m, and
support F = {w > 0} **3-wise intersecting** (any three members, repetitions allowed, share an element —
for 2m ≥ 3 points the covering condition forces this, including pairwise intersection).
μ = w/(2m) is then a probability distribution on F with all element marginals ½ ("½-balanced").

Checks: m = 4 SAT (SQS(8)); m = 5, 6, 7 UNSAT with certified proofs (§6) — consistent with LJCR
C(10,5,3) = 17, C(12,6,3) = C(14,7,3) = 15.

## 2. 4 | m ⇒ C(2m,m,3) = 14 (U14)

SQS(8) = AG(3,2) with its 14 planes: any ≤ 3 points lie in a plane.  Replace each of the 8 points by a
class of m/4 points; the 14 planes become m-sets.  Three new points lie in ≤ 3 classes, whose original
points lie in a common plane.  Files: `coverings/C{2m}_{m}_3_b14.txt` (m = 4,…,28, step 4), all
verified by `../scripts/check_covering.py`.  (Dually: the multiset = the 8 sets S_p, p ∈ AG(3,2), each
with multiplicity m/4; its support is the **SQS(8)-dual** A: 8 sets pairwise meeting in 3, any three
meeting in exactly 1.)

## 3. The ½-balanced relaxation (Rel)

Let μ be a probability distribution on a 3-wise intersecting family F ⊂ ([14] choose 7) (F = supp μ)
with all marginals ½.

**Lemma 3.1** S ≠ T ∈ F ⇒ |S∩T| ≥ 3.  *Proof.* H = S∩T meets every member, and |U∩H| = |H| for
U ∈ {S,T}.  Σ_U μ_U|U∩H| = |H|/2 (marginals), hence |H|/2 − 1 ≥ (μ_S+μ_T)(|H|−1).  For |H| ≤ 2 the left side is ≤ 0 and the right side ≥ 0, with
equality on the left only for |H| = 2, where the right side is > 0; so |H| ≥ 3. ∎

**Lemma 3.2** μ_S ≤ 1/8 for all S; equality iff every other member meets S in exactly 3 points.
*Proof.* 7/2 = Σ_T μ_T|S∩T| ≥ 7μ_S + 3(1−μ_S). ∎  (In the finite problem: multiplicities ≤ m/4.)

More precisely Σ_{T≠S} μ_T(|S∩T|−3) = ½ − 4μ_S, so the "λ = 3 neighbourhood" N(S) = {T : |S∩T| = 3}
has mass ≥ ½ + 3μ_S.

**Lemma 3.3** (a) Eight members pairwise meeting in exactly 3 points form an SQS(8)-dual.
(b) If |F| ≤ 8 then |F| = 8 and F is an SQS(8)-dual with μ uniform.
*Proof.* (a) Dually: 8 points, 14 blocks (elements), degrees d_j with Σd_j = 56, every pair of points in
exactly 3 blocks: Σ C(d_j,2) = 84 ⇒ Σ d_j² = 224 = 56²/14, so all d_j = 4: a 2-(8,4,3) design with
14·4 = 56 = C(8,3) triple slots and every triple covered (3-wise intersecting) ⇒ every triple exactly once:
an SQS(8), unique up to isomorphism.  (b) by 3.2 all μ_S = 1/8 and equality holds in 3.2. ∎

**Remark (Füredi).** If μ_S = 1/8 then the traces {S∩T : T ≠ S} are triples carrying a distribution with
uniform marginals 3/7, i.e. an intersecting 3-graph with fractional matching number 7/3 = k−1+1/k;
by Füredi (Combinatorica 1 (1981) 155–162) it is a Fano plane (the derived design of SQS(8)).

**Remark.** The Delsarte LP (only pairwise information: inner distribution supported on |S∩T| ≥ 3 plus
the balance condition = vanishing first eigenspace component) allows collision probability Σμ² = 1/78
(`delsarte.py`), so 3-wise information is essential; and balanced families need not be *unions* of
SQS-duals with a unique structure: e.g. two SQS-duals sharing 4 sets can lie in one 3-wise intersecting
family (`explore3.py`), giving non-uniform balanced μ.  All vertices found in random/greedy searches
(`explore4.py`, `explore5.py`, `explore6.py`: 198 240 LP vertices, 15+ random maximal balanced families)
are SQS(8)-duals.

## 4. Reduction theorem (Red)

**Key Lemma (KL).** If μ is ½-balanced on a 3-wise intersecting F ⊂ ([14] choose 7), then F contains an
SQS(8)-dual.  Equivalently: every vertex of the polytope P(F) = {μ ≥ 0 on F, Σμ = 1, marginals ½} is
uniform on an SQS(8)-dual.  (⇒: if supp ν ⊇ A for a vertex ν and the uniform distribution u_A on A, then
ν ± ε(ν − u_A) ∈ P(F) for small ε > 0, so ν = u_A.  ⇐: P(F) ≠ ∅ has a vertex, whose support lies in F.)

**Theorem 4.1** KL ⇒ for m ≥ 4: C(2m,m,3) = 14 ⇔ 4 | m.
*Proof.* Let P(m) = "∃ w ≥ 0 integral, Σw = 2m, degrees m, 3-wise intersecting support".  By (R),
C(2m,m,3) = 14 ⇔ P(m).  If P(m), KL applied to w/(2m) gives an SQS-dual A ⊂ supp w; removing one copy of
each member of A lowers every degree by 4 (A is a 1-design with 4 sets through each element) and keeps
the support inside the old one: P(m−4).  Iterating reaches P(r), r ∈ {0,1,2,3}.  For r ∈ {1,2,3},
Lemma 3.2 gives w_S ≤ r/4 < 1, impossible.  So r = 0.  Conversely §2. ∎

Vertices of P(F) have support ≤ 14 sets (the support vectors 1_S are linearly independent in R^14); the
finite reduction of KL to vertex supports is §5.1.

## 5. Certified computer proof of the Key Lemma

### 5.1 Finite reduction (paper)
Let μ be ½-balanced on a 3-wise intersecting F with no SQS-dual.  P(F) is a polytope; take a vertex ν.
Its support F' ⊆ F is 3-wise intersecting and SQS-free, the vectors 1_S (S ∈ F') are linearly
independent (vertex of {ν ≥ 0, Σν = 1, marginals ½}; the Σν-row is 1/7 × the sum of the marginal rows),
so s := |F'| ≤ 14, and s ≥ 9 by Lemma 3.3(b).  **Weight bound:** ν is the unique solution of an s×s
subsystem A ν = b with A a 0/1 matrix and b ∈ {½,1}^s, so by Cramer ν_S = N_S / (2 det A) with N_S ∈ Z,
hence ν_S ≥ 1/(2 H_s) where H_s ≤ (s+1)^{(s+1)/2}/2^s is Hadamard's bound for 0/1 matrices;
H_14 ≤ 40 390, so **every ν_S ≥ 1/80 780 > 10^{-5}**.

### 5.2 Normalisation (paper; all choices WLOG for F', relabelling [14])
Write w_i for the weights of the rows.
1. S := a set of maximum weight → row 0 = {0,…,6}; w_0 ≥ w_k.  w_i ≤ 1/8 (Lemma 3.2).
2. N(S) = {T : |S∩T| = 3} has mass ≥ ½+3w_0 > 0; T := a maximum-weight member → row 1 =
   {0,1,2,7,8,9,10}; valid: w_k ≤ w_1 whenever |S_0∩S_k| = 3.
3. For T ∈ N(S): μ(N(S)∩N(T)) ≥ (½+3μ_S−μ_T) + (½+3μ_T−μ_S) − (1−μ_S−μ_T) = 3(μ_S+μ_T) > 0, so
   triangles (pairwise |∩| = 3) through (S,T) exist; their triple intersection t ∈ {1,2}
   (t = 3 would give |U ∖ (S∪T)| = 4 > 3).
   - **Case A**: some triangle (S,T,U) has t = 1; U := a maximum-weight such set → row 2 =
     {0,3,4,7,8,11,12}; valid: w_k ≤ w_2 whenever rows 0,1,k form a t = 1 triangle.
   - **Case B**: none has t = 1; take any triangle → row 2 = {0,1,3,7,11,12,13}; clause: no row k
     forms a t = 1 triangle with rows 0,1.
   (Relabelling: with H = S∩T, S' = S∖T, T' = T∖S, O = rest, U meets H,S',T',O in (1,2,2,2) resp.
   (2,1,1,3) elements, forced by |U∩S| = |U∩T| = 3, |U| = 7.)
4. The remaining symmetry is Sym(block) for each atom of the Boolean algebra generated by rows 0–2;
   remaining rows lex-decreasing, columns lex-decreasing inside each atom (double-lex; valid for a
   row group × product-of-symmetric column groups acting on the free submatrix).
5. Implied counting constraints (valid for support rows): every column lies in ≥ 4 and misses ≥ 4 rows
   (column weight ½ both ways, w ≤ 1/8); every row has ≥ 5 rows k with |S_i∩S_k| = 3 (mass
   ≥ ½+3w_i > ½, each ≤ 1/8), row 0 has ≥ 6 (w_0 ≥ 1/s ≥ 1/14: mass ≥ 5/7); every |∩| = 3 pair has a
   common |∩| = 3 neighbour (item 3).
Two models: **(dup)** R = 14 rows, zero-weight duplicate rows allowed (pads any support of size ≤ 14;
all constraints above hold for duplicates of support rows; weights ≥ 0) — used for case B;
**(exact s)** exactly s pairwise distinct rows, all weights ≥ 10^{-5} (§5.1) — used for case A,
s = 9,…,14.

### 5.3 Theory (linear constraints on w, each guarded by Boolean literals) — paper
Literals: x_ij (row i contains column j), p_ik ⇔ |S_i∩S_k| ≥ 4, t_k ⇔ rows 0,1,k form a t = 1
triangle (defined in the CNF by full-equivalence counters).  Always: w ≥ 0, w ≤ 1/8, Σw = 1,
w_k ≤ w_0 (and w ≥ 10^{-5} in the exact model).  Guarded:
- U(j,P): Σ_{i∈P} w_i ≤ ½ if x_ij = 1 ∀i∈P;  D(j,Q): Σ_{i∈Q} w_i ≥ ½ if x_ij = 0 ∀i∉Q (column balance).
- partner(k): w_k ≤ w_1 if p_0k = 0;  third(k): w_k ≤ w_2 if t_k = 1 (case A) — §5.2.
- E1(i,K): Σ_{k∈K} w_k + 4w_i ≤ ½ if p_ik = 1 ∀k∈K;  E2(i,Q): 4Σ_{k∈Q} w_k + 4w_i ≥ ½ if p_ik = 0 ∀k∉Q.
  Proof: column balance gives Σ_k w_k|S_i∩S_k| = 7/2 (sum over j ∈ S_i), i.e.
  Σ_{k≠i} w_k(|S_i∩S_k| − 3) = ½ − 4w_i, and 1 ≤ |S_i∩S_k| − 3 ≤ 4 when p_ik = 1, = 0 otherwise.
A **theory lemma** is a clause ¬L such that these constraints under the literal set L are infeasible;
its certificate is a vector of exact rationals y > 0 on the used constraints with Σ y·a = 0, Σ y·b < 0.
Every lemma is valid for every genuine counterexample (whose weights satisfy all guarded constraints),
so base CNF ∧ lemmas UNSAT ⇒ no counterexample.

### 5.4 Pipeline and results
`klprop.py` (CaDiCaL 1.9.5 via PySAT IPASIR-UP + floating-point LP oracle `lpcore3.c`) searches and
records lemma literal sets; `klcertify.py` computes exact Farkas vectors (HiGHS + rational repair);
`klcheck.py` (independent code) regenerates the base CNF, re-derives every guarded constraint from its
label, checks the guard against L, verifies the Farkas identity in exact arithmetic and checks that the
CNF is exactly base + ¬L clauses; then standalone CaDiCaL re-solves base + lemmas with a DRAT proof,
checked by drat-trim (→ LRAT) and cake_lpr.  `verify_kl.sh` (= `verify_kl.py`) redoes all checks from
scratch against a **fixed manifest** of required cells (B: case t2, dup model, R = 14; A_s: case t1,
exact model, s = 9..14, with the exact option sets): each certificate is assigned to a cell by its
options (validated by regenerating the base CNF), a cell is covered by one monolithic certificate or by
cube certificates such that every assignment of the union of their cube literals satisfies some cube
(exhaustive check; allows refining a cube into sub-cubes); file names and
unvalidated metadata are never trusted (audit/astra_report.md).  `adv_controls.py` checks that the two
attacks from the audit (relabelled s = 9 certificate; lone contradictory cube) are rejected;
`neg_controls.py` checks tampered multipliers/literals/clauses/flags are rejected; `sem_test*.py`
compare the base CNF with independent Python predicates (0 mismatches).
**Case A, s = 14 (cube-and-conquer).**  The cell A_14 is split into the 32 cubes given by all sign
patterns of the literals p_{0,3},…,p_{0,7} (|S_0∩S_k| ≥ 4 for rows k = 3..7); the hardest cube 00000 was
refined further on p_{0,8}, p_{0,9} into 4 sub-cubes, giving 35 cube certificates (31 + 4) over 7 literals.
The cubes cover the models of the base CNF (every assignment satisfies some cube), so certificates for all 35
(each: base CNF + its cube unit clauses (5, or 7 for the 4 refined cubes) + its own lemma clauses, every lemma with its own exact Farkas
certificate, UNSAT by DRAT/LRAT) certify the cell; `verify_kl.py` checks that every assignment of
the cube literals lies in some cube (hard cubes may be refined further into sub-cubes).  Lemmas learned in one cube are valid theory lemmas for the base
formula (each certificate depends only on the lemma's own literal set, never on the cube), so newly started cubes are *seeded* with the
lemmas of up to three refuted cubes; seeded lemmas are recorded and certified again inside the
seeding cube's certificate.  Measured at s = 12: seeding −25 % CPU, −28 % new lemmas.  Tested and
rejected: cheaper lemma minimisation (dual support only: −58 % at s = 11 but ×3.5 at s = 12),
a 30-CPU-min per-cube budget (most cubes need 35–75 CPU-min), weight-sorted rows, the 59-way
4th-row split, extra triple (F) rows (see KL14_IDEAS.md).  Profile: 88 % of the time is the LP oracle.

<!--KL-->
| instance | model | search (klprop) | lemmas | CaDiCaL re-solve | DRAT bytes | drat-trim | cake_lpr | CNF SHA-256 (prefix) |
|---|---|---|---|---|---|---|---|---|
| v2B14 | case B, dup R=14 | 14 s | 2821 | 0.24 s | 2637951 | VERIFIED | s VERIFIED UNSAT | 9ab690084dbf9d92 |
| xA9 | case A, exact s=9 | 1 s | 108 | 0.05 s | 341984 | VERIFIED | s VERIFIED UNSAT | 5eaccfbad64892ac |
| xA10 | case A, exact s=10 | 5 s | 779 | 0.17 s | 1129077 | VERIFIED | s VERIFIED UNSAT | 3e31bf6dfb325ade |
| xA11 | case A, exact s=11 | 58 s | 6436 | 1.96 s | 8509289 | VERIFIED | s VERIFIED UNSAT | 11a1cd4a7921c834 |
| xA12 | case A, exact s=12 | 102 s | 8737 | 3.0 s | 13700174 | VERIFIED | s VERIFIED UNSAT | 8557fa113fb12b6f |
| xA13 | case A, exact s=13 | 1804 s | 96315 | 82.44 s | 221356345 | VERIFIED | s VERIFIED UNSAT | dbfc3dd5287a766d |
| xA14 (35 cubes) | case A, exact s=14 | cube-and-conquer | 923783 | per cube | per cube | VERIFIED (35/35) | s VERIFIED UNSAT (35/35) | per cube |
<!--/KL-->

## 6. Per-m certified lower bounds (direct dual encoding)

`gen_direct.py m --pair` (clause-for-clause the generator of the stored CNFs; re-checked by `verify_kl.py`) (rows = 2m points, columns = 14 blocks, row sums 7, column sums m, pairwise
|∩| ≥ 3 (Lemma 3.1, finite form), triple condition, rows 0/1 = a λ=3 pair, double lex on the rest);
`prove.py` = CaDiCaL + DRAT + drat-trim + cake_lpr.  Records: `runs/direct_proofs.jsonl`.
<!--DIRECT-->
| m | CNF | solve | DRAT bytes | drat-trim | cake_lpr | CNF SHA-256 (prefix) |
|---|---|---|---|---|---|---|
| 5 | proofs/direct_m5.cnf | 0.04 s | 236616 | VERIFIED | s VERIFIED UNSAT | 8f475044a7c06307 |
| 6 | proofs/direct_m6.cnf | 0.98 s | 4020147 | VERIFIED | s VERIFIED UNSAT | 1f6d5685649b5b3e |
| 7 | proofs/direct_m7.cnf | 5.02 s | 15324871 | VERIFIED | s VERIFIED UNSAT | 5b7ff11851303c17 |
| 9 | proofs/direct_m9.cnf | 715.3 s | 1186745468 | VERIFIED | s VERIFIED UNSAT | e77f3ea845f08a9f |
<!--/DIRECT-->

## 7. Upper bounds with 15 blocks (U15)

### 7.1 Construction
Any three planes of PG(3,2) (hyperplanes of F_2^4) meet in a point.  Give the 15 planes P integer
weights w_P ≥ 0 with Σ w_P = 2m and Σ_{P ∋ x} w_P ≤ m for every point x; replace plane P by w_P new
points and let block_x = union of the classes of the planes through x (padded to size m).  This is a
(2m,m,3) covering with 15 blocks.  (Dually: the covering-points are planes; this is exactly the finite
problem with b = 15 and marginals ≤ ½, which PG(3,2) satisfies with slack: 7/15 < ½.)
`pgblow.py 3 5 30`: weights exist for m = 6,7,8 and 10,…,30, not for m = 5, 9.  Weights for m1, m2 add
to weights for m1+m2, and {6,7,8,10,11} generate every m ≥ 6 except 9.  Explicit coverings
`coverings/C{2m}_{m}_3_b15.txt`, m = 6..30 (m ≠ 9), all verified.
**Theorem 7.1** C(2m,m,3) ≤ 15 for all m ≥ 6, m ≠ 9.

### 7.2 Consequence
With §4/§5: C(2m,m,3) = 15 for all m ≥ 6 with 4 ∤ m, m ≠ 9 (the lower bound 15 being certified
directly for m = 6, 7, 9, 10; for general m it follows from the Key Lemma, certified in §5.4; independent reviews: audit/astra_report.md,
audit/referee/REPORT.md, audit/kl_closure/).

### 7.3 m = 9
LJCR: C(18,9,3) ≤ 16 (lower 14).  Our lower bound: 15 (KL; and direct SAT, §6).  No PG(3,2)-weighting
exists for m = 9.  15 blocks ⇔ a multiset of 18 subsets of [15], 3-wise intersecting, every element in
≤ 9 of them (sizes ≥ 7, pairwise ∩ ≥ 3); direct SAT search (`gen_direct.py 9 --b 15 --rmin 7 --cmax`)
did not finish in ~15 min; a normalised version (`gen_b15.py`: a size-7 row and a |∩|=3 partner of size
s1 = 7..11 fixed; valid since Σ sizes ≤ 135 < 8·18 and Σ_q λ_pq ≤ 56 < 4·17) was run for 1 h per case
without result; later work in `../m9/`; open.

## 8. t = 4: C(2m,m,4) and 30 blocks

- Schönheim: L(2m,m,4) = 30 for m ≥ 8 (inner ceilings 3, 7, 15).  With 30 blocks every point has degree
  exactly 15 (link ≥ C(2m−1,m−1,3) ≥ 15): dual = multiset of 2m 15-subsets of [30], 4-wise intersecting,
  every element in m sets.
- Relaxation (same proofs): distinct members meet 3-wise in ≥ 3 and pairwise in ≥ 7 points, μ ≤ 1/16,
  equality structure = 16 sets pairwise meeting in 7 (Hadamard 3-(16,8,3) duals).
- Construction: AG(4,2) blow-up (30 affine hyperplanes; any 4 points lie in one) ⇒ C(2m,m,4) = 30 for
  8 | m (`agblow.py`, files `coverings/C*_4_b30.txt`, verified for m = 8,16,24).
- Reduction: "every ½-balanced 4-wise intersecting family of 15-subsets of [30] contains a 16-set
  AG(4,2)-type dual" ⇒ [C(2m,m,4) = 30 ⇔ 8 | m] (P(m) ⇒ P(m−8); P(r), 1 ≤ r ≤ 7, impossible by μ ≤ 1/16).
  Conjectured; the analogous computation (vertex supports ≤ 30 sets of 15-subsets of [30]) is far out of
  reach of §5's method.
- Upper bound 31: PG(4,2) hyperplane blow-up (any 4 hyperplanes of PG(4,2) meet), `pgblow.py 4 8 30`:
  weights exist exactly for m ∈ {8,12,14,15,16,20,22,23,24,26,…,32,34,…} (fail: 9,10,11,13,17,18,19,21,
  25,33), and for all m ≥ 34.  This reproduces exactly the LJCR entries with size 31 in this range
  (m = 12,14,15,20,22,23; files `coverings/C*_4_b31.txt`, verified), so no LJCR improvement from it.
  The general pattern: PG(t,2) blow-ups give C(2m,m,t) ≤ 2^{t+1} − 1 whenever the weight ILP is feasible.
- t = 2 contrast: C(2m,m,2) = 6 for all m ≥ 3 (LJCR; the analogous "key lemma" fails: e.g. m = 3 uses six
  triples of [6], none of AG(2,2) type), so the rigidity is a genuinely 3-wise phenomenon.

## 9. Literature
- J. Schönheim, On coverings, Pacific J. Math. 14 (1964).
- La Jolla Covering Repository (D. Gordon), Zenodo 19735294 (v1.2, 2026-04-24), `../lit/coverdata_v1.2.json`.
- P. Frankl, On Sperner families satisfying an additional condition, JCTA 20 (1976) 1–11 (r-wise EKR).
- Z. Füredi, Maximum degree and fractional matchings in uniform hypergraphs, Combinatorica 1 (1981).
- J. Frankston, J. Kahn, B. Narayanan, On regular 3-wise intersecting families, Proc. AMS 146 (2018);
  F. Chang, Quantitative bounds for regular 3-wise intersecting families, arXiv:2608.20242 (2026) —
  regular (= balanced, unweighted, non-uniform) 3-wise intersecting families; our object is the
  uniform, weighted analogue in the smallest non-trivial case.
- Hilton–Milner / Frankl–Tokushige type stability results concern sizes of non-trivial families and do not
  directly address balanced weightings; we found no prior treatment of C(2m,m,3) as a family.
- A. Sidorenko, What we know and what we do not know about Turán numbers, Graphs Combin. 11 (1995):
  C(2m,m,3) = T(2m, 2m−3, m) in Turán notation.
