# Key Lemma, case A, exact s = 14: ideas, proofs, measurements, recommended plan

Written 2026-09-30 (strategist agent), while `xA14` (klprop, single thread) and the pipeline owner's
2-literal cube split (`cA14_p{0,1}_x{0,1}`) were running.  Nothing here modifies the pipeline; small
prototypes live in `kl14_proto/` (all runs ≤ 2 threads, nice 10).  All claims that a recommendation
relies on are proved below; empirical statements are marked as such.

## 0. Summary and ranking

| rank | approach | status | expected gain for s = 14 | cost / risk |
|---|---|---|---|---|
| 1 | **Let `xA14` run** (baseline) | running (2h40m wall, 109 min CPU at 04:00) | none | extrapolated 3–9 h CPU search, ~0.5–1 M lemmas, DRAT ~2–3 GB, drat-trim ~1 h (§5) — feasible; single point of failure |
| 2 | **Unit-literal cube-and-conquer on p_{0,k}** (row 0's ≥4-partners), per-cube certificates (§4.1, Prop 7) | pipeline already supports multi-literal cubes; **measured at s = 12: 4 cubes on (p_{0,3},p_{0,4}) cost ×2.0 total CPU, heaviest cube = 84 % of the unsplit run** | wall-clock ≈ ÷1.2 per split level, CPU ×2 per level: an insurance policy (smaller DRATs, restartable), not a speed-up | no mathematical risk; needs idle cores (machine at load 180 on 10 cores during this study) |
| 3 | **Hybrid normalisation** "row 3 = heaviest free row, rows 4..13 lex" (§4.2, Prop 8) | proved valid, untested; needs 3 small edits (basecnf/kl_lib/lpcore) | unknown; strictly more theory information than lex at the price of one lex row | ~1 h of pipeline work; test on s = 11/12 first |
| 4 | `--wsort` (all free rows weight-sorted) | measured: s = 11: −30 % lemmas, +27 % CPU; s = 12: ≥ 8× CPU, aborted (§3.3) | negative | — |
| 5 | E-level literals (\|∩\| ≥ 5, ≥ 6) / E2 coefficient 3 | E2 appears in 0.5 % of s = 13 certificates ⇒ E2 tightening is worthless; E1 refinement only helps where \|∩\| ≥ 5 occurs | small | ~2 h of work |
| 6 | 4th-row shape split (59 `A<shape>` cases, `cases.py`) | valid (Prop 6) but measured total CPU ×3.7 at R = 10, ≥ ×1.8 at R = 11 | parallelism only | needs a `fourth` guarded row in kl_lib/klcheck/lpcore |
| 7 | p-first decision order (`kl14_proto/klprop_pfirst.py`) | measured: ≥ 1.7× slower at s = 11 (§3.3) | negative | — |
| — | pure linear-algebra proof of s = 14, nauty enumeration of 14×14 matrices, transferring s = 13 lemmas, uniform Farkas family | analysed and rejected (§2, §4.4–4.6) | — | — |

Bottom line: **there is no mathematical shortcut that removes the search at s = 14** (the weights are
determined by the matrix, Prop 1–2, but positivity of the determined weights is a genuinely
combinatorial condition that only the search decides), and **none of the search variants I could
measure beats the pipeline's current settings in total CPU** (cubes ×2, wsort +27 % at s = 11 and
≥ ×8 at s = 12, p-first ≥ ×1.7, 4th-row split ×3.7).  The recommendation is therefore to let `xA14` finish, keep the cube split as
insurance, and hold the hybrid normalisation (Prop 8) in reserve.  Everything below the line is a
proof, a measurement, or a reason not to do something.

## 1. What "exact s = 14" means algebraically

Notation: F' = {S_0,…,S_13} the vertex support (distinct 7-subsets of [14], 3-wise intersecting,
pairwise |∩| ≥ 3 by Lemma 3.1, SQS-free), A the 14×14 0/1 matrix with rows 1_{S_i}, ν > 0 the vertex
weights, J the all-ones matrix, 1 the all-ones vector, E = AAᵀ − 3J − 4I (so E_ii = 0 and
E_ik = |S_i∩S_k| − 3 ∈ {0,1,2,3} for i ≠ k), M = 4I + E.

