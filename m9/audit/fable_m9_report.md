> AI review, not peer review. Verbatim except that local paths and a host name were replaced. Later status of the findings: `m9/README.md`.

# Referee report: C(18,9,3) = 16 via the 1380-case extension

## Verdict

**SOUND**, with high confidence in the reduction, the case split, the formulas and the case→CNF mapping. The one thing I could not establish myself is the 1380 UNSAT verdicts, because the proofs were deleted: those rest on records of `cake_lpr`/`lrat-check` runs. I found nothing that contradicts those records and the control structure around them is adequate, but a reader must take "record says VERIFIED" as the trusted base. No gap in the mathematical argument; no over-constraint in the formulas found by 463 end-to-end control checks.

## Findings, ranked by severity

None at a level that threatens the result. In descending order:

1. **Low — proofs are unreplayable; the trusted base is the run records.** Single-proof cases: `m9/run9.py:76-100` deletes proofs after `lrat-check` + `cake_lpr` (or `drat-trim` + `cake_lpr`) both report VERIFIED; the record keeps the CNF hash and the checker output lines. CnC cases: `m9/cnc/cnc_hard.sh:25` deletes `close_run/proofs` after `verify_cnc.py --check-all`. Nothing on this Mac can re-check those proofs. Failure scenario: a record written by a process whose checker never actually ran would be indistinguishable from a genuine one. I consider this remote (the record format is produced only from checker stdout, and all 1360 single-proof records carry the literal `s VERIFIED UNSAT` line), but it is the honest statement of what is trusted.

2. **Low — pre-fix `verified_leaves` rows are accepted without hash binding.** `m9/cnc/verify_cnc.py:104` accepts a cached row when `'base_sha256' not in r`. Two CnC cases (1175: 2241 of 2514 leaves; 1376: 1965 of 2306) were closed using rows from an earlier verifier run (visible in the stored `verify_log` tails in `m9/runs/E_cnc.jsonl`). The cover check (`verify_cnc.py:66-95`) still certifies that the accepted leaves cover the space, so a false acceptance would require a stale row *and* a mismatched cube — nothing in the records suggests it, but it cannot be excluded from this checkout.

3. **Informational — positive control coverage of (O) is incomplete for two root types.** My end-to-end control exercised the positive branch of (O) (the lex-max root must not be rejected) for root types (6,4,4), (5,5,4), (5,4,4,4), and the negative branch for (4^5), (5,4,4,4), (6,4,4). Types (4^5) and (6,5) were not tested positively: the annealer never produced an object in which a 4^5 root is lex-maximal (any other D7 point of a larger type defeats it), and produced no (6,5) object with the planted root maximal. The code path is the same (`gen_ext9.py:103-134`, constants `Mx`, `ROOTMU`), and I verified by brute force over all seven excess-5 sequences that the encoded conditions are implied by `≤lex`, so an over-constraint there would have to be a pure encoding bug in a path shared with the tested types. Residual risk small.

4. **Informational — the 16-block upper bound is imported, not stored.** `family/coverings/` has no `C18_9_3_b16.txt`; the paper cites the LJCR. I built one with `m9/sa.c` (`sa 18 9 16 1 20000000 1.0`, under 2 s) and verified it with `scripts/check_covering.py` ("16 blocks (16 distinct)... uncovered 3-sets: 0, VALID COVERING"). The upper bound is therefore available by construction; I recommend storing such a witness in `family/coverings/` for the paper.

5. **Cosmetic.** `m9/gen_ext9.py:4` refers to "STATUS.md §2", which does not exist in the repo. `gen_ext9.py` never checks that the nauty stabiliser generators are automorphisms of L (it only checks they are permutations fixing q, lines 229-232); I checked all 7601 generators across the 1380 cases and all preserve L, so this is a robustness remark, not a defect.

## The reduction as a proof

**Claim.** No family of 15 subsets of size ≤ 9 of an 18-set covers all triples.

**Step 0 (normalisation, WLOG debt paid).** Suppose a covering with ≤ 15 blocks of size ≤ 9 exists. Enlarge every block to exactly 9 points (coverage is monotone), add arbitrary 9-sets to reach 15 blocks, and replace any duplicate by a 9-set not yet used (C(18,9) ≫ 15). So a covering D with 15 *distinct* 9-blocks exists; all further reasoning is about D.

