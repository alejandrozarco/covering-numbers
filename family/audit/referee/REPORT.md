# Referee report: the human reasoning chain behind C(2m,m,3) = 14 ⇔ 4 | m

Scope: FAMILY.md §1–§5.3, §6; paper.tex Part I; encoders `basecnf.py`, `cases.py`, `kl_lib.py`,
`klcheck.py`, `verify_kl.py`, `gen_direct.py` (read, not re-run). Certificates themselves are out of scope.
Nothing in `audit/astra_report.md` is repeated unless I disagree with it.

## Verdict: SOUND WITH MINOR GAPS

No fatal or serious mathematical defect. Every constraint the encoders add (base CNF and guarded
theory rows) is implied by the stated WLOG for a vertex ν of P(F), in both the dup model (case B) and
the exact-s model (case A); the direct m = 5, 6, 7, 9 encodings are a sound WLOG restriction of (R).
The defects below are all in the *exposition*: the paper's specification of the base CNF is incomplete,
and FAMILY.md carries stale status text. Ranked by severity.

## Defects

**D1 (serious, presentational). The paper's base-CNF specification omits two families of constraints
that the encoder adds.** paper.tex §5.3 lists "row size 7, pairwise intersections ≥ 3, 3-wise
intersection, no 8 rows pairwise meeting in 3, the normalisation". `basecnf.build` (called by
`klcheck.py` with `colcard=True`, `nbr=True` forced by the manifest) additionally adds
(i) every column in ≥ 4 rows and in ≤ R−4 rows, (ii) every row has ≥ 5 (row 0: ≥ 6) rows at |∩| = 3,
(iii) every |∩| = 3 pair has a common |∩| = 3 neighbour. These are valid (FAMILY §5.2 item 5 proves them
from Lemma 3.2 and w₀ ≥ 1/s), but (ii) for row 0 is the *only* place where the dup model uses the vertex
property s ≤ 14, and a reader of the paper cannot regenerate or validate the base CNF from the paper.
The paper's soundness sentence ("if the base CNF together with the theory lemmas is unsatisfiable, the
Key Lemma holds") is true only because these unlisted constraints are valid. Fix: list (i)–(iii) with
their one-line proofs in §5.3, and state that (ii) uses w₀ ≥ 1/s ≥ 1/14.

**D2 (minor). Validity of the dup model for duplicate rows is under-argued in the paper.**
paper.tex §5.2: "Case B is encoded with 14 rows, allowing zero-weight duplicates of support rows." Three
things make this sound and none is stated there: (a) duplicates must be copies of *support* rows (so
not1pair, nbr, colcard, no-SQS hold for them); (b) E1/E2 use coefficient 4 in `kl_lib.cond_rows` /
`klcheck.row` precisely because a duplicate pair has |S_i∩S_k| − 3 = 4 (in the exact model 3 would do);
(c) `w0>=`, `partner` hold for duplicates because their weight is 0 (a duplicate of S₁ placed at row
k ≥ 3 gets `partner(k)` with p₀ₖ = 0, fine only because w_k = 0). FAMILY §5.2 states (a) and §5.3 states
the bound 4; put (a)–(c) in the paper.

**D3 (minor). Double-lex justification and its interplay with weight comparisons is asserted, not
argued.** FAMILY §5.2 item 4 / paper item 4. The needed facts: the stabiliser of the ordered triple
(S₀,S₁,S₂) in Sym([14]) is exactly ∏ Sym(atom) (verified: the `blocks` in `cases.py` are the atoms for
t1, t2, pair); the row-major lex-maximal matrix in the orbit under Sym(rows ≥ 3) × ∏ Sym(atom) has rows
non-increasing and columns within atoms non-increasing (`lex_geq` reads column 0 / row f0 as most
significant, consistent with row-major order); and all guarded weight rows (`w0>=`, `partner`, `third`,
`E1/E2`, `U/D`) are invariant under that group because they compare only against rows 0–2, whose
weights ride along with the rows. Note the encoder correctly disables `rowlex` when `wsort` is on
(`klcheck.py` line 13), since weight-sorting and lex-sorting rows ≥ 3 are *not* jointly WLOG; the
manifest forbids `wsort`, so this is fine, but the paper should say rows ≥ 3 carry no mutual weight order.

