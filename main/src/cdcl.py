import copy

def cdcl_procedure(clauses, literals):
    '''
    Conflict-Driven Clause Learning procedure.
    A method to decide isf a set of clauses is satisfiable(SAT) or unsatisfiable(UNSAT).

    Basic idea:
        use resolution in order to generate a conflict clause(a clause where every literal its FALSE)
    MODES
        - Search Mode:
            - State: M || S
            - Transition Rules: Decision, (Unit)Propagation, Conflict, Success, Fail
        - Conflict Solving Mode:
            - State: M || S || C
            - Transition Rules: Backtrack(Backjump), Learn
            - Forget *
            - Restart *
            
    SAT: no more propagation nor decisions and no conflict generated
    UNSAT: empty clause generated or conflcit at level 0
    '''


    learned_clauses = []
    trail_level = 0  # number of decisions
    trail = []  # tuples (implied literal, justification)
    state(trail, clauses)

    # Truth values and VSIDS initialization
    truth_values = {literal:[None, 0, None] for literal in literals} # [value, VSIDS value, level_of_assignment]

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
                if negated in truth_values.keys():
                    truth_values[negated][0] = 0
                    truth_values[negated][2] = trail_level

                reason = clause[0]
                trail.append((clause[1][0], reason))  # (implied_literal, reason)
                print(' => propagation => ', end='')
                state(trail, clauses)

            elif  truth_values[clause[1][0]][0] == 0:
                # conflict
                print(' => conflict => ', end='')
                state(trail, clauses, conflict_clause = clause[0])
                return fail(), None
        else:
            # no more unit clauses
            break

    #check conflict
    conflict, cc = check_conflict(clauses, truth_values)
    if conflict:
        print(' => conflict => ', end='')
        state(trail, clauses, conflict_clause = clauses[cc][0])
        return fail(), None
        
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
            return success(), truth_values 
        
        conflict = False
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
                
            # if negation of the implied_literal exists set it to 0(False)
            if negated in truth_values.keys():
                truth_values[negated][0] = 0
                truth_values[negated][2] = trail_level
                
            reason = clauses[clause][0]
            trail.append((implied_literal, reason)) 
            print(' => propagation => ', end='')
            state(trail, clauses)

            # check conflicts via 2WL
            conflict, cc = check_conflict(clauses, truth_values)

            if conflict:
                cc = clauses[cc][0]
                break;
            
            clauses = cc
            clause = check_propagation(clauses, truth_values)


        #CDCL procedure: decision
        if not propagated:
            trail_level += 1
            literal = ''
            for literal in truth_values.keys():
                if truth_values[literal][0] == None:
                    truth_values[literal][0] = 1
                    truth_values[literal][2] = trail_level
                    
                    if literal[0] == '¬':
                        negated = literal[1:]
                    else:
                        negated = '¬' + literal

                    if negated in truth_values.keys():
                        truth_values[negated][0] = 0
                        truth_values[negated][2] = trail_level
                        conflict, cc = check_conflict(clauses, truth_values)

                    if conflict:
                        cc = clauses[cc][0]
                    break

            trail.append((literal, None))
            print(' => decision => ', end='')
            state(trail, clauses, learned_clauses = learned_clauses)

            # VSIDS decision
            '''
            max_score = max(truth_values.values())
            candidates = [var for var, score in self.scores.items() if score == max_score]
            return random.choice(candidates)
            
        
            # Use VSDIS
                # L_sum = #times L appears in the learned clauses
                # Decaying sum:
                #   - multiply sum by aplha in (0,1)
                #   - increment bump K to add to the sum(baseic k +=1, recent weights more than older)
            #trail_level += 1 
                # WHEN TO INCREMENT?
                def bump(self, variable):
                    self.scores[variable] += 1

                #WHEN TO DECAY ?
                def decay(self, factor):
                    for var in self.variables:
                        self.scores[var] *= factor
        '''
        
        if conflict:
            print(' => conflict => ', end='')
            state(trail, clauses, learned_clauses = learned_clauses, conflict_clause = cc)
            if trail_level == 0:
                return fail(), None

            # find 1UIP(Learning Heuristic)
            backjump_level, learn = first_unique_implication_point(truth_values, trail, cc)   
            print(' => explain => ', end='')
            if learn is None:
                state(trail, clauses, learned_clauses= learned_clauses, conflict_clause= '□')
                return fail(), None    
            
            state(trail, clauses, learned_clauses = learned_clauses, conflict_clause= learn)   

            '''
            Old and probably useless/ovecomplicated/ non efficient
            # 1 Explain 
            learn = explain(clauses, trail, cc)
            print(' => explain => ', end='')
            if learn is None:
                state(trail, clauses, learned_clauses= learned_clauses, conflict_clause= '□')
                return fail(), None
            
            state(trail, clauses, learned_clauses= learned_clauses, conflict_clause= learn)
            '''
            # 2 Learn
            present = False
            for clause in clauses:
                if learn in clause[0]:
                    present = True

            if not present:
                learned_clauses.append(learn)
                for idx,el in enumerate(clauses):
                    if len(el[0]) >= len(learn):
                        clauses.insert(idx, [learn, [None, None]])
                        break
                    elif idx == len(clauses)-1:
                        clauses.append([learn, [None, None]])
                        break

            print(' => learn => ', end='')
            state(trail, clauses, learned_clauses= learned_clauses, conflict_clause= learn)
                        
            # 3 Backjump
            # undo all assignments until the backjump level
            while True:
                # undo assignment
                step = trail.pop()
                literal = step[0]
                
                if literal[0] == '¬':
                    negated = literal[1:]
                else:
                    negated = '¬' + literal

                level = truth_values[literal][2]
                truth_values[literal][0] = None
                truth_values[literal][2] = None
                if negated in truth_values.keys():
                    truth_values[negated][0] = None
                    truth_values[negated][2] = None

                if step[1] is None and level == backjump_level + 1:
                    #reached backjump level
                    break;
            
            trail_level = backjump_level
            print(' => backjump => ', end='')
            state(trail, clauses, learned_clauses= learned_clauses)

            # restores 2WL for the clauses
            # necessary in case of more than 1 conflict        
            conflict, cc = check_conflict(clauses, truth_values)
        else:
            clauses = cc


