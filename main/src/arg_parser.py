import argparse

def parse_args():
    '''
    builds a parser for command line arguments

    :returns: args values
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument("--pidgeonhole", "-ph", action="store", choices=['5','6','7','8','9'], help="choose one between the 3 instances of the pidgeon hole problem as input(all unsatisfiable)")
    parser.add_argument("--cnf", action="store", choices=["SAT","UNSAT"], help="reads input from a file in the test folder based on choice: uf50-01000 if SAT, uuf50-01000 if UNSAT")
    parser.add_argument("--sudoku", "-s", action="store_true", help="reads input from 'sudoku.txt'")
    parser.add_argument("--custom", "-c", action="store_true", help="reads input from 'custom.cnf'")

    return parser.parse_args()