**Prop 1 (weights are determined).** A is invertible, A⁻¹1 = (1/7)1, and ν = ½·A⁻ᵀ1.  Σν = 1 is
automatic; ν ≤ 1/8 is automatic (Lemma 3.2).
*Proof.* The rows are linearly independent (vertex, §5.1) and there are 14 of them in R¹⁴.
A1 = 7·1 (row sums) gives A⁻¹1 = (1/7)1.  Column balance is Aᵀν = ½1, whence ν = ½A⁻ᵀ1 and
Σν = 1ᵀν = ½·1ᵀA⁻ᵀ1 = ½·(A⁻¹1)ᵀ1 = ½·(14/7) = 1. ∎

**Prop 2 (Gram form; valid for every s).** For a vertex support of any size s, M = 4I + E (s×s) is
invertible and ν = ½·M⁻¹1.  At s = 14 the converse holds: the unique solution of Mν = ½1 satisfies
column balance.
*Proof.* G = AAᵀ = 3J + M is positive definite (rows independent).  Gν = A(Aᵀν) = ½A1 = (7/2)1, and
since Σν = 1, Jν = 1, so Mν = Gν − 3Jν = (7/2 − 3)1 = ½1.  Invertibility of M: if Mv = 0 then
Gv = 3(1ᵀv)1; if 1ᵀv = 0 then Gv = 0 ⇒ v = 0; otherwise v = c·G⁻¹1 = c'ν with c' ≠ 0, and then
(7/2)c' = 3(1ᵀv) = 3c'(1ᵀν) = 3c', a contradiction.  Converse at s = 14: A(Aᵀν − ½1) = Gν − (7/2)1 = 0
and A is invertible. ∎

Consequence: the "theory" of the search is, in truth, the single equation Σ_k E_ik ν_k = ½ − 4ν_i
(FAMILY.md §5.3), and the U/D column constraints are its column-wise disaggregation.  The pipeline's
E1/E2 rows are the sound relaxations of this equation under partial knowledge of E (only "E_ik ≥ 1"
is a literal).  The certificates at s = 13 confirm that this is where the proof lives (§3).

**Prop 3 (arithmetic of det A).** 7 | det A; (det A)² = 7·det(4I + E); every ν_i = N_i/(2 det A)
with N_i ∈ Z; |det A| ≤ H₁₄ = 40 390.
*Proof.* χ_A ∈ Z[x] is monic with integer root 7 (A1 = 7·1), so χ_A = (x−7)q with q ∈ Z[x] and
det A = ±7q(0).  Matrix-determinant lemma: det G = det(M + 3·11ᵀ) = det M·(1 + 3·1ᵀM⁻¹1) and
1ᵀM⁻¹1 = 2Σν = 2 by Prop 2, so (det A)² = det G = 7 det M.  Cramer for Aᵀν = ½1 gives the third
claim, Hadamard's bound for 0/1 matrices the fourth (this is FAMILY.md §5.1). ∎
Checked numerically on 177 random invertible 3-wise-intersecting 14-row matrices (script in §3.2).
Empirically |det A| ∈ [7, 672] over 2 698 random samples, far below 40 390, but I see no proof of a
better bound, and (§3.1) a better positivity bound would not shorten the proof anyway.

