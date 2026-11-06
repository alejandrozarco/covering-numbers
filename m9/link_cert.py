#!/usr/bin/env python3
"""SAT certificate that the 312 link classes in links_17_8.json are complete.

A link at a degree-7 point is a 17 x 7 0/1 matrix M (rows = the 17 other points, columns = the 7 blocks through the
root, root removed) with
  (a) column sums exactly 8,  (b) any two rows share a 1 (pairs covered),  (c) row sums >= 3 (lambda >= 3),
  (d) columns pairwise distinct (the 15 blocks are distinct).
Symmetry breaking: rows lex non-increasing, columns lex strictly decreasing (strict because of (d)). This is sound:
sorting the columns (decreasing) or the rows (decreasing) each make the row-major reading of M lexicographically
larger unless already sorted, so alternating sorts terminate in a double-lex matrix isomorphic to M.

Steps:
 1. F = (a)-(d) + double lex, with a hand-written sequential-counter cardinality encoding, primary var x(q,c)=7q+c+1.
 2. Enumerate all solutions of F (pysat, blocking clauses on the 119 primaries).
 3. Map every solution to a listed class representative by an explicit (point, block) permutation, found with
    pynauty and then checked by plain code (no trust in nauty needed for this direction).
 4. F + all blocking clauses is UNSAT: CaDiCaL LRAT proof, checked by lrat-check and cake_lpr.
 5. Cross-check: the solution count of a second CNF built with pysat's totalizer encodings must be equal.
Conclusion: every link is isomorphic to one of the listed representatives.
usage: link_cert.py [outdir]
"""
import sys, os, json, hashlib, subprocess, itertools, time
import pynauty
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

HERE = os.path.dirname(os.path.abspath(__file__))
SAT = os.environ.get("SAT_TOOLS", os.path.expanduser("~/sat"))
CADICAL = f"{SAT}/cadical/build/cadical"; LRATCHECK = f"{SAT}/drat-trim/lrat-check"; CAKE = f"{SAT}/cake_lpr/cake_lpr"
NICE = os.environ.get("M9_NICE", "nice -n 19 taskpolicy -b").split()
N, B, K, SMIN = 17, 7, 8, 3
X = lambda q, c: B * q + c + 1
NPRIM = N * B


class CNF:
    def __init__(self): self.top = NPRIM; self.cl = []
    def new(self): self.top += 1; return self.top
    def add(self, c): self.cl.append(list(c))


def seqcounter(f, lits, k, mode):
    """Sinz sequential counter. s[i][j] <-> at least j+1 of lits[0..i] true (both directions encoded).
    mode 'eq' : exactly k;  'ge' : at least k."""
    n = len(lits)
    s = [[f.new() for _ in range(k + 1)] for _ in range(n)]
    for i in range(n):
        for j in range(k + 1):
            # s[i][j] <- s[i-1][j]  ;  s[i][j] <- s[i-1][j-1] & x_i  (j=0: <- x_i)
            if i > 0: f.add([-s[i - 1][j], s[i][j]])
            if j == 0: f.add([-lits[i], s[i][j]])
            elif i > 0: f.add([-s[i - 1][j - 1], -lits[i], s[i][j]])
            # s[i][j] -> s[i-1][j] | (x_i & s[i-1][j-1])
            if i == 0:
                if j == 0: f.add([-s[i][j], lits[i]])
                else: f.add([-s[i][j]])
            else:
                f.add([-s[i][j], s[i - 1][j], lits[i]])
                if j > 0: f.add([-s[i][j], s[i - 1][j], s[i - 1][j - 1]])
    last = s[n - 1]
    if mode in ("eq", "ge"): f.add([last[k - 1]])
    if mode == "eq": f.add([-last[k]])


def lex_ge(f, A, Bv, strict):
    """A >=lex Bv (strict: >). e[i] = 'equal on prefix 0..i-1' (forced when it is)."""
    e = [None] + [f.new() for _ in range(len(A))]
    for i, (a, b) in enumerate(zip(A, Bv)):
        pre = [] if i == 0 else [-e[i]]
        f.add(pre + [a, -b])                       # prefix equal -> a >= b
        f.add(pre + [-a, -b, e[i + 1]])            # prefix equal & a = b -> e[i+1]
        f.add(pre + [a, b, e[i + 1]])
    if strict: f.add([-e[len(A)]])


