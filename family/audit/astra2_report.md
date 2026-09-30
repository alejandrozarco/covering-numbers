# Astra review 2 (gpt-6-astra, codex exec, read-only, xhigh), 2026-09-30
Prompt: astra2_prompt.md. Two minor FAMILY.md defects fixed in the commit that adds this file.

**Verdict: CORRECT. Confidence: high.** I found no substantive gap in the theorem, its reduction to KL, or the completed certificate coverage. This assessment includes fresh bounded checks, but not a rerun of the full verification.

Two defects remain, ranked by severity; both are minor:

1. **The earlier inequality error remains in the working document.** [FAMILY.md:61](family/FAMILY.md:61) incorrectly appends a strict-positive inequality: when \(|H|=1\), its right-hand side is zero. The contradiction still follows, and [paper.tex:159–162](paper/paper.tex:159) correctly handles the cases. Thus this previous finding was fixed in the publication proof, but not fully propagated.

2. **The refined cubes have seven unit clauses, not five.** [FAMILY.md:176](family/FAMILY.md:176) describes every cube formula as having five cube units. The correct count is **31 formulas with five units and four with seven**. The stored formulas, coverage checker, and paper are correct.

My mathematical findings are:

| Component | Assessment |
|---|---|
| Dual reformulation | Correct, including repeated dual sets, repeated block occurrences, and intersections with repetitions. |
| SQS(8) construction | Correct; independently checked the 14 affine planes and unique coverage of every triple. |
| PG(3,2) construction | Correct; all five explicit seed weightings and their padded coverings passed exhaustive triple checks. |
| Relaxation lemmas | Correct in the paper. The intersection bound, weight identity, and eight-set characterization follow as claimed. |
| KL → divisibility | Correct. Subtracting one copy of each SQS-dual member preserves nonnegative **integral** multiplicities and balance; a positive remainder below four contradicts \(w_S<1\). |
| Finite reduction | Correct: vertex supports satisfy \(9\le s\le14\), and the determinant bound safely implies the \(10^{-5}\) cutoff. |
| Normalization and encodings | Sound. I found no unjustified active constraint or missing case. |

For the explicit PG weights at \(m=6,7,8,10,11\), the independently computed **total weight / maximum point load** was respectively
\[
12/6,\quad14/7,\quad16/8,\quad20/10,\quad22/11.
\]
The additive construction covers precisely the claimed range. I also independently excluded the \(m=9\) weighting by enumerating all **817,190** possible deficit vectors of total nine. This excludes that construction, not arbitrary fifteen-block coverings.

The potentially dangerous encoding steps withstand scrutiny:

- Maximum-weight choices justify the `w0>=`, `partner`, and case-A `third` comparisons.
- The neighborhood-mass inequalities justify the five-neighbor requirement, six neighbors for row zero, and common-neighbor clauses.
- Column balance and \(w_i\le1/8\) justify the column cardinality bounds.
- Double-lex is sound under the remaining row permutations and atom-preserving column permutations; no conflicting weight order is imposed on the free rows.
- Case-B padding works because zero-weight rows duplicate actual support members. The coefficient **4** in the intersection inequalities correctly accommodates duplicates.
- The intersection and triangle guard literals have the required semantics. The one-directional auxiliary clauses used elsewhere suffice for their existential role.
- The manifest excludes the experimental restrictions that are not part of this argument.

**The certificate set now covers the whole KL.** I independently checked:

- All **41** instances against the required case options.
- Every stored CNF against its regenerated base, declared cube units, and recorded lemma clauses.
- The 35 A14 cubes: every one of the **128** assignments is covered **exactly once**.
- The reported total of **1,038,979** Farkas lemmas.
- **20,198 exact Farkas certificates** through the actual checker, covering `xA9`, `xA10`, `B14`, `A14_c11111`, and the refined cube `A14_c00000_11`.
- Fresh DRAT and LRAT refutations for `xA9`, `B14`, `A14_c11111`, and direct \(m=5,6\), accepted by `drat-trim` and `cake_lpr`.
- Exact regeneration of all four direct CNFs, including \(m=7,9\).

The remaining proof checks are supported by the recorded complete audit run—139 PASS, zero FAIL—not by a fresh full replay here. The previous missing-A14, manifest/coverage, and direct-generator reproducibility defects are fixed.

The publication’s scope is accurate. It preserves \(C(10,5,3)=17\), excludes \(m=9\) from the fifteen-block theorem, and concludes only
\[
15\le C(18,9,3)\le16.
\]
Against the checksum-matched [LJCR v1.2 release](https://zenodo.org/records/19735294), the twelve newly settled entries are exactly
\[
m=10,11,13,14,15,17,18,19,21,22,23,25.
\]
The cases \(m=6,7\) were already known; \(m=9\) receives an improved lower bound, not an exact value.

No files were modified, no processes were killed, and no long jobs were started.

