#directory change
import os, sys
file_path = os.path.dirname(__file__)
os.chdir(file_path)

#modules
import re

#sat procdedure functions
from cdcl import cdcl_procedure as cdcl


def getLines():
    '''
    reads every line from the text file containing the clauses(be sure to have them line separated)
    checks that the clauses red from the file are correctly formatted(if not it skips them)
    and formats the remaining to simplify control

    :returns: list of clauses
    '''

    f = open('../test/input.txt', mode='r', encoding='utf-8')
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
    clause_list, literals = getLines()
    print("Input clauses: " + str([c[0] for c in clause_list]))
    print("Unique literals: " + str(literals))
    print("Starting Conflict-Driven Clause Learning procedure for satisfiability decision...\n")
    
    satisfiable, values = cdcl(clause_list, literals)

    if satisfiable:
        print(values)

    return 0

if __name__ == '__main__':
    main()


''' 
TODO
# IMPLEMENT DECISION HEURISTIC: VSIDS
- Better output formatting
- Try to get better management of explaining solution
'''