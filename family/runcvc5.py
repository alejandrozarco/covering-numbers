import sys, time, cvc5
tm = cvc5.TermManager(); s = cvc5.Solver(tm)
s.setOption('produce-models', 'false')
for o in sys.argv[2:]:
    k, v = o.split('='); s.setOption(k, v)
p = cvc5.InputParser(s); p.setFileInput(cvc5.InputLanguage.SMT_LIB_2_6, sys.argv[1])
sm = p.getSymbolManager()
t = time.time()
while True:
    cmd = p.nextCommand()
    if cmd.isNull(): break
    r = cmd.invoke(s, sm)
    if r.strip(): print(r.strip(), round(time.time() - t, 1), flush=True)
