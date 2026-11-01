# $C(18,9,3)$: a computation that finds no covering with 15 blocks

Status: **AI-produced computational result, not peer reviewed, not checked by a human expert.** Added 2026-11-01.

The La Jolla Covering Repository lists $14 \le C(18,9,3) \le 16$, and `family/` gives $C(18,9,3) \ge 15$. The computation
here finds no $(18,9,3)$ covering with 15 blocks. Together with the 16-block covering in
`family/coverings/C18_9_3_b16.txt`, this indicates $C(18,9,3) = 16$.

**This evidence is weaker than for the other results in this repository, and we do not regard the question as settled by it.**

## Limits of the evidence

- **The proofs were not kept.** They total more than a terabyte, and were deleted after checking. A reader cannot check our
  proofs directly: the files in `runs/` record that the checkers ran and what they reported. Those records were
  written by AI-authored scripts.
- **No proof hashes for 20 cases.** The 1360 single-proof cases have a recorded SHA-256 for each proof. The 20 cases
  that rest only on cube-and-conquer record verdicts per sub-problem but no proof hashes.
- **Two cases are being re-run.** Part of the sub-problem checks for cases 1175 and 1376 came from runs that were
  interrupted and resumed, with a verifier later found to accept stale results (below). The logs show every sub-problem checked and
  none failed, but the link between log and proof is not as tight for those two. As of 2026-11-01 both are being re-run
  with the corrected verifier; this has not finished.
- **Only AI systems have reviewed this.** See Reviews.
- **The reduction is a written, unformalised argument**, and each CNF is trusted to encode what its generator says.

## Method

A written reduction (full text in `audit/fable_m9_report.md`, "The reduction as a proof"):

1. A 15-block covering may be assumed to have 15 distinct blocks of size 9. Then every point has degree at least 7, every pair
   lies in at least 3 blocks, and at least 9 points have degree exactly 7.
2. The blocks through a degree-7 point, with that point removed, form a $(17,8,2)$ covering with 7 distinct blocks. There are
   312 classes of these up to isomorphism (`links_17_8.json`).
3. A root point, its link, a partner point $q$ and a lex-leader for the remaining symmetry are chosen in that order.
   This leaves 1380 cases (`cases.json`), each one CNF (`gen_ext9.py`).

Each CNF is recorded as unsatisfiable.

| cases | method | checkers |
|---|---|---|
| 1360 | one proof from CaDiCaL | drat-trim or lrat-check, and cake_lpr |
| 20 | cube-and-conquer, about 51 400 sub-problems in total | lrat-trim, lrat-check and cake_lpr on every sub-problem; a checked proof that the sub-problems cover the case |

Cases 5 and 700 were done both ways. Solving took about 790 core-hours; the single proofs total about 1.3 TB. Most cases are small: 1248 of
them take 33 GB of proofs together, and 112 hard cases account for the rest. `runs/` also holds
timed-out runs and failed-check records; a case counts only through a record with passing checks, and every case has one.

## Checks made after the run

| check | result | limit |
|---|---|---|
| Regenerate all 1380 CNFs, compare with recorded hashes (`regen_hashes.py`) | 1380 of 1380 match (`audit/m9_regen_hashes.jsonl`) | shows the formulas, not their correctness |
| Second enumeration of the 312 classes with nauty's `genbg` | same 312 classes, matched by canonical form, same automorphism orders (`audit/links_17_8_genbg.json`) | both use nauty |
| Solve and check 40 random cases again from scratch | all unsatisfiable, all checks pass, all 40 proofs byte-identical to the recorded hashes (`audit/m9_replay.jsonl`) | 40 quick cases, DRAT, macOS arm64; hard cases and Linux builds not tested |
| Near-coverings run through the reduction's choices into their exact case formula (`control_e2e.py`) | 86 objects, 0 failures; 16 of 16 injected over-constraining errors detected (`audit/m9_control_e2e.json`) | uneven: 24 of 1380 cases, 3 objects with orbit exclusion, 2 of root type $4^5$, none with trivial stabiliser |
| Leaf logs of all 22 cube-and-conquer runs | 51 530 sub-problems, none failed, none missing | logs only |

`control.py` is the earlier control. It is kept because the reviews discuss it; review found that it detects very little.

## Reviews

AI reviews, not peer review. Each was run independently of the agents that did the work.

- gpt-6-astra (`audit/astra_m9_report.md`): verdict GAP. It reproved the reduction by hand and found no mathematical error,
  no error in any result, and no sign that the defects below had any effect. Its findings, and what happened to them:
  1. `verify_cnc.py` skipped failed leaves on restart: corrected; `cnc/test_verify_cnc.sh` is the regression test.
  2. Stored leaf results were not bound to their formula, cube and proof: corrected for new runs; see Limits.
  3. The controls were weak: `control_e2e.py` added; see its limits above.
  4. The 312-class enumeration had no independent confirmation: `genbg` added.
- Claude Fable 5.1 (`audit/fable_m9_report.md`), written before reading the first review, after findings 1, 2 and 4 had been addressed: verdict SOUND
  for the reduction, case split and formulas, with the 1380 verdicts resting on the records. It did not check any proof.

Agreement between AI reviews is limited evidence: they may share blind spots, and no human expert has checked this work.

## Reproduce

Tools as in the main README (CaDiCaL 3.0.1 c607304, drat-trim 2e3b2dc, cake_lpr a36874a), plus lrat-trim b30f400 and
march_cu (CnC 705b60c), in `~/sat` or `$SAT_TOOLS`. Some cases ran on macOS arm64, others, including the hardest, on Linux x86-64.

From this directory:

```sh
cc -O2 -o sa_ext sa_ext.c -lm
python3 regen_hashes.py hashes.jsonl /tmp/m9regen                     # 1380 CNFs, about 5 minutes
python3 control_e2e.py out.json /tmp/m9ctl ./sa_ext 150 --mutants     # 1 to 2 hours
python3 run9.py replay.jsonl 2,13,53 --proof --timeout 1200           # compare drat_sha256 with runs/*.jsonl
cnc/test_verify_cnc.sh                                                # verifier regression test
```

`cnc/cnc_hard.sh` and `cnc/resume_verify.sh` were written for one server, and their paths need editing.
