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
    trail_level = 0                             # number of decisions
    trail = []                                  # tuples (implied literal, justification)
    state(trail, clauses)

    # Truth values and VSIDS initialization
    truth_values = {lit:[None, 0] for lit in literals}

    # watch 2 literals for each clause(if possible)
    for clause in clauses:
        watched = 0
        for idx,char in enumerate(clause[0]):
            if char.isalpha():
                if clause[0][idx-1] == '¬':
                    clause[2][watched] = '¬' + char
                else:
                    clause[2][watched] = char

                watched += 1

            if watched == 2:
                break;
    
    # CDCL procedure: start
    clause = check_propagation(clauses, truth_values)
    while True:
        conflict = False
        propagated = False

        #CDCL procedure: propagation
        while clause is not None:
            propagated = True

            # implied literal becomes 1(True)
            implied_literal = clauses[clause][2][0]
            truth_values[implied_literal][0] = 1

            if '¬' in implied_literal:
                negated = implied_literal[1]
            else: 
                negated = '¬' + implied_literal
                
            # if negation of the implied_literal exists set it to 0(False)
            if negated in truth_values.keys():
                truth_values[negated][0] = 0

            reason = clauses[clause][0]
            trail.append((clauses[clause][2][0], reason))    # (implied_literal, reason)
            print(' ⇒ propagation ⇒ ', end='')
            state(trail, clauses)

            #check conflict 
            conflict, cc = check_conflict(clauses, negated, truth_values)

            if conflict:
                cc = clauses[cc][0]
                break;
            
            clauses = cc
            clause = check_propagation(clauses, truth_values)

        #CDCL procedure: decision
        if not propagated:
            lit = ''
            for lit in truth_values.keys():
                if truth_values[lit][0] == None:
                    truth_values[lit][0] = 1
                    
                    if '¬' in lit:
                        negated = lit[1]
                    else:
                        negated = '¬' + lit

                    if negated in truth_values.keys():
                        truth_values[negated][0] = 0
                        conflict, cc = check_conflict(clauses, negated, truth_values)

                    if conflict:
                        cc = clauses[cc][0]
                    break

            trail.append((lit, None))
            print(' ⇒ decision ⇒ ', end='')
            state(trail, clauses, learned_clauses = learned_clauses)
            trail_level += 1

            # VSIDS decision
            max_score = max(truth_values.)
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



        if conflict:
            print(' ⇒ conflict ⇒ ', end='')
            state(trail, clauses, learned_clauses = learned_clauses, conflict_clause = cc)
            if trail_level == 0:
                return fail(), None

            # 1 Explain 
            learn = explain(clauses, trail, cc)
            print(' ⇒ explain ⇒ ', end='')
            if learn is None:
                state(trail, clauses, learned_clauses= learned_clauses, conflict_clause= '□')
                return fail(), None
            
            state(trail, clauses, learned_clauses= learned_clauses, conflict_clause= learn)
            
            # 2 Learn
            if learn not in learned_clauses:
                learned_clauses.append(learn)

            checklist = [clause[0] for clause in clauses]
            if learn not in checklist:
                literals = 0
                for char in learn:
                    if char.isalpha():
                        literals += 1

                for idx,el in enumerate(clauses):
                    if el[1] >= literals:
                        clauses.insert(idx, [learn, literals, [None, None]])
                        break
                    elif idx == len(clauses)-1:
                        clauses.append([learn, literals, [None, None]])
                        break
                
                #clauses.insert(0, [learn, 1, [learn, None]])

            print(' ⇒ learn ⇒ ', end='')
            state(trail, clauses, learned_clauses= learned_clauses, conflict_clause= learn)
            
            # 3 Backjump
            # remove all trail steps until the first decision
            undo = []
            while True:
                lit = trail.pop() 
                undo.append(lit)
                if lit[1] == None:
                    break
            
            # undo all the steps
            for step in undo:
                literal = step[0]

                if '¬' in literal:
                    negated = literal[1]
                else:
                    negated = '¬' + literal
                
                truth_values[literal][0] = None
                if negated in truth_values.keys():
                    truth_values[negated][0] = None
                
            trail_level -= 1

            # make true the learned clause
            CHECK IF NEEDED
            if len(learn) == 1 or len(learn) == 2:
                trail.append((learn, learn))
                truth_values[learn][0] = 1

                if '¬' in learn:
                    negated = learn[1]
                else:
                    negated = '¬' + learn

                if negated in truth_values.keys():
                    truth_values[negated][0] = 0


            print(' ⇒ backjump ⇒ ', end='')
            state(trail, clauses, learned_clauses= learned_clauses)
        else:
            #check if all clauses are satisfied
            if None not in truth_values.values():
                return success(), truth_values
            
            clause = check_propagation(clauses, truth_values)



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
        if clause[2][1] is None:
            if truth_values[clause[2][0]][0] is None:
                #implied literal
                return idx
    
    return None


def check_conflict(clauses, negated_literal, truth_values):
    '''
    Checks the watched literals and acts accordingly:
        - both are not false, do nothing
        - one false: look for another literal in the clause
        - both false: look for two implied literals

    :reutrn: true if conflict, false otherwise
    '''

    for idx,clause in enumerate(clauses):
        if negated_literal in clause[2]:
            #search another literal
            if clause[1] != 1:
                new_watched = search_watched_literal(clause, truth_values)
            else:
                new_watched = [None, None]

            if new_watched[0] == None and new_watched[1] == None:
                # found 0: conflict clause try to solve
                return True, idx

            clause[2] = new_watched

    return False, clauses


def search_watched_literal(clause, truth_values):
    '''
    Searches another not false literal in the clause:

    :returns: two watched literals, one implied literal or None
    '''
    watched = [clause[2][0], clause[2][1]]

    def search():
        '''
        Looks for another literal that is not false 

        :returns: literal or None
        '''

        for idx,char in enumerate(clause[0]):
            if char.isalpha():
                if clause[0][idx-1] == '¬':
                    if truth_values['¬'+char][0] != 0 and '¬'+char not in watched:
                        return '¬'+char
                else:
                    if truth_values[char][0] != 0 and char not in watched:
                        return char
        
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


def explain(clauses, trail, conflict_clause):
    '''
    Transforms the conflict clause into an 
    assertion clause (i.e. cc where only one literal is false)
    
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
        conflict_clause = reduce(conflict_clause)

    conflict_clause = reduce(conflict_clause)
    print(conflict_clause)
    print("\n")
    return conflict_clause


def reduce(clause):
    '''
    eliminates literal duplicates from the clause
    
    :returns: clause without duplicates
    '''

    reduced = True
    while reduced:
        reduced = False
        for idx,char in enumerate(clause):
            if char.isalpha():
                if clause[idx-1] == '¬':
                    lit = '¬' + char
                else:
                    lit = char

                #remove duplicates
                bkp = len(clause)
                clause = clause[:idx+1] + clause[idx+1:].replace('∨'+lit, '')
                if bkp != len(clause):
                    reduced = True
                    break;

                CHECK TAUTOLOGIES
                #remove tautologies
                #if '∨'+lit in clause:

    return clause


def fail():
    '''
    The resolution steps lead to a failure.
    The set of clauses is unsatisfiable

    :returns: False(UNSAT)
    '''

    print(' ⇒ fail ⇒ UNSAT')
    return False

def success():
    '''
    The resolution steps lead to a success.
    The set of clauses is satisfiable

    :returns: True(SAT)
    '''

    print(' ⇒ success ⇒ SAT')
    return True