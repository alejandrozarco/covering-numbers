#!/usr/bin/env python3
"""Minimal CNF builder: variables, clauses, a sequential-counter cardinality
encoding (full equivalence, so it is exact in both directions), and a lex
constraint.  Self-test: `python3 cnflib.py` exhaustively checks the cardinality
and lex encodings on small sizes by enumerating all input assignments and
checking satisfiability of the residual formula with a tiny DPLL.
"""
from itertools import product


class CNF:
    def __init__(self):
        self.nv = 0
        self.clauses = []

    def new(self):
        self.nv += 1
        return self.nv

    def add(self, cl):
        self.clauses.append(list(cl))

    # ---- cardinality: counter s[i][j] <-> "at least j of xs[0..i-1] true" ----
    def _counter(self, xs, top):
        """returns list s where s[j] (j=0..top) is a literal meaning
        'at least j of xs are true' (s[0] = None means TRUE)."""
        n = len(xs)
        prev = [None] + [False] * top          # None = TRUE, False = FALSE constants
        for i in range(n):
            x = xs[i]
            cur = [None]
            for j in range(1, top + 1):
                a = prev[j]          # at least j among first i
                c = prev[j - 1]      # at least j-1 among first i
                # cur_j <-> a or (c and x)
                if a is None:
                    cur.append(None)
                    continue
                if a is False and c is False:
                    cur.append(False)
                    continue
                v = self.new()
                # a -> v
                if a is not False:
                    self.add([-a, v])
                # c & x -> v
                if c is not False:
                    self.add(([-c] if c is not None else []) + [-x, v])
                # v -> a or c
                cl = [-v]
                if a is not False:
                    cl.append(a)
                if c is None:
                    pass  # c true: v -> a or true, trivially satisfied; skip clause
                else:
                    if c is not False:
                        cl.append(c)
                    self.add(cl)
                # v -> a or x
                cl = [-v]
                if a is not False:
                    cl.append(a)
                cl.append(x)
                self.add(cl)
                cur.append(v)
            prev = cur
        return prev

    def _assert_true(self, lit):
        if lit is None:
            return
        if lit is False:
            self.add([])
            return
        self.add([lit])

    def _assert_false(self, lit):
        if lit is None:
            self.add([])
            return
        if lit is False:
            return
        self.add([-lit])

    def exactly(self, xs, k):
        n = len(xs)
        if k < 0 or k > n:
            self.add([])
            return
        s = self._counter(xs, min(k + 1, n))
        self._assert_true(s[k])
        if k + 1 <= n:
            self._assert_false(s[k + 1])

    def atleast(self, xs, k):
        if k <= 0:
            return
        if k > len(xs):
            self.add([])
            return
        s = self._counter(xs, k)
        self._assert_true(s[k])

    def atmost(self, xs, k):
        if k >= len(xs):
            return
        if k < 0:
            self.add([])
            return
        s = self._counter(xs, k + 1)
        self._assert_false(s[k + 1])

    def and_aux(self, lits):
        """fresh z with z -> each lit (one direction; enough for positive use)."""
        z = self.new()
        for l in lits:
            self.add([-z, l])
        return z

    def and_def(self, lits):
        """fresh z with z <-> AND(lits)."""
        z = self.new()
        for l in lits:
            self.add([-z, l])
        self.add([z] + [-l for l in lits])
        return z

    def lex_geq(self, X, Y):
        """X >=lex Y (true > false), X[0] most significant.  e_i = 'prefix equal'."""
        e = None  # None = TRUE
        for i in range(len(X)):
            x, y = X[i], Y[i]
            if x == y:
                continue
            # e -> (x or not y)
            self.add(([-e] if e is not None else []) + [x, -y])
            if i == len(X) - 1:
                break
            e2 = self.new()
            pre = [-e] if e is not None else []
            self.add(pre + [x, y, e2])        # e & !x & !y -> e2
            self.add(pre + [-x, -y, e2])      # e & x & y -> e2
            e = e2

    def write(self, fn, comments=()):
        with open(fn, "w") as f:
            for c in comments:
                f.write(f"c {c}\n")
            f.write(f"p cnf {self.nv} {len(self.clauses)}\n")
            for cl in self.clauses:
                f.write(" ".join(map(str, cl)) + " 0\n")


