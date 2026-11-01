#!/usr/bin/env python3
"""End-to-end control of the C(18,9,3) reduction (replaces control.py; audit finding 3, Astra 2026-11-01).

Test object: 15 blocks of size 9 with all degrees >= 7 and all pair degrees >= 3, some triples uncovered (sa_ext.c, any
link class planted). Run the proof's choices on it, written here independently of cases9.py: root = degree-7 point with
lex-largest pair-degree sequence (discard the object if a triple through it is uncovered, since then its link is no
covering); relabel the link to the catalogue; first link-degree-3 orbit containing a degree-7 point gives the case;
move that point to q; maximise the row-major vector over Stab(q) x S_8. The exact case formula with only the uncovered
triples' clauses removed, plus units for that assignment, must be SAT. A generator or case bug that loses structures
would show as UNSAT. Only over-constraining bugs can fake an UNSAT, so --mutants injects such bugs and reports which
ones the control catches; an uncaught mutant is a hole in the control.
usage: control_e2e.py OUT.json TMPDIR SA_EXT N_OBJECTS [--mutants]
"""
import hashlib, importlib.util, itertools, json, os, random, subprocess, sys, tempfile, time
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pynauty
CAD = os.environ.get("CADICAL", os.path.expanduser("~/sat/cadical/build/cadical"))
SRC = open(f"{HERE}/gen_ext9.py").read()
D = json.load(open(f"{HERE}/links_17_8.json")); CL = D["classes"]; CASES = json.load(open(f"{HERE}/cases.json"))
CASEIX = {}
for i, (c, q, nd) in enumerate(CASES): CASEIX.setdefault(c, []).append((i, q, nd))

def load(src, name):
    spec = importlib.util.spec_from_loader(name, loader=None); m = importlib.util.module_from_spec(spec)
    m.__dict__["__file__"] = f"{HERE}/gen_ext9.py"; exec(compile(src, name, "exec"), m.__dict__); return m

def graph(masks, b=7):
    n = len(masks); adj = {i: [] for i in range(n + b)}
    for q, m in enumerate(masks):
        for c in range(b):
            if m >> c & 1: adj[q].append(n + c)
    return pynauty.Graph(n + b, adjacency_dict=adj, vertex_coloring=[set(range(n)), set(range(n, n + b))])

CERT = {pynauty.certificate(graph(c["masks"])): i for i, c in enumerate(CL)}

def group(idx, cap=200000):
    """Aut of link class idx as permutations of the 17 link points (closure of the generators, no use of nauty orbits)."""
    gens = [tuple(g[:17]) for g in pynauty.autgrp(graph(CL[idx]["masks"]))[0]]
    e = tuple(range(17)); seen = {e}; todo = [e]
    while todo:
        x = todo.pop()
        for g in gens:
            y = tuple(g[x[i]] for i in range(17))
            if y not in seen:
                seen.add(y); todo.append(y)
                if len(seen) > cap: return None
    return seen

