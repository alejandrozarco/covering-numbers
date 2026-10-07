**All seven files are VALID.** Each establishes its stated upper bound \(C(v,k,t)\le b\).

I wrote and ran an independent Python checker using only the standard library, without importing or executing the repository’s checker or construction scripts. For every file it verified:

- Exactly \(b\) distinct blocks, each containing exactly \(k\) distinct integer labels.
- All labels belong to \(0,\ldots,v-1\), and every label occurs.
- **Every \(t\)-subset exhaustively:** intersecting its points’ block-membership bitsets always gave a nonempty intersection.

| File in `upper/candidates/` | Verdict | Blocks | \(t\)-subsets checked | Uncovered | Unpadded load range |
|---|---|---:|---:|---:|---:|
| `C54_19_4_b121.txt` | **VALID** | 121 | 316,251 | 0 | 9–19 |
| `C55_19_4_b121.txt` | **VALID** | 121 | 341,055 | 0 | 10–19 |
| `C65_23_4_b121.txt` | **VALID** | 121 | 677,040 | 0 | 14–23 |
| `C69_24_4_b121.txt` | **VALID** | 121 | 864,501 | 0 | 15–24 |
| `C64_14_3_b156.txt` | **VALID** | 156 | 41,664 | 0 | 4–14 |
| `C76_16_3_b156.txt` | **VALID** | 156 | 70,300 | 0 | 6–16 |
| `C95_20_3_b155.txt` | **VALID** | 155 | 138,415 | 0 | 15–20 |

**The construction argument is sound.**

- In \(\mathrm{PG}(4,3)\), four representative vectors span a vector subspace of dimension at most four in \(\mathbb F_3^5\). That subspace lies in a hyperplane.
- In \(\mathrm{PG}(3,5)\), three representative vectors span a subspace of dimension at most three in \(\mathbb F_5^4\), hence lie in a projective plane.
- In \(\mathrm{AG}(3,5)\), three points have affine span of dimension at most two, which is contained in an affine plane.

For the blow-up, replace each geometric point \(x\) by a disjoint fibre of \(w_x\) labels. Any \(t\) new labels project to **at most** \(t\) geometric points, even when several labels share a parent. A geometric block containing those parents lifts to a block containing all the selected labels. When its size is at most \(k\le v\), padding it to size \(k\) preserves coverage.

I independently regenerated the geometries by directly enumerating representatives with first nonzero coordinate \(1\). Their block counts were respectively **121, 156, 155**. I also exhaustively checked their base coverage: 8,495,410 quadruples, 620,620 triples, and 317,750 triples, respectively; none were uncovered.

For every candidate, the recorded weights were nonnegative integers summing to \(v\). Every lifted block had size at most \(k\), and independent reconstruction using the recorded weights and specified padding **matched every file row exactly**.

I found **no defect invalidating any stated upper bound**. These are precisely *padded weighted blow-ups*; padding is necessary for the smaller lifted blocks. This audit establishes validity, not novelty or optimality.

The successful checker used one thread, took 1.36 seconds, and peaked at approximately 20.8 MB RSS. No files were modified.