def state(trail, clauses, learned_clauses = None, conflict_clause = None):
    '''
    Prints the transitions until now.
    '''

    text = lambda learn, cc: f"{trail} || {[c[0] for c in clauses]}{' U ' + str(learn) if learn else ''}{' || ' + str(cc) if cc else ''}"
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
    applies the 1UIP(aka First Assertion Clause) procedure to find the learn clause.
    Procedure:
        - loop on trail backwards
        - if literal assignment_level < conflict_level then stop
        - else if literal is in conflict_clause then:
               . conflict_clause = resolve(conflict_clause, reason)
               
    :returns: learn clause
    '''
    learned = copy.deepcopy(cc)
    conflict_level = truth_values[trail[-1][0]][2] # last literal on the trail generated the conflict

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

    if len(learned) == 0:
        return -1, None

    return backjump_level, learned


def check_assertion(clause, truth_values, conflict_level):
    '''
    checks if the clause generated by the 1UIP procedure
    is an assertion clause(hence UIP)

    :returns: True or False
    '''
    count = 0
    backjump_level = 0
    for literal in clause:
        level = truth_values[literal][2]
        if level == conflict_level:
            count += 1
            if count > 1:
                return False, backjump_level
        elif level > backjump_level:
            backjump_level = level
        

    return True, backjump_level


def explain(clauses, trail, conflict_clause):
    '''
    Transforms the conflict clause into an 
    assertion clause (i.e. cc where only one false literal at the current level)
    
    :returns: assertion literal or None if empty clause is generated
    '''

    # take all trail steps until the first decision
    explanation = []
    for step in trail[::-1]:
        if step[1] is None:
            break;
        explanation.append(step)

    
    print("\n\n")
    blank = 0
    for step in explanation:
        # explaination tree cycle 
        oth_clause = step[1]
                
        print(conflict_clause + ' '*8 + oth_clause)

        print(' ' * blank, end='')
        print("-" * (len(conflict_clause)+8+len(oth_clause)))
        blank += len(conflict_clause) + 2
        print(' ' * blank, end='')

        if '¬' in step[0]:
            negated = step[0][1]
            conflict_clause = conflict_clause[:2].replace(negated+'∨', '') + conflict_clause[2:].replace('∨'+negated, '')
            oth_clause = oth_clause.replace('∨'+step[0], '')
            oth_clause = oth_clause.replace(step[0]+'∨', '')
        else:
            negated = '¬' + step[0]
            conflict_clause = conflict_clause.replace('∨'+negated, '')
            conflict_clause = conflict_clause.replace(negated+'∨', '')
            oth_clause = oth_clause = oth_clause[:2].replace(step[0]+'∨', '') + oth_clause[2:].replace('∨'+step[0], '')
            

        if len(conflict_clause) + len(oth_clause) == 0:
            print('□')
            return None
        elif len(conflict_clause) + len(oth_clause) == 1:
            assertion_literal = max([conflict_clause, oth_clause],key=len)
            if '¬' in assertion_literal:
                negated = assertion_literal[1]
            else:
                negated = '¬' + assertion_literal
            
            if negated in clauses:
                print(assertion_literal + ' '*8 + negated)
                print("-" * (len(assertion_literal)+8+len(negated)))
                print(' ' * (len(assertion_literal) + 2) + '□')
                return None
            else:
                conflict_clause = assertion_literal
                break

        
        conflict_clause = conflict_clause + '∨' + oth_clause

    print(conflict_clause)
    print("\n")
    return conflict_clause


def fail():
    '''
    The resolution steps lead to a failure.
    The set of clauses is unsatisfiable

    :returns: False(UNSAT)
    '''

    print(' => fail => UNSAT')
    return False

def success():
    '''
    The resolution steps lead to a success.
    The set of clauses is satisfiable

    :returns: True(SAT)
    '''

    print(' => success => SAT')
    return True