**Prop 4 (column sums; no further rigidity provable).** Every point lies in c_j ∈ [4, 10] rows and
Σ_j c_j = 98.  Nothing forces c_j = 7: the only constraint on column j is ν(C_j) = ½ where
C_j = {i : j ∈ S_i}, and with ν ≤ 1/8 that is exactly 4 ≤ c_j ≤ 10.
*Transposed view (for intuition, not used).* Because s = 14 = number of points, F' is self-dual in
shape: the 14 column sets C_j ⊆ [14] (rows) are distinct, have sizes 4..10, cover every triple of
rows (3-wise intersecting), cover every pair of rows at least 3 times (Lemma 3.1), every row lies in
exactly 7 of them, all have ν-measure exactly ½, and SQS-freeness says no 8 rows have all their pairs
covered exactly 3 times.  The complement matrix B = J − A is also invertible (det B = −det A, since
det(J−A) = det(−A)·(1 − 1ᵀA⁻¹1) = det A·(1 − 2)) with the same E and the same ν, but the complement
family need not be 3-wise intersecting (three members cover [14] iff they form a (3,3,3)-triangle
with triple intersection 2 or a (3,3,4) configuration with S∩T ⊆ U), so complementation is not a
usable symmetry.

**Prop 5 (Motzkin–Straus bound).** For any ½-balanced ν on an SQS-free 3-wise intersecting family,
Σ_i ν_i² ≤ 5/42.
*Proof.* Let Γ be the λ=3 graph (E_ik = 0).  Γ is K₈-free (Lemma 3.3a).  From Σ_k E_ik ν_k = ½ − 4ν_i
and E_ik ≥ 1 on non-edges, ν(N_Γ(i)) ≥ 1 − ν_i − (½ − 4ν_i) = ½ + 3ν_i.  Summing with weights ν_i:
½ + 3Σν_i² ≤ Σ_i ν_i ν(N_Γ(i)) = 2Σ_{ik∈Γ} ν_iν_k ≤ 1 − 1/ω(Γ) ≤ 6/7 (Motzkin–Straus). ∎
This is a valid *quadratic* cut; it reproves Lemma 3.3(b) (s = 8 forces Σν² ≥ 1/8 > 5/42) but for
s ≥ 9 it is compatible with everything else, and I found no linear consequence beyond ν ≤ 1/8.  Not
recommended for the pipeline; recorded because it is the only global (non-row-wise) inequality I
could prove.

## 2. Why there is no "linear-algebra shortcut" at s = 14

The temptation: since ν = ½A⁻ᵀ1, replace the LP by exact rational linear algebra.  This changes
nothing in the search: the LP relaxation with all 14 columns and all 91 p-literals assigned is
already exact (Prop 2), and leaves are a negligible part of the search.  What decides the problem
is the sign pattern of A⁻ᵀ1 over a space of ~10³⁰ matrices (star-like families {S ∋ j} pairwise
meeting in ≥ 3 already give C(≈1700,14)-many 3-wise intersecting 14-families), and no invariant
that I could find (determinant divisibility, column sums, Gram identity, Motzkin–Straus) separates
"ν > 0" from "some ν_i ≤ 0" without a search.  Random sampling (§3.2) illustrates how restrictive
positivity is: of 2 698 random invertible 3-wise intersecting 14-row matrices, **none** had ν > 0.

**Nauty enumeration** of 14×14 matrices (row sums 7, pairwise ≥ 3, 3-wise, SQS-free, invertible,
A⁻ᵀ1 > 0) as an independent certificate: not feasible.  The candidate space before the positivity
filter is astronomically large (see the star count above), and the only pruning available on partial
matrices is LP feasibility of the guarded system — i.e. exactly the CDCL(T) search without clause
learning.  Orderly generation would be strictly slower than what runs now.

## 3. What the s = 13 proof actually uses (and what that implies)

### 3.1 Certificate statistics (`ks/xA13.cert.json`, 96 315 lemmas)

