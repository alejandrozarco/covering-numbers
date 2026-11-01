> AI review, not peer review. Verbatim except that local paths and a host name were replaced. Later status of the findings: `m9/README.md`.

**GAP — high confidence in the verification gap.** The mathematical reduction and the combined symmetry breaks appear sound. I found a reproducible false-acceptance path in the CnC verifier, and I could not independently establish the completeness of the 312-class enumeration or replay the deleted proofs. I have **not** refuted \(C(18,9,3)=16\).

The recorded CnC summaries do **not** show the verifier bug being triggered. That distinction matters: this is a defective verification procedure and an incomplete independent certification, rather than a demonstrated incorrect covering-number result.

Findings, ranked by severity:

1. **High: a failed leaf verification is skipped on restart.**  
   [m9/cnc/verify_cnc.py:99](m9/cnc/verify_cnc.py:99) adds every logged ID to `already`, including rows with `"verified": false`. Line 102 then removes those leaves from checking. The final success condition counts only failures in the current invocation.

   A concrete counterexample is:
   - Base formula \(F=(x)\), which is satisfiable.
   - Cubes \(x\) and \(\neg x\), whose union covers all assignments.
   - The \(x\)-leaf has a failed proof check; the \(\neg x\)-leaf has a successful check.
   - On restart, the failed leaf is skipped. The cover check correctly proves \(\neg x\land x\) UNSAT, and the verifier exits successfully with zero leaf checks.

   I reproduced that control flow by executing the unchanged verifier source against an in-memory filesystem, with mocked checker responses for the independently truth-checked cover formula. **No real proof checker was invoked in this regression test.**

   For the actual 22 summaries, the number of remaining proof files equals the number newly checked, so this particular skipped-failure symptom is absent.

2. **High: cached verification results are not bound to their formula or cube.**  
   [m9/cnc/verify_cnc.py:36](m9/cnc/verify_cnc.py:36), [m9/cnc/verify_cnc.py:45](m9/cnc/verify_cnc.py:45), and [m9/cnc/verify_cnc.py:122](m9/cnc/verify_cnc.py:122).

   Acceptance uses a leaf ID and a boolean, without checking a base-CNF hash, cube literals, or proof hash. Reusing a directory after changing the base or cube tree can therefore accept stale results. I reproduced that false-acceptance path in the same in-memory harness.

   The two resumed records rely on this cache:
   - **1175:** 2,241 of 2,514 leaves were previously verified.
   - **1376:** 1,965 of 2,306 leaves were previously verified.

   The local CnC records retain a **base-CNF hash**, but no leaf-proof, cover-proof, or cube-tree hashes. The corresponding completed trees and per-leaf logs were not available in this checkout. See [m9/cnc/cnc_hard.sh:21](m9/cnc/cnc_hard.sh:21). I found no evidence that stale results were actually reused.

3. **Medium: the controls provide much less coverage than “96/96” suggests.**  
   [m9/control.py:46](m9/control.py:46), [m9/control.py:60](m9/control.py:60), and [m9/control.py:65](m9/control.py:65).

   I ran the original control harness against an intentionally broken, in-memory generator implementing **only (X)**. It still returned:
   ```
   controls: 96, agree 96, SAT 48
   ```
   All size, ordinary degree, coverage, pair-degree, Q, N, O, and symmetry constraints had been omitted.

   Additionally, the control oracle omits the special “6 together with 5” prohibition for root type \((6,4,4)\). Automorphism constraints are never tested because `aut_gens=[]`.

4. **Verification limit: orbit–stabiliser agreement cannot exclude a completely missing class.**  
   [m9/classify_links.py:10](m9/classify_links.py:10).

   I independently confirmed all supplied classes, automorphism orders, orbit counts, and the total 267,906. My separate enumeration did not finish. Thus the assertion that these are **all** link classes remains dependent on the original enumeration execution.

The reduction passes the following hand check.

1. **Fifteen distinct blocks of size nine are WLOG.**  
   Starting from a covering with at most fifteen blocks of size at most nine, enlarge blocks to nine points, remove duplicates, and add unused nine-subsets until there are fifteen distinct blocks. Coverage persists. This argument does not require assuming a lower bound of fifteen.

2. **\(C(17,8,2)=7\).**  
   In a \((17,8,2)\) covering, each point belongs to at least
   \[
   \left\lceil\frac{16}{7}\right\rceil=3
   \]
   blocks. Consequently \(8b\ge51\), hence \(b\ge7\).

   Here is an explicit seven-block witness in dual notation. Each entry describes which blocks contain a point, followed by its multiplicity:
   \[
   123:3,\quad124:1,\quad145:2,\quad156:2,\quad
   256:1,\quad257:3,\quad3467:5.
   \]
   These are seventeen points; every block contains eight points; every two incidence sets intersect. Therefore every point pair is covered.

