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
    Reads every line from the text file containing the clauses(be sure to have them line separated)
    and removes any space from the lines to simplify string control

    :returns: list of clauses without spaces
    '''

    f = open('../test/input.txt', mode='r', encoding='utf-8')
    lines = [line.replace(' ', '') for line in f.read().splitlines()]
    f.close()
    lines = [s.upper() for s in lines]

    return sort(checkStrings(lines))


def checkStrings(clauses):
    '''
    checks that the clauses red from the file are correctly formatted
    and removes them

    :returns: formatted clauses
    '''
    rem = []
    for idx in range(len(clauses)):
        match = re.match('^(¬?(([A-Z]+[0-9]*)|¬?[A-Z]+[0-9]*(∨¬?[A-Z]+[0-9]*)*)∧)*¬?(([A-Z]+[0-9]*)|¬?[A-Z]+[0-9]*(∨¬?[A-Z]+[0-9]*)*)$', clauses[idx])
        if match is None:
            rem.append(idx)
            print(f"String {idx} is improperly typed!")

    # removing bad typed strings
    for idx in rem[::-1]:
        del clauses[idx]

    return clauses


def sort(clauses):
    '''
    sorts clauses by number of literals

    :returns: ordered list of clauses, list of unique literals
    '''

    sorted_clauses = []
    unique = {}
    for clause in clauses:
        literals = 0
        for idx,char in enumerate(clause):
            if char.isalpha():
                literals += 1
                if clause[idx-1] == '¬':
                    unique.add('¬' + char)
                else:
                    unique.add(char)

        if len(sorted_clauses) == 0:
            sorted_clauses.append([clause, literals, [None, None]])
        else:
            for idx,el in enumerate(sorted_clauses):
                if el[1] >= literals:
                    sorted_clauses.insert(idx, [clause, literals, [None, None]])
                    break
                elif idx == len(sorted_clauses)-1:
                    sorted_clauses.append([clause, literals, [None, None]])
                    break

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
# IMPLEMENT DECISION HEURISTIC: VSIDS
- Better output formatting
- Try to get better management of explaining solution
- Let propositions be either letter numbers both
'''