| constraint type | in how many lemma certificates | note |
|---|---|---|
| E1 (Σ_{p_ik=1} w_k + 4w_i ≤ ½) | 82 764 (86 %) | the proof is a weight-packing argument over ≥4-neighbourhoods |
| U (column sum ≤ ½) | 81 162 (84 %) | |
| pos (w ≥ 10⁻⁵) | 76 400 (79 %) | i.e. most lemmas prove "some weight would be ≤ 0" |
| w_k ≤ w_0 | 75 509 (78 %) | |
| Σw ≥ 1 | 73 963 (77 %) | |
| D (column sum ≥ ½ over possible rows) | 43 945 (46 %) | |
| partner (w_k ≤ w_1) | 42 370 (44 %) | |
| third (w_k ≤ w_2) | 31 616 (33 %) | |
| **E2** (4Σ_{p_ik≠0} w_k + 4w_i ≥ ½) | **484 (0.5 %)** | tightening 4 → 3 (valid in the exact model since \|∩\| ≤ 6) is worthless |
| Σw ≤ 1 | 4 129 (4 %) | |

Lemma lengths are 10–35 literals (median ≈ 20): each lemma cuts a small box.  Literal types:
1.51 M x-literals, 0.34 M p-literals, 41 k t-literals.  Most frequent *free* literals:
p_{0,3}=1 (28 % of lemmas), p_{0,6}=1 (20 %), p_{0,4}=1 (20 %), p_{0,7}=1 (18 %), x_{11,7}=1 (21 %),
x_{12,8}=1 (20 %), x_{3,7}=1 (18 %).  Literal x_{3,13} — one of the two literals of the running cube
split — occurs in only 2 % of lemmas (as 0: 1 961, as 1: 141).

Implications.
* Raising the positivity bound (Prop 3 could at best give 1/(2·672) if the empirical determinant
  bound were provable) does **not** shorten the proof: a lemma that uses `pos` derives w_i ≤ 0 under
  L; it would be found with the same literal set for any ε > 0.  Do not spend effort on det bounds.
* E1 is the workhorse, and E1 fires on p-literals.  Cubing on p_{0,k} (which rows meet row 0 in ≥ 4)
  therefore cuts along the axis the proof uses.  With w_0 ≥ 1/14 and E1(0): Σ_{p_0k=1} w_k ≤ 3/14, so
  cubes with many p_{0,k} = 1 die almost immediately (each such w_k ≥ 10⁻⁵ is too weak, but the
  U/partner/third rows then finish the job in short lemmas — this is what the 28 % frequency says).
* Lemmas from s = 13 cannot be reused at s = 14: every certificate has a negative right-hand side,
  hence uses Σw ≥ 1, D, E2 or pos, and each of these changes meaning when a 14th row is added
  (Σ_{i<13} w_i ≥ 1 becomes false, D/E2 quantify over "all rows not known to miss").  Only lemmas
  certified by {nonneg, le1/8, Σw ≤ 1, w0≥, U, partner, third, E1} alone would transfer, and there
  are none (a certificate needs a negative b).

### 3.2 Prototype scripts (`kl14_proto/`)
* `run_wsort_test.sh R` — controlled lex vs `--wsort` comparison (same load, sequential).
* `klprop_pfirst.py` — klprop with a custom IPASIR-UP `decide()` that branches on p-literals first.
* `run_cube_profile.sh R` — the four (p_{0,3}, p_{0,4}) cubes at s = R with the pipeline's `--cube`.
* Logs: `wsort_test_11.log`, `wsort_test_12.log`, `pfirst_test_11.log`, `cube_profile_12.log`
  (CNF/raw.json outputs are git-ignored; they are reproducible and not certificates).
* The sampling / identity checks of §1 and §3.2 were run inline (seeds 7, 11, 3); they are
  reproducible from the descriptions here in a few lines each, and their outputs are quoted in §3.

### 3.3 Measurements (Apple M5, 10 cores, machine load 60–180 during the tests; CPU-user times)