# ----------------------------- self test -----------------------------------
def _sat(clauses, nv, fixed):
    """tiny DPLL: is clauses satisfiable extending the partial assignment fixed?"""
    assign = dict(fixed)

    def val(l):
        v = assign.get(abs(l))
        if v is None:
            return None
        return v if l > 0 else not v

    def rec():
        # unit propagation loop (naive)
        changed = True
        trail = []
        while changed:
            changed = False
            for cl in clauses:
                unassigned = []
                sat = False
                for l in cl:
                    v = val(l)
                    if v is True:
                        sat = True
                        break
                    if v is None:
                        unassigned.append(l)
                if sat:
                    continue
                if not unassigned:
                    for t in trail:
                        del assign[t]
                    return False
                if len(unassigned) == 1:
                    l = unassigned[0]
                    assign[abs(l)] = l > 0
                    trail.append(abs(l))
                    changed = True
        free = [v for v in range(1, nv + 1) if v not in assign]
        if not free:
            ok = True
        else:
            v = free[0]
            ok = False
            for b in (True, False):
                assign[v] = b
                if rec():
                    ok = True
                    break
                del assign[v]
        for t in trail:
            del assign[t]
        return ok

    return rec()


def selftest():
    for n in range(0, 7):
        for k in range(-1, n + 2):
            for kind in ("exactly", "atleast", "atmost"):
                c = CNF()
                xs = [c.new() for _ in range(n)]
                getattr(c, kind)(xs, k)
                for bits in product([False, True], repeat=n):
                    s = sum(bits)
                    want = {"exactly": s == k, "atleast": s >= k, "atmost": s <= k}[kind]
                    got = _sat(c.clauses, c.nv, {xs[i]: bits[i] for i in range(n)})
                    assert got == want, (n, k, kind, bits)
    for n in range(1, 6):
        c = CNF()
        X = [c.new() for _ in range(n)]
        Y = [c.new() for _ in range(n)]
        c.lex_geq(X, Y)
        for bx in product([0, 1], repeat=n):
            for by in product([0, 1], repeat=n):
                fixed = {X[i]: bool(bx[i]) for i in range(n)}
                fixed.update({Y[i]: bool(by[i]) for i in range(n)})
                assert _sat(c.clauses, c.nv, fixed) == (bx >= by)
        # shared variables (permuted vector): X vs its reversal
        c = CNF()
        X = [c.new() for _ in range(n)]
        c.lex_geq(X, X[::-1])
        for bx in product([0, 1], repeat=n):
            fixed = {X[i]: bool(bx[i]) for i in range(n)}
            assert _sat(c.clauses, c.nv, fixed) == (bx >= bx[::-1])
    # counter outputs as literals: s[j] <-> (sum >= j), both polarities
    for n in range(0, 6):
        for top in range(0, n + 1):
            for j in range(0, top + 1):
                for pol in (True, False):
                    c = CNF()
                    xs = [c.new() for _ in range(n)]
                    s = c._counter(xs, top)
                    (c._assert_true if pol else c._assert_false)(s[j])
                    for bits in product([False, True], repeat=n):
                        want = (sum(bits) >= j) == pol
                        got = _sat(c.clauses, c.nv, {xs[i]: bits[i] for i in range(n)})
                        assert got == want, (n, top, j, pol, bits)
    # and_def
    for n in range(1, 4):
        c = CNF()
        xs = [c.new() for _ in range(n)]
        z = c.and_def(xs)
        for bits in product([False, True], repeat=n):
            for zb in (False, True):
                fixed = {xs[i]: bits[i] for i in range(n)}
                fixed[z] = zb
                assert _sat(c.clauses, c.nv, fixed) == (zb == all(bits))
    print("cnflib selftest OK")


if __name__ == "__main__":
    selftest()
