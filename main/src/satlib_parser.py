'''
this file creates a well formatted file from this library: https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html.

#cnf example(',' is a newline in the cnf file): 
    ['c horn? no', 
     'c forced? no', 
     'c mixed sat? no', 
     'c clause length = 3', 
     'c', 
     'p cnf 20  91', #20 variables, 91 clauses
     '4 -18 19 0', 
     '3 18 -5 0', 
     '-5 -8 -15 0', 
     '-20 7 -16 0']
'''

def cnf_parser(args):

    if args.custom:
        file = "custom.cnf"
    elif args.cnf == "SAT":
        file = "uf50-01000.cnf"
    elif args.cnf == "UNSAT":
        file = "uuf50-01000.cnf"
    elif args.pidgeonhole:
        file =  "ph" + str(args.pidgeonhole) + ".cnf"
    else:
        # no option, no parsing
        return None

    #read file
    with open('../test/cnf/'+ file, mode='r', encoding='utf-8') as f:
        cnf = ['']
        for line in f.read().splitlines():    
            tokens = line.split()
            if len(tokens) != 0 and tokens[0] not in ("p", "c", "%"):
                for tok in tokens:
                    if tok == '0':
                        cnf[-1] = cnf[-1][:-1]
                        cnf.append('')
                    else:
                        tok = tok.replace('-', '¬')
                        cnf[-1] = cnf[-1] + tok +'∨'

    # write in input file
    with open('../test/input.txt', mode = 'w', encoding='utf-8') as file:
        for clause in cnf:
            file.write(clause+"\n")

