import argparse

def parse_args():
    '''
    builds a parser for command line arguments

    :returns: args values
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument("--pidgeonhole", "-ph", action="store", choices=['4','5','6','7','8','9','10'], help="reads as input the pidgeon hole instance file chosen(ph[N].cnf)")
    parser.add_argument("--cnf", action="store", choices=["SAT","UNSAT"], help="reads input from a file in the test folder based on choice: uf50-01000 if SAT, uuf50-01000 if UNSAT")
    parser.add_argument("--verbose", "-v", action="store_true", help="writes in 'main/out/cdclsteps.txt' every passage of the cdcl algorithm in the following format: '... => action => trail||clauses(||possible conflict)...'")

    return parser.parse_args()