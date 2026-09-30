# Independent audit: Key Lemma closure (case A, s = 14)

**Claim audited:** "KL case A s=14 is certified and the full KL certificate set is complete."
**Verdict: CONFIRMED** (within the stated trust base; see Scope). Audited tree: e43416f (family/ at 5fbc22b).
kl_certs/ is 82 files; sha256 of the concatenated per-file sha256 list is 3224fd0d…c33.

## 1. Full from-scratch run (`verify_kl.log`, `DONE`)
`nice -n 10 family/verify_kl.sh --full`, run once, detached (PID 4120, about 61 min wall), gave **EXIT=0,
`VERIFY_KL: PASS`, 139 PASS / 0 FAIL**. That covers: the cnflib self-test; klcheck on all 41 certificates
(B14, xA9..xA13, and 35 A14 cubes); 45 CaDiCaL DRAT → drat-trim → LRAT → cake_lpr UNSAT checks (41
certificates plus direct m = 5, 6, 7, 9, each regenerated clause-for-clause); and all 7 manifest cells.
This agrees with the author's runs/verify_kl_full.log (139 PASS).

## 2. Independent coverage and base-CNF check (`indep_check.py`, `indep_check.log`: PASS)
My own script. It does not use verify_kl.py or klcheck.py and reads only the certificate JSON and CNF files.
- **Cell assignment:** each certificate's 11 option fields are matched against the fixed manifest.
  Result: B → B14, A9..A13 → xA9..xA13 (monolithic), A14 → exactly the 35 cube certificates. No leftovers.
- **Coverage:** the union K of all cube keys is p_{0,3}, …, p_{0,9} (7 literals). A brute-force pass over
  all 2^7 assignments finds **0 uncovered**. No cube repeats or contradicts a literal. The cube volumes sum to
  128 = 2^7, so the cubes form an exact **partition**: the 31 five-literal cubes, plus c00000 refined into
  4 seven-literal sub-cubes over p_{0,8} and p_{0,9}.
- **Base problem:** there is no base-CNF hash in any manifest. Instead I built the A14 base once with the
  family generator `basecnf.build(14,'t1', exact/distinct, third, nbr, colcard, rowlex, not1pair=False,
  useF=False)`, using **no cube literals**. It has 56057 clauses, sha256(repr) 28e22f13…. For each of the 35
  CNFs I checked that the first `nbase` clauses equal this list clause for clause and in the same order
  (same hash), that the next |cube| clauses are exactly the cube units (mapped through the generator's
  variable map), and that the rest are exactly one clause ¬L per recorded lemma literal set, **with nothing
  else**. All 35 pass. So each cube is (unrestricted A14 base) + (its cube units) + (theory lemmas). The
  Farkas validity of those lemmas is checked by klcheck in run 1 (35/35 PASS), not by this script.

## 3. Fresh negative controls (`controls.py`, `controls.log`: all as expected)
These run on copies in tmp/ (deleted afterwards) with `verify_kl.py --no-proof --dir=<copy>`. The baseline is
all 41 real certificates with their lemma lists emptied and their CNFs cut down to base + cube units. It
exercises the real option sets and cube lists, and it **PASSes**. Each control changes one thing:

| control | result | failing check |
|---|---|---|
| (i) drop cube A14_c10110 | FAIL | cell A14 cover (34 cubes) |
| (ii-a) xA9 file renamed to A14_c11111 | FAIL | cell A14 cover (xA9 still assigned to A9) |
| (ii-b) same, with metadata edited to R=14, A14 options, cube 11111 | FAIL | klcheck (base CNF mismatch, line 75) + cover |
| (iii) real A14_c11111 with one Farkas multiplier y → y+1/7 | FAIL | klcheck (Farkas identity, line 71); unmodified: PASS |
| (iv-a) extra cube with p_{0,3}=1 ∧ p_{0,3}=0 added to the full set | FAIL | "a cube repeats a literal" |
| (iv-b) the same cube replacing A14_c11111 | FAIL | "a cube repeats a literal" |
| (iv-c) A14_c11111 replaced by cube 11111 ∧ x_{0,0}=0 (contradicts the fixed row 0) | FAIL | cover (8 literals, gap) |

## Scope and minor gaps (none affects the verdict)
1. **Trust base, not re-audited here:** that the base CNF (basecnf.py, cases.py) and the guarded linear
   constraints in klcheck.py correctly encode the Key Lemma (FAMILY.md §5.1–5.3, including the w ≥ 10^-5
   bound and the symmetry breaking), and the tools (CaDiCaL, drat-trim, cake_lpr). My base check reuses the
   family generator, so it shows "the cubes are the unrestricted A14 instance *as the generator defines it*".
2. **`--no-proof` PASS is not a certificate.** The lemma-free stub baseline above passes with satisfiable
   CNFs. Only the default or `--full` mode, as in run 1, certifies anything.
3. FAMILY.md §7.2 (line 226) still says the KL certificate is "complete except for case A, s = 14". This is stale.
4. The verify_kl.py docstring says cube patterns must be realised "exactly once", but the code checks only
   cover, so overlap is allowed. That is sound. The code also rejects a complete set with an added
   self-contradictory cube (iv-a), which is conservative.
