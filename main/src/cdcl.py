import os
import sys
import copy

def cdcl_procedure(clauses, literals):
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
            
    SAT: no more propagation nor decisions, and no conflict generated
    UNSAT: empty clause generated or conflcit at level 0
    '''

    # clearing proof output file
    open("../out/output.txt", 'w').close()

    learned_clauses = 0
    trail_level = 0  # number of decisions
    trail = []  # tuples (implied literal, justification)

    # Truth values and VSIDS initialization
    truth_values = {literal:[None, 0, None] for literal in literals} # [value, VSIDS value, level_of_assignment]
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

    # CDCL procedure: initial BCP(make true all unit clauses)
    propagated = False
    for clause in clauses:
        if clause[1][1] == None:
            propagated = True
            if  truth_values[clause[1][0]][0] == 0:
                # conflict at level 0
                if len(trail) <= 50:
                    unsat_proof(trail, clause[0])
                return fail(), None, learned_clauses
    
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

    #check conflict
    conflict = False
    cc = clauses
    if propagated:
        for clause in clauses:
            #search another literal
            new_watched = search_watched_literal(clause, truth_values)

            if new_watched[0] == None and new_watched[1] == None:
                # found 0: conflict
                conflict = True
                cc = clause
                break
        
            clause[1] = new_watched

    if conflict:
        # conflict at level 0
        if len(trail) <= 50:
            unsat_proof(trail, clauses[cc][0])
        return fail(), None, learned_clauses 
        
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
            return success(), truth_values, learned_clauses 
        
        conflict = False
        cc = clauses

        #CDCL procedure: VSIDS decision
        if not propagated:
            trail_level += 1

            if (learned_clauses + 1) % 250 == 0:
                decay(truth_values)
                # sorting literals by VSIDS value    
                literals = sorted(literals, key = lambda literal: truth_values[literal][1])[::-1]
                last_index = 0

            literal = ''
            for last_index in range(last_index, len(literals)):
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
                        conflict, cc = check_conflict(clauses, truth_values, negated = negated)
                        clauses = cc
                    
                    last_index += 1
                    break;
            
            trail.append((literal, None))

        #CDCL procedure: propagation BCP
        propagated = False
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

            # if negation of the implied_literal exists set it to 0(False)
            if negated in literals:
                truth_values[negated][0] = 0
                truth_values[negated][2] = trail_level
                # check conflicts via 2WL
                conflict, cc = check_conflict(clauses, truth_values, negated = negated)
                if conflict:
                    cc = clauses[cc][0]
                    break;
                else:
                    clauses = cc
            
            clause = check_propagation(clauses, truth_values)
        
        # CDCL: conflict analsys
        if conflict:
            if trail_level == 0:
                if len(trail) <= 50:
                    unsat_proof(trail, cc)
                return fail(), None, learned_clauses 

            # 1UIP(Learning Heuristic)
            backjump_level, learn = first_unique_implication_point(truth_values, trail, cc)   
            
            # Learn clause
            # VSIDS: sum
            for literal in learn:
                truth_values[literal][1] += 1

            learned_clauses += 1
            clauses.insert(0,[learn, [None, None]])

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

            # restores 2WL for the clauses
            # necessary in case of more than 1 conflict
            for clause in clauses:
                #search another literal
                new_watched = search_watched_literal(clause, truth_values)
                clause[1] = new_watched

        else:
            clauses = cc


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


def check_conflict(clauses, truth_values, negated):
    '''
    Checks the watched literals and acts accordingly:
        - both are not false, do nothing
        - one false: look for another literal in the clause
        - both false: look for two implied literals

    :return: true if conflict, false otherwise
    '''

    for idx,clause in enumerate(clauses):
        if negated in clause[1]:
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
    applies the 1UIP(aka First Assertion Clause) heuristic to find the learn clause.
    Procedure:
        - loop on trail backwards
        - if learned_clause is assertion_clause then return learned_clause
        - else if literal is in conflict_clause then:
               . resolution between conflict_clause and reason
               
    :returns: learn clause
    '''

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
            learned = learned.union(antecedent)

            is_assertion, backjump_level = check_assertion(learned, truth_values, conflict_level)
            if is_assertion:
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


def fail():
    '''
    The resolution steps lead to a failure.
    The set of clauses is unsatisfiable

    :returns: False(UNSAT)
    '''
    
    return False


def success():
    '''
    The resolution steps lead to a success.
    The set of clauses is satisfiable

    :returns: True(SAT)
    ''' 

    return True