import os
import sys
import copy


def cdcl_procedure(clauses, literals, args):
    '''
    Conflict-Driven Clause Learning procedure.
    An algorithm to decide if a set of clauses is satisfiable(SAT) or unsatisfiable(UNSAT).

    Basic idea:
        use resolution in order to generate a conflict clause(a clause where every literal is False)
    MODES
        - Search Mode:
            - Transition Rules: Decision, (Unit)Propagation, Conflict, Success, Fail
        - Conflict Solving Mode:
            - Transition Rules: Backtrack(Backjump), Learn
            - Forget *
            - Restart *
            
    SAT: no more propagation nor decisions and no conflict generated
    UNSAT: empty clause generated or conflcit at level 0
    '''

    if not args.verbose:
        # stop terminal output
        sys.stdout = open(os.devnull, 'w')
    else:
        # output in file
        sys.stdout = open("../out/cdclsteps.txt", 'w', encoding='utf-8')

    # clearing proof output file
    open("../out/output.txt", 'w').close()

    learned_clauses = []
    trail_level = 0  # number of decisions
    trail = []  # tuples (implied literal, justification)
    state(trail)

    # Truth values and VSIDS initialization
    truth_values = {literal:[None, 0, None] for literal in literals} # [value, VSIDS value, level_of_assignment]
    literals = list(literals)
    last_index = 0

    # initialize watched literals(2WL)
    for clause in clauses:
        watched = 0
        for literal in clause[0]:
            clause[1][watched] = literal
            watched += 1
            if watched == 2:
                break;


# CDCL procedure: start

    # CDCL procedure: initial BCP
    for clause in clauses:
        if len(clause[0]) == 1:
            if truth_values[clause[1][0]][0] is None:
                # implied literal becomes 1(True)
                implied_literal = clause[1][0]
                truth_values[implied_literal][0] = 1
                truth_values[implied_literal][2] = trail_level

                if implied_literal[0] == '¬':
                    negated = implied_literal[1:]
                else: 
                    negated = '¬' + implied_literal

                # if its negation is present set it to 0(False)
                if negated in literals:
                    truth_values[negated][0] = 0
                    truth_values[negated][2] = trail_level

                reason = clause[0]
                trail.append((clause[1][0], reason))  # (implied_literal, reason)
                print(' => propagation => ', end='')
                state(trail)

            elif  truth_values[clause[1][0]][0] == 0:
                # conflict
                print(' => conflict => ', end='')
                state(trail, conflict_clause = clause[0])
                unsat_proof(trail, clause[0])
                return fail(args), None, len(learned_clauses) 
        else:
            # no more unit clauses
            break

    #check conflict
    conflict, cc = check_conflict(clauses, truth_values)
    if conflict:
        print(' => conflict => ', end='')
        state(trail, conflict_clause = clauses[cc][0])
        unsat_proof(trail, clauses[cc][0])
        return fail(args), None, len(learned_clauses) 
        
    clauses = cc

    # CDCL: propagation/decision loop
    while True:
        
        #check if all literals have been assigned
        unassigned = False
        for value in truth_values.values():
            if value[0] is None:
                unassigned = True
                break

        if not unassigned:
            return success(args), truth_values, len(learned_clauses) 
        
        conflict = False
        cc = clauses
        propagated = False

        #CDCL procedure: propagation BCP
        clause = check_propagation(clauses, truth_values)
        while clause is not None:
            propagated = True

            # implied literal becomes 1(True)
            implied_literal = clauses[clause][1][0]
            truth_values[implied_literal][0] = 1
            truth_values[implied_literal][2] = trail_level

            if implied_literal[0] == '¬':
                negated = implied_literal[1:]
            else: 
                negated = '¬' + implied_literal
                
            reason = clauses[clause][0]
            trail.append((implied_literal, reason)) 
            print(' => propagation => ', end='')
            state(trail)

            # if negation of the implied_literal exists set it to 0(False)
            if negated in literals:
                truth_values[negated][0] = 0
                truth_values[negated][2] = trail_level
                # check conflicts via 2WL
                conflict, cc = check_conflict(clauses, truth_values)
                if conflict:
                    cc = clauses[cc][0]
                    break;
                else:
                    clauses = cc
            
            clause = check_propagation(clauses, truth_values)

        #CDCL procedure: VSIDS decision
        if not propagated:
            trail_level += 1

            if (len(learned_clauses) + 1) % 250 == 0:
                decay(truth_values)
                # sorting literals by VSIDS value    
                literals = sorted(literals, key = lambda literal: truth_values[literal][1])[::-1]
                last_index = 0

            literal = ''
            for last_index in range(last_index, len(literals)-1):
                literal = literals[last_index]
                if truth_values[literal][0] == None:
                    truth_values[literal][0] = 1
                    truth_values[literal][2] = trail_level
                    
                    if literal[0] == '¬':
                        negated = literal[1:]
                    else:
                        negated = '¬' + literal

                    if negated in literals:
                        truth_values[negated][0] = 0
                        truth_values[negated][2] = trail_level
                        conflict, cc = check_conflict(clauses, truth_values)
                        if conflict:
                            cc = clauses[cc][0]
                        else:
                            clauses = cc
                    
                    last_index += 1
                    break;
            
            trail.append((literal, None))
            print(' => decision => ', end='')
            state(trail, learned_clauses = learned_clauses)
        
        # CDCL: conflict analyss
        if conflict:
            print(' => conflict => ', end='')
            state(trail, learned_clauses = learned_clauses, conflict_clause = cc)
            if trail_level == 0:
                unsat_proof(trail, cc)
                return fail(args), None, len(learned_clauses) 

            # 1UIP(Learning Heuristic)
            backjump_level, learn = first_unique_implication_point(truth_values, trail, cc)   
            print(' => explain => ', end='')  
            state(trail, learned_clauses = learned_clauses, conflict_clause= learn)   

            # Learn clause
            present = False
            for clause in clauses:
                if learn in clause[0]:
                    present = True

            if not present:
                # VSIDS: sum
                for literal in learn:
                    truth_values[literal][1] += 1

                learned_clauses.append(learn)
                for idx,el in enumerate(clauses):
                    if len(el[0]) >= len(learn):
                        clauses.insert(idx, [learn, [None, None]])
                        break
                    elif idx == len(clauses)-1:
                        clauses.append([learn, [None, None]])
                        break
                
            print(' => learn => ', end='')
            state(trail, learned_clauses= learned_clauses, conflict_clause= learn)

            # Backjump
            # undo all assignments until the backjump level
            while True:
                # undo assignment
                step = trail.pop()
                literal = step[0]

                # VSIDS: return to first unassigned variable
                last_index = min(last_index, literals.index(literal))
                
                if literal[0] == '¬':
                    negated = literal[1:]
                else:
                    negated = '¬' + literal

                level = truth_values[literal][2]
                truth_values[literal][0] = None
                truth_values[literal][2] = None
                if negated in literals:
                    truth_values[negated][0] = None
                    truth_values[negated][2] = None

                if step[1] is None and level == backjump_level + 1:
                    #reached backjump level
                    break;
            
            trail_level = backjump_level
            print(' => backjump => ', end='')
            state(trail, learned_clauses= learned_clauses)

            # restores 2WL for the clauses
            # necessary in case of more than 1 conflict        
            conflict, cc = check_conflict(clauses, truth_values)
        else:
            clauses = cc


