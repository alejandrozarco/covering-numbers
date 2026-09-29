# Covering numbers C(17,8,3) and C(20,10,3): computation and certificates

Status: **computational results, not peer reviewed.** First published 2026-09-29.

C(v,k,t) is the minimum number of k-subsets (blocks) of a v-set such that every t-subset lies in some block.
The La Jolla Covering Repository (Zenodo record 19735294, v1.2, 2026-04-24) lists 17 ≤ C(17,8,3) ≤ 18 and
14 ≤ C(20,10,3) ≤ 15. The computations here find no covering with 17 resp. 14 blocks, which together with the
coverings in `coverings/` indicates C(17,8,3) = 18 and C(20,10,3) = 15.

For C(17,8,3) see also the title "The Covering Number C(17,8,3) = 18" (J. Hartley and M. A. Olson), listed without a
link on https://www.jonathanhartley.net/research as of 2026-09-29 (found after this computation was done; the two were
obtained independently).

## Method (outline)

For (v,k,b) = (17,8,17) resp. (20,10,14), counting forces every point into exactly r = 8 resp. 7 blocks, and the
blocks through a point (point removed) form an optimal 2-(v−1,k−1,1) covering with r blocks (C(16,7,2) = 8,
C(19,9,2) = 7). `scripts/counting.py` checks the arithmetic; `proofs/lb/` certifies C(16,7,2) ≥ 8.
These link coverings are classified up to isomorphism (`scripts/enum_links.c`, `scripts/classify_links.py`,
nauty via pynauty): 185 classes for (16,7,2; 8 blocks), 2132 classes for (19,9,2; 7 blocks) — `data/links_*.json`.
For each class, `scripts/gen_ext.py` writes a CNF for the remaining blocks with the link of a root point fixed.
Root choice: let M be the maximum pair degree λ(pq) of a hypothetical covering and μ(p) = #{q : λ(pq) = M}; take
as root a point maximising μ. Since λ(pq) is the degree of q in the link of p, the root's link L has maximum degree
M and μ(root) points of that degree, so every pair satisfies λ ≤ M_L and every point has at most μ_L partners at
degree M_L; these constraints are added. Symmetry breaking: lex-leader constraints for Aut(L) × S_{b−r} acting on
the incidence matrix of the new blocks (all other constraints are invariant, so each orbit keeps its lex-greatest
member); see the header of `gen_ext.py`. Every CNF is solved by CaDiCaL with a DRAT proof, which is checked by
drat-trim and, after conversion to LRAT, by cake_lpr.

## Contents

| path | content |
|---|---|
| `scripts/` | generator and driver (`run_case.py`), covering checker (`check_covering.py`) |
| `data/links_16_7.json`, `data/links_19_9.json` | link classifications (class representatives + automorphism generators) |
| `runs/*/results.jsonl` | one row per class: CNF sha256, solver status, proof sha256, checker verdicts |
| `proofs/C17_8_3_b17/`, `proofs/C20_10_3_b14/` | DRAT proofs (xz), one per class |
| `proofs/lb/`, `runs/lb_c16_7_2_*.log` | certificate for C(16,7,2) ≥ 8 |
| `coverings/C17_8_3_b18.txt` | an 18-block (17,8,3) covering |
| `coverings/C20_10_3_b15.txt` | the 15-block (20,10,3) covering listed in the La Jolla Covering Repository |
| `MANIFEST.sha256` | sha256 of every file |

## Reproduce

Requirements: Python 3 with `pynauty`; a C compiler; builds of CaDiCaL, drat-trim and cake_lpr in one directory
`$SAT_TOOLS` (`cadical/build/cadical`, `drat-trim/drat-trim`, `cake_lpr/cake_lpr`). Versions used:
CaDiCaL 3.0.1 (c607304), drat-trim 2e3b2dc, cake_lpr a36874a, pynauty 2.8.8.1, macOS arm64.

```sh
cc -O2 -o scripts/enum_links scripts/enum_links.c
python3 scripts/check_covering.py 17 8 3 coverings/C17_8_3_b18.txt
python3 scripts/check_covering.py 20 10 3 coverings/C20_10_3_b15.txt
# re-run a case from scratch (regenerates every CNF; compare cnf_sha256 with runs/*/results.jsonl):
mv runs/C17_8_3_b17 runs/C17_8_3_b17.published
SAT_TOOLS=/path/to/tools python3 scripts/run_case.py 17 8 17 8 --proof     # 185 classes, ~1 min
SAT_TOOLS=/path/to/tools python3 scripts/run_case.py 20 10 14 7 --proof    # 2132 classes, ~10 min
# to also redo the link classification, delete data/links_16_7.json / data/links_19_9.json first (~25 min each)
```

To check a stored proof directly: `xz -dk proofs/C17_8_3_b17/e0.drat.xz`, regenerate the CNF for class 0 with
`scripts/gen_ext.py` (see `run_case.py` for the exact arguments), then `drat-trim e0.cnf e0.drat`.