GROUPS = {}
def choices(blocks):
    """the proof's choices on a test object; returns (case index, new blocks as rows over 1..17, uncovered triples) or a reason"""
    lam = lambda a, b: sum(a in B and b in B for B in blocks)
    deg = [sum(p in B for B in blocks) for p in range(18)]
    dseq = lambda r: tuple(sorted((lam(r, s) for s in range(18) if s != r), reverse=True))
    unc = [set(T) for T in itertools.combinations(range(18), 3) if not any(set(T) <= B for B in blocks)]
    if min(deg) < 7 or sum(deg) != 135: return "premise"
    D7 = [p for p in range(18) if deg[p] == 7]
    root = max(D7, key=dseq)
    if any(root in T for T in unc): return "root on uncovered triple"
    oth = [p for p in range(18) if p != root]; ix = {p: i for i, p in enumerate(oth)}
    LB = [b for b in blocks if root in b]; NB = [b for b in blocks if root not in b]
    masks = [sum(1 << c for c, b in enumerate(LB) if p in b) for p in oth]
    g = graph(masks); idx = CERT.get(pynauty.certificate(g))
    assert idx is not None, "link is a covering but not in the catalogue"   # a catalogue gap would stop here
    h = graph(CL[idx]["masks"]); la, lb = pynauty.canon_label(g), pynauty.canon_label(h)
    to = dict(zip(la, lb))                                                 # object link point -> catalogue link point
    pi = {p: to[ix[p]] for p in oth}
    cat = {frozenset(b) for b in CL[idx]["blocks"]}
    assert {frozenset(pi[p] for p in b if p != root) for b in LB} == cat
    if idx not in GROUPS: GROUPS[idx] = group(idx)
    G = GROUPS[idx]
    if G is None: return "group too large"
    d = {pi[p]: deg[p] for p in oth}     # degree by catalogue link point
    ldeg = [bin(m).count("1") for m in CL[idx]["masks"]]
    orbit = lambda x: {g[x] for g in G}
    ol, seen = [], set()
    for x in range(17):
        if ldeg[x] == 3 and x not in seen:
            o = sorted(orbit(x)); seen |= set(o); ol.append([y + 1 for y in o])
    ol.sort(key=lambda o: (-len(o), o))     # the order of the proof: largest orbit first, ties by smallest point
    for k, o in enumerate(ol):
        hit = [y for y in o if d[y - 1] == 7]
        if hit: break
    else: return "no degree-7 partner"
    before = sorted(y for o2 in ol[:k] for y in o2)
    match = [c for c in CASEIX[idx] if c[1] == o[0] and c[2] == before]
    assert match, f"no case for class {idx} q {o[0]} before {before}"     # a missing case would stop here
    q0 = o[0] - 1; g = next(g for g in G if g[hit[0] - 1] == q0)
    stab = [s for s in G if s[q0] == q0]
    rows0 = [{g[pi[p]] + 1 for p in b} for b in NB]
    best = None
    for s in stab:
        rows = sorted(([1 if p in {s[x - 1] + 1 for x in b} else 0 for p in range(1, 18)] for b in rows0), reverse=True)
        v = [x for r in rows for x in r]
        if best is None or v > best: best = v; brows = rows; bs = s
    skip = {frozenset(bs[g[pi[p]]] + 1 for p in T) for T in unc}   # the same relabelling as the rows
    return match[0][0], brows, skip, idx, len(stab), tuple(sorted(CL[idx]["degseq"], reverse=True))[:5]

def solve(G, ci, rows, skip, tmp, stabber=None):
    cls, q, nond7 = CASES[ci]; cl = CL[cls]
    raw = (stabber or G.stab_gens)(cl["masks"], 17, 7, q - 1)
    gens = [{p + 1: r[p] + 1 for p in range(17)} for r in raw]
    c, y, _ = G.build(cl["blocks"], gens, q, True, True, False, nond7, skip=skip)
    for j in range(8):
        for i in range(17): c.add([y[j][i] if rows[j][i] else -y[j][i]])
    fn = f"{tmp}/c.cnf"; c.write(fn)
    r = subprocess.run([CAD, "-q", fn], capture_output=True, text=True); os.remove(fn)
    assert r.returncode in (10, 20), r.stderr
    return r.returncode == 10

MUT = [  # (name, old, new): each makes the formula stronger than the proof allows
 ("rows ordered ascending", "c.lex_geq(y[j], y[j + 1])", "c.lex_geq(y[j + 1], y[j])"),
 ("aut lex reversed", "c.lex_geq(vec, gvec)", "c.lex_geq(gvec, vec)"),
 ("degree >= 8", "need = R - sum(p in Bl for Bl in L)\n        if need > 0:", "need = R + 1 - sum(p in Bl for Bl in L)\n        if need > 0:"),
 ("block size 10", "c.exactly(y[j], K)", "c.exactly(y[j], K + 1)"),
 ("q degree 8", "c.exactly([y[j][q - 1] for j in range(M)], 4)", "c.exactly([y[j][q - 1] for j in range(M)], 5)"),
 ("X degree >= 9", "c.atleast([y[j][p - 1] for j in range(M)], need + 1)", "c.atleast([y[j][p - 1] for j in range(M)], need + 2)"),
 ("N >= 12", "c.atleast(flags, 8)", "c.atleast(flags, 12)"),
 ("pair degree >= 4", "need = 3 - lamL[a, b]", "need = 4 - lamL[a, b]"),
 ("O max too small", "l = ge[s][Mx + 1]", "l = ge[s][Mx]"),
 ("O count one less", "lim = ROOTMU[tuple(Dseq)] - const", "lim = ROOTMU[tuple(Dseq)] - const - 1"),
 ("O 6-with-5 on all types", "if tuple(Dseq[:3]) == (6, 4, 4):", "if True:"),
 ("O degree guard dropped", "d7 = -c._counter([y[j][r - 1] for j in range(M)], need + 1)[need + 1]  # new(r) <= need", "d7 = c.new(); c.add([d7])"),
 ("triple also needs a second block", "c.add([c.and_aux([y[j][p - 1] for p in T]) for j in range(M)])", "L_ = [c.and_aux([y[j][p - 1] for p in T]) for j in range(M)]; c.add(L_); c.add(L_[1:])"),
 ("link point labels off by one", "L = [frozenset(q + 1 for q in Bl) for Bl in link_blocks]", "L = [frozenset((q + 1) % 17 + 1 for q in Bl) for Bl in link_blocks]"),
]