def state(trail, learned_clauses = [], conflict_clause = None):
    '''
    prints the transitions state.
    '''
    
    steps = [step[0] for step in trail]
    text = lambda learn, cc: f"{steps} || S{' U  L' if len(learn) > 0 else ''}{' || ' + str(cc) if cc else ''}"
    print(text(learned_clauses, conflict_clause), end='')


def check_propagation(clauses, truth_values):
    '''
    Search for implied literals.

    :returns: None if no implied literals, else the clause having an implied literal
    '''
    
    for idx, clause in enumerate(clauses):
        if clause[1][1] is None:
            if truth_values[clause[1][0]][0] is None:
                #implied literal
                return idx
    
    return None


def check_conflict(clauses, truth_values):
    '''
    Checks the watched literals and acts accordingly:
        - both are not false, do nothing
        - one false: look for another literal in the clause
        - both false: look for two implied literals

    :return: true if conflict, false otherwise
    '''

    for idx,clause in enumerate(clauses):
        #search another literal
        new_watched = search_watched_literal(clause, truth_values)

        if new_watched[0] == None and new_watched[1] == None:
            # found 0: conflict
            return True, idx

        clause[1] = new_watched

    return False, clauses


def search_watched_literal(clause, truth_values):
    '''
    Searches another not false literal in the clause:

    :returns: two watched literals, one implied literal or None
    '''
    watched = [clause[1][0], clause[1][1]]

    def search():
        '''
        Looks for another literal that is not false 

        :returns: literal or None
        '''

        for literal in clause[0]:
            if truth_values[literal][0] != 0 and literal not in watched:
                return literal
        
        return None
                    
    # check watched literals
    for idx, literal in enumerate(watched):
        if literal is None:
            watched[idx] = search()
        elif truth_values[literal][0] == 0:
            watched[idx] = search()

    if watched[0] is None:
        return [watched[1], None]
    else:
        return watched 