def build(card):
    f = CNF()
    pool = None
    if card == "pysat":
        pool = IDPool(start_from=NPRIM + 1)
        f.new = lambda: pool.id()
    def cardinality(lits, k, mode):
        if card == "seq": seqcounter(f, lits, k, mode)
        else:
            enc = CardEnc.equals if mode == "eq" else CardEnc.atleast
            for c in enc(lits=lits, bound=k, vpool=pool, encoding=EncType.totalizer).clauses: f.add(c)
    for c in range(B): cardinality([X(q, c) for q in range(N)], K, "eq")            # (a)
    for q in range(N): cardinality([X(q, c) for c in range(B)], SMIN, "ge")         # (c)
    for q, r in itertools.combinations(range(N), 2):                                # (b)
        ys = []
        for c in range(B):
            y = f.new(); ys.append(y); f.add([-y, X(q, c)]); f.add([-y, X(r, c)])
        f.add(ys)
    for q in range(N - 1): lex_ge(f, [X(q, c) for c in range(B)], [X(q + 1, c) for c in range(B)], False)
    for c in range(B - 1): lex_ge(f, [X(q, c) for q in range(N)], [X(q, c + 1) for q in range(N)], True)   # (d)
    if card == "pysat": f.top = pool.top
    return f


def enumerate_all(f):
    sols = []
    with Solver(name="cadical153", bootstrap_with=f.cl) as s:
        while s.solve():
            m = s.get_model()
            sol = tuple(1 if m[v - 1] > 0 else 0 for v in range(1, NPRIM + 1))
            sols.append(sol)
            s.add_clause([-v if sol[v - 1] else v for v in range(1, NPRIM + 1)])
    return sols


def check_link(M):
    rows = [[M[B * q + c] for c in range(B)] for q in range(N)]
    assert all(sum(rows[q][c] for q in range(N)) == K for c in range(B))
    assert all(sum(r) >= SMIN for r in rows)
    assert all(any(a & b for a, b in zip(rows[q], rows[r])) for q, r in itertools.combinations(range(N), 2))
    assert len({tuple(rows[q][c] for q in range(N)) for c in range(B)}) == B