**Step 1 (degrees).** For a point p, the blocks through p minus p form a family of 7-or-8-subsets of the remaining 17 points covering all pairs (a triple {p,a,b} must lie in a block through p). Each point of that 17-set lies in ≥ ⌈16/7⌉ = 3 of these blocks, so 8·d_p ≥ 51, i.e. d_p ≥ 7. This is C(17,8,2) ≥ 7 and only the inequality is used. Since Σ d_p = 135 = 18·7 + 9, at most 9 points have degree ≥ 8, hence at least 9 points have degree exactly 7 (call the set D7).

**Step 2 (pair degrees at a degree-7 point).** For p ∈ D7 and q ≠ p: the 16 other points must each share a block with {p,q}, each block through p,q covers 7 of them, so λ_pq ≥ 3. Σ_q λ_pq = 7·8 = 56, so Σ_q (λ_pq − 3) = 5: at most 5 partners have λ > 3, at least 12 have λ = 3, and since at most 9 points have degree ≥ 8, p has at least 3 partners q with d_q = 7 and λ_pq = 3. The link of p is a (17,8,2) covering with exactly 7 *distinct* 8-blocks (distinct because the design blocks are distinct and all contain p); its degree sequence is (λ_pq)_q, an excess-5 sequence.

**Step 3 (choice of root — pays the (O) debt).** Choose ρ ∈ D7 whose descending sequence degseq(ρ) = (λ_ρq)_q is lex-maximal among D7. Then every r ∈ D7 satisfies degseq(r) ≤lex degseq(ρ). The formula does not encode ≤lex directly but three consequences (`gen_ext9.py:23-30, 103-134`): max_s λ_rs ≤ D[0]; #{s : λ_rs = D[0]} ≤ (multiplicity of D[0] in D); and for D = (6,4,4) no r has both a 6 and a 5. Each is implied by ≤lex for *any* descending sequence (first entry; leading run; second entry ≤ 4 forbids a later 5) — I checked this by hand and by brute force over all seven excess-5 partitions, so soundness of (O) does not depend on the catalogue being complete. The "exactness on the five types" is only a strength statement. Note (O) is evaluated for every r ∈ P, with d7(r) ⟺ deg(r) = 7 (`gen_ext9.py:94`, combined with (D)), and λ_r0 = deg_L(r) handled as a constant (`line 100`).

