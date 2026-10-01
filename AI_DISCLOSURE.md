# AI disclosure

AI models produced the content of this repository: the computations, the written argument in `family/FAMILY.md`,
the encoders, checkers and certificates, the coverings, figures and text. The repository owner chose the problem,
directed the work and decided on scope and publication. The owner did not check the mathematics or the code line by
line.

**Models**
- Claude Opus 5.5 (Anthropic, via Claude Code) did all the work, as several coordinated agents.
- Reviews and audits were run as separate instances:
  - independent reproductions of $C(17,8,3)$, $C(20,10,3)$ and $C(22,11,3)$ (own classifier, own CNF encoding, own
    proofs, code frozen before reading the original scripts), and an audit of the Key Lemma certificate set
    (`family/audit/kl_closure/`): separate Claude Opus 5.5 agents;
  - a referee report on the written argument and the encoders (`family/audit/referee/REPORT.md`): Claude Fable 5.1
    (Anthropic);
  - two reviews of the family argument and certificates (`family/audit/astra_report.md`, `astra2_report.md`):
    gpt-6-astra (OpenAI, via the Codex CLI).
- The commits carry a `Co-Authored-By: Claude Opus 5.5` trailer.

**Reviews.** The AI reviews found real errors, all fixed:
- the Key Lemma verifier trusted certificate metadata and filenames, so a certificate for the wrong case, or one whose
  cubes did not cover its case, could pass (shown with tampered certificates); the verifier now enforces case identity
  and cube coverage, and `family/audit/kl_closure/controls.py` keeps such negative controls;
- the stored direct certificates for $m = 5, 6, 7, 9$ were not reproduced verbatim by the generator; the verifier now
  regenerates every CNF clause for clause and compares hashes;
- the written specification of the base CNF omitted constraints that the encoder uses; they are now listed and
  justified in `FAMILY.md` §5.2;
- under-argued steps (duplicate-row model, double-lex symmetry breaking, the $10^{-5}$ weight bound), an inexact
  inequality in Lemma 3.1, a wrong cube count, a definition that did not match its use, and text that claimed more,
  or less, than was checked at the time.

AI reviews are not peer review, and no human expert has checked this work. In the terminology of the Lean community
these are *warrants*, not human-readable proofs (see the note at the top of `README.md`).

**What is checked by software**
- Every unsatisfiability claim has a DRAT proof checked by drat-trim and, after conversion to LRAT, by cake_lpr, a
  checker whose correctness is a machine-checked theorem (CakeML/HOL4).
- `scripts/check_covering.py` checks every stored covering (every $t$-subset in some block).
- `family/verify_kl.sh` re-checks the 41 Key Lemma certificates: the exact Farkas certificates for the
  linear-arithmetic lemmas in rational arithmetic, the case split and cube coverage, and the DRAT/LRAT refutations.

What remains to be trusted:
- the written, unformalised arguments: the counting that forces every link to be an optimal 2-covering, the link
  classifications (nauty), the symmetry breaking, and the reduction in `FAMILY.md` §1–§4 from the Key Lemma to the
  family statement;
- that each CNF encodes what its generator's documentation says it encodes;
- the toolchain: nauty/pynauty, CaDiCaL only through its proofs, and the compiled cake_lpr binary.
