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

    print("="*40)
    print(" "*16 + "STARTED")

    # input reading from a cnf file(first formatted by satlib_parser)
    s = time.time()
    if args.cnf:
        cnf_parser(args.cnf)
    elif args.pidgeonhole:
        cnf_parser(args.pidgeonhole)

    # file reading
    clause_list, literals = get_lines()
    e = time.time()
    print(f"File parsing: {e-s:0.3f} sec")
    print("Unique literals: " + str(literals))
    print(" "*7 + "EXECUTING CDCL ALGORITHM...")

    # call to CDCL algorithm
    s = time.time()
    satisfiable, model, num_learned = cdcl(clause_list, literals, args)
    e = time.time()
    
    print(f"CDCL execution time: {e-s:0.3f} sec")
    print(f"Learned clauses: {num_learned}")
    print("="*40)

    if satisfiable:
        print("The set of clauses is Satisfiable")
        # writing model
        with open("../out/output.txt", 'w', encoding='utf-8') as file:
            sys.stdout = file
            model = list(model.items())
            print("Model for the set of clauses: ")
            for key, value in model:
                if value[0] == 1:
                    print(f'{key}: {value[0]}')

            sys.stdout = sys.__stdout__
    else:
        print("The set of clauses is Unsatisfiable")

    return 0

if __name__ == '__main__':
    args = parse_args()
    main()