**Step 4 (choice of link representative).** Relabel so ρ = 0 and the link of 0 is literally the catalogue representative L of its isomorphism class (as a set of 7 blocks on {1..17}). The catalogue `m9/links_17_8.json` must contain every isomorphism class of 7-block (17,8,2) coverings with distinct 8-blocks. Completeness: `enum_links 17 7 8 3 1` lists every block-labelled covering in which some point has incidence set {0,1,2} (always achievable by a block permutation, since some point has link degree exactly 3 by Step 2's counting; the key-minimal popcount-3 mask is 7 and the sequence is sorted by (popcount, value)); pruning (`enum_links.c:59-69`) is by exact counting arguments. Isomorphism = colour-preserving isomorphism of the incidence bipartite graph, which is correct because blocks are distinct sets. Result: 312 classes. (O) is invariant under this relabelling because it quantifies over all r and compares against the multiset degseq(0), which equals the link degree sequence `Dseq` of L (`gen_ext9.py:70`).

**Step 5 (choice of q and the orbit exclusion — pays the (Q)/(X) debt).** Let O_1, O_2, … be the Aut(L)-orbits on link-degree-3 points, in the fixed order of `cases9.py:24` (size descending, then smallest label). By Step 2 at least three link-degree-3 points have degree 7, so some orbit contains one; let O_k be the first and h ∈ O_k such a point. Take g ∈ Aut(L) with g(h) = min O_k and relabel points 1..17 by g (fixing 0). Then L is preserved as a set, q := min O_k has degree 7 (Q), and every point of O_1 ∪ … ∪ O_{k−1} has degree ≥ 8 (X) because these orbits are g-invariant sets with no degree-7 point. (O) is preserved (invariant under any relabelling fixing 0). If |O_1 ∪ … ∪ O_{k−1}| ≥ 10 this contradicts Step 1, which is exactly why `cases9.py:27` stops at `len(before) > 9` — dropped cases are impossible, not skipped. Hence the labelled design falls in one of the 1380 cases (class, q, nond7).

**Step 6 (lex-leader — pays the (R)/(A) debt).** Let H = Stab_{Aut(L)}(q) × S_8 act on the 8×17 matrix Y of new blocks (point permutation of columns, permutation of rows). Every constraint established so far — (S) block size, (D) degree ≥ 7, (T) uncovered triples, (P) λ ≥ 3, (Q), (X) (nond7 is a union of Aut(L)-orbits, hence Stab(q)-invariant), (N), (O) — is H-invariant, so the H-orbit of our Y consists of valid Y's. Choose the row-major-lex-max element of the orbit. It satisfies vec(Y) ≥lex vec(σY) for every σ ∈ H, in particular for adjacent row swaps (that is exactly (R), `gen_ext9.py:196-197`) and for the stabiliser generators (A, `lines 198-203`; the action `(gY)[j][p] = Y[j][g⁻¹p]` is a genuine group action, and using only generators is a relaxation, hence sound). (N): at least 8 of points 1..17 have degree 7 since |D7| ≥ 9 and 0 ∈ D7.

**Step 7 (conclusion).** The resulting labelled design is a model of the formula built by `gen_ext9.build` for its case, with the triple clauses, cardinality counters and lex encodings all exact (counters are full-equivalence sequential counters; `and_aux` is one-directional but used only positively; verified by `cnflib.selftest` and my extra permuted-lex test). Hence if all 1380 formulas are UNSAT, no covering D exists, so C(18,9,3) ≥ 16; with the verified 16-block covering, C(18,9,3) = 16.

**Why the choices are jointly sound.** Each step's constraint is invariant under the group used by all later steps: (O) under all relabellings fixing 0 (Steps 4–6), the link under Aut(L) and its stabiliser (Steps 5–6), (Q)/(X) under Stab(q) × S_8 (Step 6). No step's choice can destroy an earlier step's property, so one labelled object satisfies the conjunction.

## Attacks on the assumptions a code reader would skip

- **Definition of degree/link.** Design degree d_p = blocks through p; link degree deg_L(p) = λ_0p = popcount of the point's mask. `cases9.py:22` (popcount == 3), `gen_ext9.py:45-47` (deg_L(q)=3 → exactly 4 new blocks), `gen_ext9.py:68-71` (`degL`, `Dseq`), and `classify_links.py:78` (`degseq`) all agree; I checked `Dseq` equals the json `degseq` for all 312 classes.
- **Indexing.** Link points 0..16 ↔ design points 1..17 via `+1` consistently: `gen_ext9.py:34` (blocks), `:226-233` (generators `g[p]+1`, stabiliser of `q-1`), `cases9.py:23` (`q+1`), and columns `y[j][p-1]`. The `--nond7` values are design labels, consumed as design labels (`gen_ext9.py:48-50`). I regenerated `cases.json` with my own brute-force orbits in design labels and it is identical, which would have caught an off-by-one in either file.
- **Generators act on the formula's labels.** The stabiliser graph colouring `[{fixed}, others, blocks]` (`gen_ext9.py:215`) forces point→point, block→block; I verified all 7601 generators map the design-labelled block set L to itself and fix q.
- **Root's pair-degree sequence.** `cases9.py` does not compute it; `gen_ext9.py` computes it from L (`Dseq`) and keys `ROOTMU` by the full 17-tuple; every catalogue sequence is one of the five keys (else `KeyError` at generation).
- **Clauses assuming something not yet established.** The only such dependency is (O)'s "λ = Mx" being encoded as "λ ≥ Mx" (`gen_ext9.py:121-134`), which is valid only together with the "max ≤ Mx" clauses in the same formula — they are present (`lines 103-109`).
- **Constants in counters.** `_counter` outputs for the indices used are always variables (need+1 ≤ 5 ≤ 8 inputs), so no `-None`/`-False` literal can arise.

## Concrete failure attempts (item 3)

I ran the proof's own choices end to end on near-coverings and asked the exact case formula (all constraints on, only the uncovered triples' clauses removed, Y fixed by units to the canonical lex-max assignment) to be SAT. The pipeline (`e2e.py`/`e2e2.py`, the reviewer's own scripts, not kept) is independent of `control*.py`: brute-force canonical form over S_7 for class identification, explicit isomorphism, explicit group enumeration for orbits and the lex-max, and `gen_ext9.build` + `stab_gens` as the code under test.

- 8 one-triple-short objects (4 from `m9/near_1{2,3,4,6}.txt`, 4 fresh from `sa.c`): 240 + 120 checks, all agree (all land in class 310, type (6,4,4); every D7 root not on the triple gives SAT in case 1376; the wrong-orbit case 1377 gives UNSAT).
- 13 planted-link objects (4–6 uncovered triples) across all five types: 32 checks agree — 31 correct UNSATs where the tested root is not lex-maximal (negative (O) control for types 4^5, (5,4,4,4), (6,4,4)) and 1 positive.
- 6 planted objects with the planted root lex-maximal: 71 checks agree — 28 positives across classes 277, 284, 285, 288, 289, 296–298, 306, 308, 310 (types (5,4,4,4), (5,5,4), (6,4,4)), each with its wrong-orbit negative UNSAT.

No case in which the formula rejects a structure the proof says it must accept, and no object whose canonical case was missing from `cases.json` (the script asserts on that).

## Item 4: what else is imported

- C(17,8,2) ≥ 7: elementary (Step 1); nothing deeper is used.
- 16-block upper bound: LJCR citation in the paper; witness built and verified here (Finding 4).
- nauty: used for the certificate (classification), orbits (`cases9.py`) and stabiliser generators. All three are now independently confirmed without nauty (brute-force S_7 canonical form: 312 classes, per-class leaf counts identical to the json; brute-force orbits reproduce the 1380 cases; generator check above). genbg (a different algorithm) also yields exactly these 312 classes in under a second.
- Solvers: CaDiCaL, march_cu, drat-trim, lrat-trim are *not* trusted; `cake_lpr` (and `lrat-check` as a second opinion) is the trusted checker, and it checks against the same CNF file whose SHA-256 is recorded and regenerable.

## Item 5: proof-checking chain, what is trusted

- *Single proofs* (`run9.py:63-103`): CaDiCaL → DRAT → drat-trim → LRAT → cake_lpr, or CaDiCaL --lrat → lrat-check + cake_lpr. The CNF is hashed before solving and the same path is handed to the checkers. Trusted: cake_lpr binary, the script's parsing of `s VERIFIED UNSAT`, the record file. All 1306 drat-trim records and 54 cadical-lrat records that cover the 1360 single-proof cases contain that line.
- *Cube-and-conquer* (`cnc_hard.sh`, `cnc_sweep.py`, `verify_cnc.py`): each leaf (base + cube units) UNSAT with a checked proof, and the clause set {¬cube : leaf} UNSAT with a checked proof. That pair of facts implies base UNSAT without trusting march_cu or the tree bookkeeping. Trusted: cake_lpr, the verify script's walk/accept logic, the grep conditions in `cnc_hard.sh:16`, and (Finding 2) cached rows for two cases. All 22 records show `COVER VERIFIED` and `PROOFS: N VERIFIED, 0 FAILED` with N equal to the number of leaves with proof files.
- Records: every one of the 1380 cases has at least one verified-UNSAT record; no SAT record anywhere; no two records for the same case disagree on the CNF hash; `(class, q, nond7)` in every record equals `cases.json`; 7 regenerated CNFs (cases 0, 5, 333, 700, 1000, 1376, 1379) match their recorded hashes byte-for-byte.

## What I ran versus read, and what I did not check

Ran: `cnflib` self-test plus an exhaustive permuted-lex test; `enum_links` (267,906 leaves) and my own S_7 canonical classification (312 classes, leaf counts match); genbg enumeration (312, same classes); brute-force Aut orders, orbits and case list (identical to `cases.json`); automorphism check of all 7601 stabiliser generators; CNF hash regeneration for 7 cases; record aggregation across all `m9/runs/*.jsonl`; 463 end-to-end control solves; 16-block covering construction and check; brute-force check of the (O) implications.

Read only: `run9.py`, `cnc_hard.sh`, `cnc_sweep.py`, `verify_cnc.py` (the Mac has no lrat tools path I was allowed to exercise and no proofs exist).

Not checked: any actual proof (deleted); the pre-fix `verified_leaves` rows for cases 1175 and 1376; the positive (O) branch for root types 4^5 and (6,5); anything on the compute server.

## Relation to the previous review (read only after writing the above)

I agree with its hand check of the reduction and with findings 1–2 on `verify_cnc.py` as code defects (since fixed; my Finding 2 is the residual of its finding 2). I disagree with the resulting verdict today: its finding 4 (link completeness) is now closed three independent ways, its finding 3 (weak controls) is addressed by the end-to-end control above, and the verifier defects were restart-path issues that the stored logs show were not triggered. What remains is the unreplayability of deleted proofs, which is a statement about the trusted base rather than a gap in the argument. If the user wants to remove even that, the cheapest route is to re-run the 20 CnC-only cases and a sample of single-proof cases with proofs retained; nothing in the reduction needs to change.