3. **Degrees and degree-seven points.**  
   The link of any point in the proposed covering is a \((17,8,2)\) covering, so \(d_p\ge7\). Since
   \[
   \sum_p d_p=15\cdot9=135,\qquad
   \sum_p(d_p-7)=9,
   \]
   at most nine points have degree at least eight. Therefore **at least nine** points have degree seven.

4. **Pair-degree excess and the partner \(q\).**  
   Every pair belongs to at least three blocks: its sixteen possible third points must be covered, and each block through the pair covers seven of them.

   For a degree-seven root \(p\),
   \[
   \sum_{q\ne p}\lambda_{pq}=7\cdot8=56,\qquad
   \sum_{q\ne p}(\lambda_{pq}-3)=5.
   \]
   Hence at most five partners have \(\lambda_{pq}>3\). There are at least eight other degree-seven points, leaving **at least three** degree-seven partners with \(\lambda_{pq}=3\).

5. **Link classes.**  
   Removing the root from its seven blocks produces seven distinct eight-subsets of the remaining seventeen points. They cover every pair. Isomorphism permits point relabelling and block permutation, with those two sorts kept separate.

   The dual representation is a multiset of seventeen nonempty subsets of seven block labels. Pair coverage means pairwise intersection; block size means each column sum is eight. The incidence-graph classification implements precisely this equivalence.

The simultaneous representative-choice argument is sound. The following order establishes existence of a surviving case:

1. Choose a degree-seven root whose descending seventeen-entry pair-degree sequence is lexicographically greatest among degree-seven points. This establishes **(O)**.
2. Relabel its link to a catalogue representative.
3. Order the link-degree-three point orbits exactly as `cases9.py` does.
4. Select the **first** orbit containing a degree-seven point. All earlier orbits then consist of points of degree at least eight, establishing **(X)**.
5. Map a degree-seven point in that orbit to its chosen representative \(q\), establishing **(Q)**. A link automorphism preserves every full-group orbit setwise, so the earlier-orbit exclusions survive.
6. Now maximise the row-major membership vector over
   \[
   \operatorname{Stab}_{\operatorname{Aut}L}(q)\times S_8.
   \]
   All previously imposed semantic conditions are invariant under this group. A maximum has descending lexicographic block rows and dominates every stabiliser-generator image. Thus **block ordering and the automorphism lex constraints hold simultaneously**.

This last step is the important compatibility argument: both lex constraints follow from one maximum over the remaining product action.

If the first eligible orbit had more than nine points in earlier orbits, those earlier points would supply more than nine degree-at-least-eight points, contradicting the degree sum. Consequently the dropped cases are impossible. **(N)** is already implied by that same degree sum.

I also checked all **7,601 generated stabiliser generators across all 1,380 cases**: each preserves the link, fixes \(q\), and preserves the excluded-orbit union.

The CNF families implement their stated conditions correctly, subject to catalogue completeness:

| Family | Audit result |
|---|---|
| Size, lines 39–40 | Exact cardinality nine for each new block. |
| Degree, lines 41–44 | Correctly adds the fixed link contribution to new-block membership. |
| Q, lines 45–47 | Link degree three plus exactly four new memberships gives degree seven. |
| X, lines 48–50 | Correctly imposes total degree at least eight. |
| N, lines 51–60 | Flags imply degree at most seven; the ordinary degree lower bound makes this exactly seven. Eight true flags are sufficient and attainable. |
| Triple coverage, lines 62–66 | Triples containing the root are covered by the link. Other triples already contained in a link block need no new clause. The remaining clauses require a genuine new-block witness. |
| Pair degrees, lines 73–78 | Exact conjunction definitions and exact counters correctly represent \(\lambda_{ab}\). |
| O, lines 79–134 | The degree-seven guard is exact in conjunction with (D). Thresholds include the pair with root zero correctly. |
| Row and automorphism lex constraints, lines 196–203 | Correct encodings, jointly justified by the representative argument above. |

References: [m9/gen_ext9.py:39](m9/gen_ext9.py:39), [scripts/cnflib.py:24](scripts/cnflib.py:24).

For all 25 comparisons between the five catalogue degree types, I checked that the implemented O predicate is equivalent to the intended lexicographic comparison. The claim that these five types are exhaustive remains part of the enumeration dependency.

The one-way triple witnesses and lex-prefix auxiliaries are sufficient: truthful conjunction values and truthful prefix-equality values provide satisfying auxiliary assignments whenever the intended condition holds. Pair counters need full equivalence because O uses upper bounds; they have it.

The CNF does not enforce distinctness of new blocks. That is a harmless relaxation for an UNSAT argument.

`root2` was unused in the recorded generator options. Its intended secondary root choice fits the same root-first argument; I inspected its encoding but did not execute dedicated tests for it.

For case completeness, I established the following:

