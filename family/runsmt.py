import sys, time, z3
s = z3.Solver()
s.set('threads', 1) if False else None
s.from_file(sys.argv[1])
t = time.time(); r = s.check(); print(r, round(time.time() - t, 1), flush=True)
if r == z3.sat and len(sys.argv) > 2:
    m = s.model(); print(m)