def stab_full(masks, n, b, fixed):   # mutant: full Aut instead of the stabiliser of q
    return [list(x) for x in pynauty.autgrp(graph(masks))[0]]

def main():
    out, tmp, sa, N = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]); mutants = "--mutants" in sys.argv
    os.makedirs(tmp, exist_ok=True); rng = random.Random(1); G = load(SRC, "gen")
    types = {}
    for i, c in enumerate(CL): types.setdefault(tuple(c["degseq"][:5]), []).append(i)
    print({k: len(v) for k, v in types.items()}, flush=True)
    objs, stat, fails = [], Counter(), []
    tl = sorted(types); seed = 0; want = {t: N // len(tl) for t in tl}; have = Counter()
    while any(have[t] < want[t] for t in tl) and seed < 12 * N:
        seed += 1; t = tl[seed % len(tl)]; idx = rng.choice(types[t]); a = [str(x + 1) for b in CL[idx]["blocks"] for x in b]
        r = subprocess.run([sa, str(seed), "3000000", "1.0", "15"] + a, capture_output=True, text=True)
        if r.returncode: stat["sa no object"] += 1; continue
        v = list(map(int, r.stdout.split())); blocks = [set(v[1 + i * 9:10 + i * 9]) for i in range(15)]
        if len({frozenset(b) for b in blocks}) < 15: stat["repeated block"] += 1; continue
        res = choices(blocks)
        if isinstance(res, str): stat[res] += 1; continue
        ci, rows, skip, cls, ns, ty = res
        if have[ty] >= want[ty]: stat["type full"] += 1; continue
        have[ty] += 1; ok = solve(G, ci, rows, skip, tmp); stat["SAT" if ok else "UNSAT"] += 1
        objs.append((ci, rows, skip, cls, ns, ty))
        if not ok: fails.append({"case": ci, "class": cls, "seed": seed}); print("CONTROL FAILED", ci, cls, seed, flush=True)
        if len(objs) % 25 == 0: print(len(objs), dict(have), dict(stat), flush=True)
    rep = {"objects": len(objs), "stat": dict(stat), "failures": fails, "types": {str(k): v for k, v in have.items()},
           "cases": len({o[0] for o in objs}), "classes": len({o[3] for o in objs}), "with_exclusion": sum(bool(CASES[o[0]][2]) for o in objs),
           "stab_nontrivial": sum(o[4] > 1 for o in objs)}
    print(rep, flush=True)
    if mutants:
        res = {}
        order = sorted(objs, key=lambda o: (o[5], -o[4]))
        for name, a, b in MUT + [("full Aut instead of stabiliser", None, None)]:
            assert a is None or a in SRC, name
            M = load(SRC.replace(a, b), "mut") if a else G
            kill = 0; tried = 0
            for ci, rows, skip, cls, ns, ty in order:
                try: ok = solve(M, ci, rows, skip, tmp, stab_full if a is None else None)
                except (AssertionError, KeyError, ValueError): continue
                tried += 1; kill += (not ok)
                if kill >= 3: break
            res[name] = {"killed": kill, "tried": tried}; print(name, res[name], flush=True)
        # the case-selection step: wrong orbit order = wrong nond7
        wrong = 0
        for ci, rows, skip, cls, ns, ty in order:
            c, q, nd = CASES[ci]; alt = [x for x in CASEIX[c] if x[1] != q and x[2]]
            if alt: wrong += (not solve(G, alt[-1][0], rows, skip, tmp)); 
        res["wrong case for the object"] = {"killed": wrong, "tried": len(order)}; rep["mutants"] = res
    json.dump(rep, open(out, "w"), indent=1)
    sys.exit(1 if fails else 0)
main()
