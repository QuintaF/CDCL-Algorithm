import argparse

def parse_args():
    '''
    builds a parser for 
    command line arguments

    :returns: args values
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument("--cnf", action="store", choices=["SAT","UNSAT"], help="reads input from a random file in the test folder based on choice: UF... if SAT, UUF... if UNSAT")
    parser.add_argument("--verbose", "-v", action="store_true", help="outputs on terminal every passage of the cdcl algorithm in the following format: '... => action => trail||clauses(||possible conflict)...'")
    parser.add_argument("--output", "--out", "-o", action="store", nargs='*', help="path in which to save the output of the algorithm(final stats are still printed in terminal)")

    return parser.parse_args()