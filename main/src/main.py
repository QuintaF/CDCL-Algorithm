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
            lines.append([list(clause), [None, None]])
            
    f.close()

    return unique(lines)


def unique(clauses):
    '''
    puts in a list every literal occurring in the clauses

    :returns: list of clauses, list of unique literals
    '''

    unique = set()

    for clause in clauses:
        for literal in clause[0]:
            unique.add(literal)

    return clauses, unique


def main():

    print("="*40)
    print(" "*16 + "STARTED")

    # input reading from a cnf file(first formatted by satlib_parser)
    s = time.time()
    cnf_parser(args)

    # file reading
    if args.sudoku:
        clause_list, literals = get_lines("../test/sudoku.txt")
    else:
        clause_list, literals = get_lines()
    
    # transforming the set into a list otherwise it would introduce randomness in the execution
    literals = list(literals)
    literals.sort()
    e = time.time()

    print(f"Preparation: {e-s:0.3f} sec")
    print(" "*7 + "EXECUTING CDCL ALGORITHM...")

    # call to CDCL algorithm
    s = time.time()
    satisfiable, model, num_learned = cdcl(clause_list, literals)
    e = time.time()
    
    print(f"CDCL execution time: {e-s:0.3f} sec")
    print(f"Learned clauses: {num_learned}")
    print("="*40)

    if satisfiable:
        print("The set of clauses is Satisfiable")
        # write model
        with open("../out/output.txt", 'w', encoding='utf-8') as file:
            sys.stdout = file
            model = list(model.items())
            print("Model for the set of clauses: ")
            for key, value in model:
                if value[0] == 1:
                    print(f'{key}')

            sys.stdout = sys.__stdout__
    else:
        print("The set of clauses is Unsatisfiable")

    return 0

if __name__ == '__main__':
    args = parse_args()
    main()