| test | s | lemmas | CPU user | verdict |
|---|---|---|---|---|
| baseline (= xA settings) | 11 | 6 436 | 64.7 s | (FAMILY.md: 58 s unloaded) |
| `--wsort` | 11 | 4 477 | 82.3 s | fewer lemmas, more time: the weight chain w_3 ≥ … ≥ w_13 makes lemmas stronger but the solver loses row-lex propagation and pays for symmetric re-exploration |
| p-first decisions, polarity 0 | 11 | — | > 110 s, aborted (≥ 1.7× baseline) | negative |
| baseline | 12 | 8 737 | 95.0 s | reproduces xA12 exactly (FAMILY.md: 102 s unloaded) |
| `--wsort` | 12 | — | > 770 s, aborted (≥ 8.1× baseline) | the s = 11 trade-off (fewer lemmas, more time) turns into a blow-up one size up: weight ordering cannot replace row-lex |
| cubes (p_{0,3},p_{0,4}) ∈ {0,1}² | 12 | 3 621 / 4 584 / 4 433 / 8 225 | 34.8 / 38.5 / 40.4 / 79.8 s (sum 193.5 s) | CPU ×2.0; heaviest cube 84 % of unsplit (§4.1) |
| 4th-row shape split, old pipeline (`runs/Asub_10.log`, `runs/Asub_11.log`) | 10 / 11 | 59 cases, ~50 k lemmas / 35 of 59 cases, 735 s | 63 s vs 16.8 s unsplit (R = 10); ≥ 735 s vs 401 s unsplit (R = 11, split incomplete) | total CPU ×3.7 / ≥ ×1.8; only useful for parallelism |
| random 14-row 3-wise families, greedy | 14 | 4 472 families, 2 698 invertible, 0 with ν > 0 | 4 min | positivity is the whole problem |
| "uniform certificate" test: random *maximal* SQS-free 3-wise families (125–194 members) | — | 12 / 12 have a majority set X (\|X\| ∈ {1,3,5,7}, every member contains > \|X\|/2 of X) | 2.5 min | see §4.6 |

## 4. Evaluated approaches

### 4.1 Cube-and-conquer on unit literals (recommended)

**Prop 7 (cover).** For any fixed literals ℓ_1,…,ℓ_k, the 2^k instances base ∧ (ℓ_1^{ε_1} ∧ … ∧ ℓ_k^{ε_k}),
ε ∈ {0,1}^k, partition the models of base; each instance's certificate (klcheck + DRAT, with the cube
units recorded and checked as the pipeline owner's `--cube` extension does) is a certificate for its
cell, and all 2^k together certify base UNSAT. ∎  (Nothing WLOG is needed; the cubes are not
symmetry-based.)

Which literals.  From §3.1 the most active free variables are p_{0,3}, p_{0,4}, p_{0,6}, p_{0,7}, p_{0,5}
(and then p_{0,8}, x_{3,7}, x_{11,7}, x_{12,8}); x_{3,13} (one axis of the running split) occurs in 2 % of
lemmas, so both of its halves keep nearly the whole search.

**Measured profile at s = 12** (`kl14_proto/run_cube_profile.sh 12`, same settings as xA12, CPU-user
seconds; unsplit baseline 95.0 s / 8 737 lemmas measured under the same load):

| cube (p_{0,3}, p_{0,4}) | CPU | lemmas |
|---|---|---|
| (1,1) | 34.8 s | 3 621 |
| (1,0) | 38.5 s | 4 584 |
| (0,1) | 40.4 s | 4 433 |
| (0,0) | 79.8 s | 8 225 |
| **sum** | **193.5 s (×2.0)** | 20 863 (×2.4) |

My a-priori expectation that cubes with p_{0,k} = 1 die "in seconds" was wrong: E1(0) prunes only
after enough weight is pinned, and each cube re-learns most of the shared lemmas.  The split is
CPU-neutral per cube at best; the (0,0) cube (rows 3 and 4 both λ=3 to row 0, the lex-largest
configuration) carries 84 % of the unsplit cost.  Recursive re-cubing therefore gains ≈ 1.2× wall-
clock per level for ×2 CPU per level.  Conclusion: cube-and-conquer is worth doing only as insurance
(independent restartable pieces, DRATs of a few hundred MB instead of one of 2–3 GB) or when idle
cores are free; it is not a "much cheaper" method.  If used, cube on (p_{0,3}, p_{0,4}, p_{0,5}) (8 cubes)
rather than on x-literals, and expect the all-zero cube to dominate.