- All **312 supplied representatives** have seven distinct eight-point blocks and cover every pair.
- All 312 are **pairwise nonisomorphic**, independently checked by explicitly applying all \(7!\) block permutations, without nauty.
- Every stored automorphism order and anchored orbit-image count agrees with that independent calculation.
- The counts by non-three degree entries are **224, 77, 6, 4, 1** for \((4^5),(5,4,4,4),(5,5,4),(6,4,4),(6,5)\).
- There are **1,935** link-degree-three point orbits: **1,380 retained**, **555 dropped**. Independently reconstructing the cases produced exactly `cases.json`, including its order, representatives, and exclusions.
- The anchored orbit counts sum to **267,906**.

“Labelled” needs qualification here: 267,906 counts point-unlabelled incidence multisets with labelled blocks, restricted to those containing the fixed three-subset. It is not the number of fully point-labelled coverings.

The orbit–stabiliser identity is correct. If \(A_b\) is the block-action automorphism group and \(t\) is the number of distinct three-subsets occurring as incidence types, the anchored count is
\[
\frac{7!}{|A_b|}\frac{t}{\binom73}.
\]
My explicit orbit-image counts confirmed this class by class.

The original enumerator’s pruning is also sound: sorted-mask ordering, total-incidence bounds, column capacity, remaining column capacity, and terminal column distinctness all preserve completeness. Fixing the initial mask to `7` is legitimate because minimum incidence is three and average incidence is \(56/17<4\). See [m9/enum_links.c:39](m9/enum_links.c:39).

My independent enumeration instead canonicalised partial incidence multisets at every depth. It reached 42,357 classes at depth six, then stopped at its conservative cap of 200,008 partial states at depth seven. **It did not independently reproduce the exhaustive 312 count.**

The records audit found:

| Item | Result |
|---|---:|
| JSONL records inspected | 1,596 |
| UNSAT records | 1,406 |
| UNKNOWN records | 190 |
| SAT records | **0** |
| Cases with at least one successful checker record | **1,380/1,380** |
| Conflicting CNF hashes for the same case | **0** |
| Recorded class/q/exclusion mismatches | **0** |

Successful records comprise **1,306 DRAT cases**, **54 direct-LRAT cases**, and **22 CnC cases**. Cases **5 and 700** have both single-proof and CnC success records. Thus there are 1,360 cases with successful single-proof records and **20 relying exclusively on CnC**; your 1,358-plus-22 partition is possible by assigning those two overlaps to CnC.

There are **19 earlier failed-check UNSAT records**, covering cases:

`1028, 1112, 1135, 1155, 1165, 1199, 1209, 1223, 1229, 1243, 1244, 1248, 1249, 1267, 1274, 1275, 1285`.

The five sample records for `115, 187, 173, 739, 346` have no proof checks. **Every one of these cases also has a successful checked record.** Counting UNSAT status alone would therefore be inadequate, but filtering on successful checks leaves no missing case.

I regenerated **100 CNFs in memory across 66 classes**, including all 22 CnC cases and all five degree types. **All 100 hashes matched**, including DIMACS comments. The differing checker pipelines do not themselves create a logical problem: each successful pipeline is intended to certify the same case formula’s unsatisfiability.

For CnC, the underlying composition is correct when every leaf result is valid and bound to the current inputs. If the cubes are \(C_i\), the leaf checks establish
\[
F\land C_i\text{ is UNSAT},
\]
and the cover check establishes
\[
\bigwedge_i\neg C_i\text{ is UNSAT}.
\]
Together these imply \(F\) is UNSAT.

The verifier constructs each leaf formula as **the original base clauses plus every accumulated cube literal as a unit clause**, with the clause count adjusted correctly. Its cover formula contains precisely the negated leaf cubes. This unconditional cover check is stronger than merely covering models of \(F\), and is sound. See [m9/cnc/verify_cnc.py:80](m9/cnc/verify_cnc.py:80) and [m9/cnc/verify_cnc.py:110](m9/cnc/verify_cnc.py:110).

I inspected the actual October 31 commit. The local proof change replaces whole-file decompression with binary streaming; the checker receives the same bytes. A 2.25 MB in-memory comparison confirmed identical output. Adding `--CML_HEAP_SIZE=12000` changes the allocation limit, not the verification condition. **Those changes are harmless to the verification logic.** The restart defects predate them.

Finally, the controls exercise four near-coverings, one selected root per file, all of root type \((6,4,4)\). Their ordinary degree, pair-degree, N, Q, and root conditions already pass. All 48 negative controls arise from X deliberately including a degree-seven point. They therefore fail to detect wholesale omission of the other constraints, do not test automorphism compatibility or case completeness, and omit one O condition from their oracle. They also print disagreements without returning failure.

I performed **31,239 independent small-assignment checks** of cardinalities, counter outputs, lex constraints including shared-variable permutations, triple witnesses, and pair-degree thresholds; all passed.

What remains unchecked is explicit: **exhaustive independent link enumeration; replay of the deleted single and CnC proofs; the completed CnC trees and per-leaf cache provenance; and the exact remote checker/source versions used historically.** I accepted the stated upper bound of sixteen without rechecking its witness. No files were modified, no full-case solver runs were performed, no processes were killed, and the compute server was not contacted.