def first_unique_implication_point(truth_values, trail, cc):
    '''
    applies the 1UIP(aka First Assertion Clause) heuristic to find the learn clause, prints the resolution steps in the output file(main/out/output.txt).
    Procedure:
        - loop on trail backwards
        - if learned_clause is assertion_clause then return learned_clause
        - else if literal is in conflict_clause then:
               . resolution between conflict_clause and reason
               
    :returns: learn clause
    '''

    try:
        output_file = open("../out/output.txt", 'a', encoding='utf-8')
        currout = sys.stdout
        sys.stdout = output_file
        print(f"Resolution steps:\n")
        print(f"CC∨¬L   L∨D\n-----------\n    CC∨D\n")
    except FileNotFoundError:
        print("File does not exist")
    except Exception as e:
        print(f"An exception occurred when opening file {e}")

    blank = 0  # resolution line offset

    learned = copy.deepcopy(cc)
    conflict_level = truth_values[trail[-1][0]][2]  # the last literal on the trail generates the conflict

    is_assertion, backjump_level = check_assertion(learned, truth_values, conflict_level)
    if is_assertion:
        return backjump_level, learned

    for step in trail[::-1]:
        if step[1] is None:
            # decision
            continue;
        
        literal = step[0]
        if literal[0] == '¬':
            negated = literal[1:]
        else:
            negated = '¬' + literal

        if negated in learned:
            # resolution(remove literal and keep others)
            antecedent = copy.deepcopy(step[1])
            antecedent.remove(step[0])

            learned.remove(negated)
            txt = f"{learned}∨{negated}        {literal}∨{antecedent}"
            learned = learned.union(antecedent)

            # write resolution step in the file
            print(txt)
            print(' ' * blank, end='')
            print("-" * len(txt))
            blank += len(learned) + 3
            print(' ' * blank, end='')

            is_assertion, backjump_level = check_assertion(learned, truth_values, conflict_level)
            if is_assertion:
                # print final clause and restore standard output
                print(f"{learned}\n")
                sys.stdout = currout
                output_file.close()

                return backjump_level, learned


def check_assertion(clause, truth_values, conflict_level):
    '''
    checks if the clause generated by the 1UIP procedure
    is an assertion clause(UIP)

    :returns: True or False
    '''

    # defined by the literal at the lowest level in the clause(conflict_level excluded)
    backjump_level = 0  

    count = 0
    for literal in clause:
        level = truth_values[literal][2]
        if level == conflict_level:
            count += 1
            if count > 1:
                return False, backjump_level
        elif level > backjump_level:
            backjump_level = level
        

    return True, backjump_level


def decay(truth_values):
    '''
    decaying sums for the VSIDS heuristic

    :returns:
    '''

    for values in truth_values.values():
        values[1] /= 2


def unsat_proof(trail, cc):
    '''
    a conflict happened at the lowest level (S ⊨ □).
    prints on the output file the proof of unsatisfiability
    as resolution steps
    '''
    
    try:
        output_file = open("../out/output.txt", 'a', encoding='utf-8')
        currout = sys.stdout
        sys.stdout = output_file
        print(f"Resolution steps:\n")
    except FileNotFoundError:
        print("File does not exist")
    except Exception as e:
        print(f"An exception occurred when opening file {e}")

    blank = 0
    learned = cc
    for step in trail[::-1]:
        literal = step[0]
        if literal[0] == '¬':
            negated = literal[1:]
        else:
            negated = '¬' + literal

        if negated in learned:

            # resolution(remove literal and keep others)
            antecedent = copy.deepcopy(step[1])
            antecedent.remove(step[0])

            learned.remove(negated)
            txt = f"{learned}∨{negated}        {literal}∨{antecedent}"
            learned = learned.union(antecedent)
            
            if len(learned) == 0:
                txt = f"{negated}        {literal}"

            print(txt)
            print(' ' * blank, end='')
            print("-" * len(txt))
            blank += len(learned) + 3
            print(' ' * blank, end='')

    # write empty clause and restore standard output
    print(f"{' ' * len(negated)}□\n")
    sys.stdout = currout
    output_file.close()


def fail(args):
    '''
    The resolution steps lead to a failure.
    The set of clauses is unsatisfiable

    :returns: False(UNSAT)
    '''

    print(' => fail => UNSAT')
    if args.verbose:
        # close file
        sys.stdout.close()
    
    
    sys.stdout = sys.__stdout__
    return False


def success(args):
    '''
    The resolution steps lead to a success.
    The set of clauses is satisfiable

    :returns: True(SAT)
    '''    
    
    print(' => success => SAT')

    if args.verbose:
        # close file
        sys.stdout.close()

    sys.stdout = sys.__stdout__
    return True