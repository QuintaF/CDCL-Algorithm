#directory change
import os, sys
file_path = os.path.dirname(__file__)
os.chdir(file_path)

# modules
import re
import time

# sat procdedure functions
from cdcl import cdcl_procedure as cdcl

# parser
from satlib_parser import cnf_parser
from arg_parser import parse_args


def get_lines(filename = '../test/input.txt'):
    '''
    reads every line from the text file containing the clauses(be sure to have them line separated)
    checks that the clauses red from the file are correctly formatted(if not it skips them)
    and formats the remaining to simplify control

    :returns: list of clauses
    '''

    f = open(filename, mode='r', encoding='utf-8')
    lines = []
    count = 0
    for line in f.read().splitlines():
        count += 1
        clause = line.replace(' ','').upper()
        
        # possible clause reduction regex: ^(¬?(([A-Z]+[0-9]*)|¬?[A-Z]+[0-9]*(∨¬?[A-Z]+[0-9]*)*)∧)*¬?(([A-Z]+[0-9]*)|¬?[A-Z]+[0-9]*(∨¬?[A-Z]+[0-9]*)*)$
        match = re.match('^(¬?([0-9]|[A-Z])+∨)*¬?([0-9]|[A-Z])+$', clause)
        if match is None:
            print(f"String {count} is improperly typed!")
        else:
            clause = set(clause.split('∨'))
            lines.append(clause)
            
    f.close()

    return sort(lines)


def sort(clauses):
    '''
    sorts clauses by number of literals

    :returns: ordered list of clauses, list of unique literals
    '''

    unique = set()
    sorted_clauses = []

    for clause in clauses:
        for literal in clause:
            unique.add(literal)

        inserted = False
        literals = len(clause)
        for idx, el in enumerate(sorted_clauses):
            if len(el[0]) >= literals:
                sorted_clauses.insert(idx, [clause, [None, None]])
                inserted = True
                break
        
        if not inserted:
            sorted_clauses.append([clause, [None, None]])

    return sorted_clauses, unique


def main():

    print("="*20)
    print("STARTED")

    if args.cnf:
        # input read from a cnf file(first formatted by satlib_parser)
        print("CNF file: " + str(cnf_parser(args.cnf)))
    if not args.verbose:
        #outputs everything on terminal
        sys.stdout = open(os.devnull, 'w')
    if args.output:
        sys.stdout = open(args.output, 'w')

    s = time.time()
    clause_list, literals = get_lines()
    e = time.time()
    print("Input clauses: " + str([c[0] for c in clause_list]))
    print("Unique literals: " + str(literals))
    print("Starting Conflict-Driven Clause Learning procedure for satisfiability decision...\n")
    

    print(f"File parsing time: {e-s}")

    print("EXECUTING CDCL ALGORITHM...")
    s = time.time()
    satisfiable, values = cdcl(clause_list, literals)
    e = time.time()
    
    sys.stdout = sys.__stdout__
    print(f"CDCL execution time: {e-s}")
    print("clause learned: ")
    print("="*20)

    if satisfiable:
        print(values)

    return 0

if __name__ == '__main__':
    args = parse_args()
    main()

''' 
TODO
# IMPLEMENT DECISION HEURISTIC: VSIDS
- Better output formatting
- Try to get better management of explaining solution
'''