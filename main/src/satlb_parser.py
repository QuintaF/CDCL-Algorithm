in_data = ['c horn? no', 'c forced? no', 'c mixed sat? no', 'c clause length = 3', 'c', 'p cnf 20  91', '4 -18 19 0', '3 18 -5 0', '-5 -8 -15 0', '-20 7 -16 0']

cnf = list()
cnf.append(list())
maxvar = 0

for line in in_data:
    tokens = line.split()
    if len(tokens) != 0 and tokens[0] not in ("p", "c"):
        for tok in tokens:
            lit = int(tok)
            maxvar = max(maxvar, abs(lit))
            if lit == 0:
                cnf.append(list())
            else:
                cnf[-1].append(lit)

assert len(cnf[-1]) == 0
cnf.pop()

print(cnf)
print(maxvar)