def graph(rows):
    adj = {i: [] for i in range(N + B)}
    for q, r in enumerate(rows):
        for c in range(B):
            if r[c]: adj[q].append(N + c)
    return pynauty.Graph(N + B, adjacency_dict=adj, vertex_coloring=[set(range(N)), set(range(N, N + B))])


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "audit", "m9_linkcert")
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    L = json.load(open(os.path.join(HERE, "links_17_8.json")))
    assert (L["n"], L["b"], L["k"], L["smin"]) == (N, B, K, SMIN)
    # gen_ext9.py builds the extension CNF from cl["blocks"]; the representative used here is the same object
    reps = [[[int(q in bl) for bl in cl["blocks"]] for q in range(N)] for cl in L["classes"]]
    for cl, R in zip(L["classes"], reps):   # the masks field (dual form) must describe the same matrix
        assert [sum(R[q][c] << c for c in range(B)) for q in range(N)] == cl["masks"]
    rep_cert = {}
    for i, R in enumerate(reps):
        check_link([R[q][c] for q in range(N) for c in range(B)])
        rep_cert.setdefault(pynauty.certificate(graph(R)), i)
    assert len(rep_cert) == len(reps), "listed representatives not pairwise non-isomorphic"
    f = build("seq")
    sols = enumerate_all(f)
    print(f"seq encoding: {len(f.cl)} clauses, {f.top} vars, {len(sols)} double-lex solutions ({time.time()-t0:.0f}s)", flush=True)
    hit = [0] * len(reps); isos = []
    for sol in sols:
        check_link(sol)
        S = [[sol[B * q + c] for c in range(B)] for q in range(N)]
        gS = graph(S); i = rep_cert.get(pynauty.certificate(gS))
        assert i is not None, f"solution not isomorphic to any listed class: {sol}"
        R = reps[i]
        lS = pynauty.canon_label(gS); lR = pynauty.canon_label(graph(R))
        # canon_label[j] = original vertex at canonical position j; so S-vertex lS[j] <-> R-vertex lR[j]
        phi = [None] * (N + B)
        for j in range(N + B): phi[lS[j]] = lR[j]
        # explicit check, no trust in nauty: points->points, blocks->blocks, incidences preserved
        assert sorted(phi[:N]) == list(range(N)) and sorted(phi[N:]) == list(range(N, N + B))
        assert all(S[q][c] == R[phi[q]][phi[N + c] - N] for q in range(N) for c in range(B))
        hit[i] += 1; isos.append({"sol": "".join(map(str, sol)), "class": i, "phi": phi})
    missing = [i for i, h in enumerate(hit) if h == 0]
    print(f"every solution mapped to a listed class by a checked isomorphism; classes hit: {len(reps)-len(missing)}/{len(reps)}", flush=True)
    # certificate CNF
    cnf = os.path.join(out, "linkcert.cnf"); prf = os.path.join(out, "linkcert.lrat")
    with open(cnf, "w") as fo:
        fo.write(f"c links_17_8 completeness: (a)-(d) + double lex + {len(sols)} blocking clauses\n")
        fo.write(f"p cnf {f.top} {len(f.cl) + len(sols)}\n")
        for c in f.cl: fo.write(" ".join(map(str, c)) + " 0\n")
        for sol in sols: fo.write(" ".join(str(-v if sol[v - 1] else v) for v in range(1, NPRIM + 1)) + " 0\n")
    r = subprocess.run(NICE + [CADICAL, "-q", "--lrat", "--binary=false", cnf, prf], capture_output=True, text=True)
    unsat = "s UNSATISFIABLE" in r.stdout
    lc = subprocess.run(NICE + [LRATCHECK, cnf, prf], capture_output=True, text=True) if unsat else None
    ck = subprocess.run(NICE + [CAKE, cnf, prf], capture_output=True, text=True) if unsat else None
    lc_ok = unsat and "c VERIFIED" in lc.stdout.splitlines()
    ck_ok = unsat and "s VERIFIED UNSAT" in ck.stdout
    print(f"F + blocking: {'UNSAT' if unsat else 'NOT UNSAT'}; lrat-check {'VERIFIED' if lc_ok else 'FAILED'}; cake_lpr {'VERIFIED' if ck_ok else 'FAILED'}", flush=True)
    f2 = build("pysat"); n2 = len(enumerate_all(f2))
    print(f"cross-check, pysat totalizer encoding: {n2} solutions ({'equal' if n2 == len(sols) else 'DIFFERENT'})", flush=True)
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    json.dump(isos, open(os.path.join(out, "isomorphisms.json"), "w"))
    rec = {"links_sha256": sha(os.path.join(HERE, "links_17_8.json")), "classes": len(reps), "solutions": len(sols),
           "classes_hit": len(reps) - len(missing), "missing_classes": missing, "cnf_sha256": sha(cnf),
           "lrat_sha256": sha(prf) if unsat else None, "lrat_bytes": os.path.getsize(prf) if unsat else None,
           "unsat": unsat, "lrat_check": lc_ok, "cake_lpr": ck_ok, "pysat_totalizer_solutions": n2,
           "isomorphisms_sha256": sha(os.path.join(out, "isomorphisms.json")),
           "complete": unsat and lc_ok and ck_ok and n2 == len(sols) and not missing, "seconds": round(time.time() - t0)}
    json.dump(rec, open(os.path.join(out, "record.json"), "w"), indent=1)
    print(json.dumps(rec))
    if unsat and lc_ok and ck_ok: os.remove(prf)   # hash recorded; regenerate with CaDiCaL from linkcert.cnf
    sys.exit(0 if rec["complete"] else 1)


if __name__ == "__main__":
    main()