**D4 (minor). Weight bound 10⁻⁵ (paper §5.1) skips the load-bearing step.** The paper says "By Cramer's
rule and Hadamard's bound … ν_S ≥ 1/80 780". Needed: choose s linearly independent marginal rows
(possible since the 1_S are independent, so no Σ = 1 row is needed and b = ½·1), A is 0/1 s×s,
det(A_S) = ½·det(0/1 matrix) so ν_S = N_S/(2 det A) with N_S ∈ ℤ, N_S ≥ 1, and H₁₄ ≤ 15^{7.5}/2^{14}
≈ 40 389. FAMILY §5.1 has it; copy it. Also say the bound is used only in the exact model (case A).

**D5 (minor). FAMILY §4 "Equivalently (Carathéodory): every vertex of P(F) is uniform on an
SQS(8)-dual."** Correct but unproved and misnamed: if supp ν ⊇ A then ν ± ε(ν − u_A) ∈ P(F), so a
vertex equals u_A. The following remark ("a balanced vertex without SQS-dual whose weights have
denominator not dividing 8") is loose: w/2m need not be a vertex; the vertex argument is in §5.1, not §4.

**D6 (minor). Lemma 3.1 wording.** FAMILY: "|H|/2 − 1 ≥ (μ_S+μ_T)(|H|−1) > 0 unless |H| ≥ 3"; paper:
"… > 0, i.e. |H| ≥ 3". For |H| = 1 the right side is 0, not > 0; the contradiction is −½ ≥ 0.
State: for |H| ≤ 2 the left side is ≤ 0 and the right side ≥ 0 with equality on the left only if |H| = 2,
where the right side is > 0.

**D7 (presentational). Stale text in FAMILY.md contradicts the certified state and the paper.**
§0 table `KL_STATUS` placeholder; §5.4 "split into the 32 cubes given by … p_{0,3},…,p_{0,7}" and table
row `xA14 … pending`; §7.2 "complete except for case A, s = 14"; §7.3 `B15_STATUS`. Actual store:
35 certificates = 31 five-literal cubes + 4 refinements of cube 00000 on p_{0,8}, p_{0,9}; paper says
"35 cubes over 7 intersection literals" (correct). Commit 5fbc22b says A₁₄ is certified.

**D8 (presentational). `verify_kl.py` docstring step 3 does not describe the code.** It says cube
families must "use the same k keys in the same order and realise each of the 2^k sign patterns exactly
once"; the code (lines 71–78) checks that every assignment of the *union* of the cube keys lies in some
cube, which is what the refined family needs and is sound (cover suffices; lemmas are cube-independent).
Update the docstring; FAMILY §5.4 already describes the code's behaviour.

**D9 (presentational). Definition/use mismatch for "SQS(8)-dual".** FAMILY §2 defines it as 8 sets
pairwise meeting in 3, any three in exactly 1; Theorem 4.1 uses "4 sets through each element". The
latter follows (Σ C(d_j,2) = 84, Σ d_j = 56 ⇒ all d_j = 4), and Lemma 3.3(a) proves it, but the
definition should include the 1-design property or Theorem 4.1 should cite 3.3(a) for it.

## Items checked and found correct (not previously recorded)

- (R): the degree count uses ⌈(2m−2)/(m−2)⌉ = 3 and ⌈3(2m−1)/(m−1)⌉ = 7, both exact for m = 4 and
  strict ceilings for m ≥ 5; multiset and repeated-block issues are handled; P(m) is read algebraically
  for m' < 4 in the iteration, so (R)'s range is never exceeded.
- Lemma 3.2 identity and the two derived mass bounds (N(S) ≥ ½+3μ_S; N(S)∩N(T) ≥ 3(μ_S+μ_T)) are exact;
  t ∈ {1,2} for triangles is forced by |[14]∖(S∪T)| = 3.
- Case split: `not1pair` (B) and `third`/fixed t1 row (A) are exactly complementary; `T3[k]` and the
  `p` literals are full equivalences, so both polarities of every guard literal are semantically sound.
- Exact model: `distinct` + non-strict `lex_geq` is consistent; `pos` rows are 1e-5 ≤ 1/(2H_s) for all
  s ≤ 14; `colcard`/`nbr` thresholds are the weakest valid ones (s = 14).
- Direct encodings (`--pair`): existence of a |∩| = 3 pair of *points* follows from N(S) having positive
  mass; blocks (0..2),(3..6),(7..10),(11..13) are the atoms of the two fixed rows; no distinctness is
  imposed, matching the multiset; `verify_kl.py` compares the stored CNF clause-for-clause with the
  default `--pair` invocation (default `--lam 3`, no `--cmax`), which uses the `atleast(…,3)` branch.
- `klcheck.py` hard-wires `not1=False`, `colcard=True`, `notrade=False`, `lamcnt=False`, so a certificate
  built with other flags fails the base-CNF comparison; the manifest flags are therefore exhaustive.