Certification cost is additive and unchanged (klcertify + klcheck + drat-trim per cube).

### 4.2 Hybrid normalisation: heaviest free row first, then lex (untested; proved valid)

**Prop 8.** In the exact model with fixed rows 0–2 (case A), the following normalisation is valid:
w_3 ≥ w_k for all k ≥ 4; rows 4..13 lex non-increasing; columns lex non-increasing inside each atom of
rows 0–2, read over rows 3..13 (row 3 first).
*Proof.* Let a counterexample be given with rows 0–2 fixed as in §5.2.  The group
H = Sym(rows 3..13) × Π_atoms Sym(atom) acts on it, preserving all hypotheses, and column permutations
preserve every weight.  Choose a representative with a heaviest row among rows 3..13 in position 3;
the stabiliser of that choice contains H' = Sym(rows 4..13) × Π Sym(atom) (column permutations keep
row 3 heaviest because weights do not change).  Among the H'-orbit take the matrix (rows 3..13,
free columns) that is lexicographically largest read row-major.  If rows i < i' (both ≥ 4) had
row_i <_lex row_{i'}, swapping them would increase the reading; if two columns j < j' in one atom had
col_j <_lex col_{j'} read top-down from row 3, swapping them would increase the reading at the first
row where they differ.  Hence the representative satisfies both lex conditions and w_3 ≥ w_k. ∎

What it buys: the LP gets the rows w_k − w_3 ≤ 0 (k ≥ 4), i.e. a fourth "max" anchor besides w_0, w_1,
w_2, without the guard that `third`/`partner` need; it costs only the lex relation between rows 3
and 4.  This is between lex (all Boolean symmetry breaking) and `--wsort` (all weight ordering).
Given the wsort measurement (fewer lemmas, more time) the hybrid is worth one test at s = 11/12
before use.  Pipeline changes: basecnf `rowlex` from row f0+1 instead of f0 (one line); kl_lib
`base_rows` a `('max3', k)` row with c[k] = 1, c[3] = −1, b = 0; lpcore3 the same row (no guard);
klcheck a `max3` label asserting `D['max3']`.  Everything remains certifiable exactly as now.

### 4.3 Theory refinements (low value)
* E2 coefficient 3 (valid: distinct rows ⇒ |∩| ≤ 6): E2 is used in 0.5 % of certificates — skip.
* Level literals q5_ik ⇔ |∩| ≥ 5, q6_ik ⇔ |∩| ≥ 6 (the counters in `basecnf.build` stop at 4; extend
  to 6) and E1 with coefficient 1 + [q5] + [q6]: sound, cheap in CNF, but only bites where |∩| ≥ 5
  occurs in the explored region; expected gain small.  If tried, add the labels to klcheck first.
* useF (triple literals): available, not used by the xA runs; presumably already found unhelpful.

### 4.4 4th-row shape split (`cases.py A<shape>`, 59 shapes)

**Prop 6 (validity, restated with proof).** In case A the three fixed rows contain column 0; the sets
avoiding column 0 have mass ½ (column balance), so a heaviest one V exists; V meets S∩T = {0,1,2},
S∩U = {0,3,4}, T∩U = {0,7,8} (3-wise intersecting) in columns ≠ 0, has |V∩S|,|V∩T|,|V∩U| ≥ 3 and |V| = 7;
its count vector over the atoms {1,2},{3,4},{5,6},{7,8},{9,10},{11,12},{13} is one of the 59 in
`v_shapes()`, and within each atom V can be taken to occupy the first elements (atom symmetry).  The
guarded row w_k ≤ w_3 if x_{k0} = 0 (k ≥ 4) is then valid, and the refined atoms give the column-lex
blocks.  The 59 cases are exhaustive and disjoint. ∎
Measured cost (old pipeline, §3.3): total CPU ×3.7 at R = 10 — the extra fixed row does not pay for
the loss of the lex-largest-row symmetry breaking on row 3.  Use only if ≥ 8 free cores and the
p-literal cubes of §4.1 are not enough; it needs the `fourth` row in kl_lib/lpcore3/klcheck.

### 4.5 Search heuristics (measured negative)
* `--wsort`: §3.3.  * p-first decisions: §3.3, negative.
* (Not tested) `--every` < 8 (more frequent LP checks): a pure tuning knob; the s = 13 run did
  427 k checks for 96 k lemmas, so LP time is already ≈ 4 checks per lemma; unlikely to matter.

### 4.6 "One uniform Farkas family" and the majority-set phenomenon

For a fixed family F the non-existence of a ½-balanced distribution is certified by y ∈ R¹⁴ with
y(S) ≥ 0 for all S ∈ F and Σ_j y_j < 0 (Farkas).  The simplest such y are y = 1_X − t·1, which exist
iff some X has min_S |S∩X| > |X|/2 ("majority set"; then X can be taken odd, |X| ≤ 7).  Empirically
(§3.3) every random maximal SQS-free 3-wise intersecting family had one.  **Conjecture M**: every
SQS-free 3-wise intersecting family of 7-subsets of [14] with pairwise |∩| ≥ 3 has a majority set of
odd size ≤ 7.  Conjecture M ⇒ KL (balance forces Σ_S μ_S|S∩X| = |X|/2 exactly).  But it is *stronger*
than KL, and a computational proof would have to enumerate maximal families of the class (125–194
members each in the samples) rather than vertex supports of size ≤ 14 — a larger job than the one at
hand.  So: no uniform certificate for s = 14 supports, but Conjecture M is the natural structural
statement behind KL and would be the right thing to state in a paper (with the reduction as the proof
path, not the other way round).

## 5. Cost model for the baseline `xA14`

Growth per step s → s+1 from FAMILY.md: lemmas ×7, ×8, ×1.4, ×11 (geometric mean 5.5); search time
×5, ×12, ×1.8, ×18 (geometric mean 6.5).  Extrapolation for s = 14: 0.5–1 M lemmas, 3–9 h CPU search
on an idle core; at the current load (the process gets ≈ 30–65 % of a core) 6–30 h wall.  Then
klcertify ≈ 1 h (6 min for 96 k lemmas), klcheck ≈ 1 h, CaDiCaL re-solve ≈ 15–40 min (82 s at s = 13
with 96 k lemma clauses), DRAT 2–3 GB, drat-trim ≈ 30–90 min (140 s for 221 MB), cake_lpr minutes.
Feasible within a day; the risks are the machine load and a single very large DRAT.  The cube plan of
§4.1 addresses both.

## 6. Recommended plan

1. Keep `xA14` running: it is the simplest certificate and, by the measurements, the cheapest in
   total CPU.  Reserve disk for a 2–3 GB DRAT plus LRAT; run drat-trim with a generous `-t`.
2. Keep the 4-cube split as insurance only (it is CPU ×2, §4.1); do not add more cubes unless cores
   are idle.  If a cube is added, use p_{0,4}/p_{0,5} rather than x_{3,13}.  Record every cube in
   `runs/kl_v2.jsonl` and the cube list in FAMILY.md so that the cover (Prop 7) is visible to a
   referee; add the cube-completeness check (all 2^k sign patterns present) to `verify_kl.sh`.
3. If `xA14` has not finished after ~24 h of CPU: implement the hybrid normalisation (§4.2, Prop 8),
   test on s = 11/12 (< 5 min each unloaded), and restart s = 14 with it only if it wins there.
4. Do not pursue: determinant bounds / better `pos`, E2 tightening, wsort, p-first decisions, nauty
   enumeration, lemma transfer from s = 13, the 4th-row shape split (unless ≥ 8 idle cores).
5. For the write-up: state Prop 1–3 (the s = 14 case is "a 14×14 0/1 matrix whose inverse has a
   positive column-sum vector") — it makes the finite reduction easier to read and gives the referee
   a one-line independent check of any claimed counterexample.
