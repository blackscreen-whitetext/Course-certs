import abc

# this class characterizes an automaton
class FSA:
    def __init__ (self, numStates = 0, startStates=None, finalStates=None, alphabetTransitions=None) :
        self.numStates = numStates
        self.startStates = startStates
        self.finalStates = finalStates
        self.alphabetTransitions = alphabetTransitions

class NFA(FSA):
    def simulate(self, ipStr):
        S = set(self.startStates)
        newS = set()
        for i in range(len(ipStr)):
            symbol = ipStr[i]
            tm = self.alphabetTransitions[symbol]
            for state in S:
                trs = tm[state]
                for tr in range(len(trs)):
                    if trs[tr] == 1:
                        newS.add(tr)
            S = set(newS)
            newS = set()
        if len(self.finalStates) > 0 and not S.isdisjoint(self.finalStates):
            print("String Accepted")
            return True
        else:
            print("String Rejected")
            return False

    def getNFA(self):
        return self

class ETree:
    root = None
    nfa = None
    class ETNode:
        def __init__(self, val=" ", left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    def compute(self, operands, operators):
            operator = operators.pop()
            if operator == "*":
                left = operands.pop()
                operands.append(self.ETNode(val=operator, left=left))
            elif operator == "+":
                right, left = operands.pop(), operands.pop()
                operands.append(self.ETNode(val=operator, left=left, right=right))
            elif operator == ".":
                right, left = operands.pop(), operands.pop()
                operands.append(self.ETNode(val=operator, left=left, right=right))

    def parseRegex(self, regex):
        operands, operators = [], []
        for i in range(len(regex)):
            if regex[i].isalpha():
                operands.append(self.ETNode(val=regex[i]))
            elif regex[i] == '(':
                operators.append(regex[i])
            elif regex[i] == ')':
                while operators[-1] != '(':
                    self.compute(operands, operators)
                operators.pop()
            else :
                operators.append(regex[i])
        while operators:
            self.compute(operands, operators)

        if len(operators) == 0:
            self.root = operands[-1]
        else :
            print("Parsing Regex failed.")

    def getTree(self):
        return self.root

    ###################################################################
    # IMPLEMENTATION STARTS AFTER THE COMMENT
    # Implement the following functions

    # In the below functions to be implemented delete the pass statement
    # and implement the functions. You may define more functions according
    # to your need.
    ###################################################################
    # .
    def operatorDot(self, fsaX, fsaY):
        # make start states as those of X and final those of y
        numStates = fsaX.numStates + fsaY.numStates
        startStates = fsaX.startStates
        finalStates = set([fsaX.numStates + state for state in fsaY.finalStates])
        #check for acceptance of empty string by X
        if not fsaX.startStates.isdisjoint(fsaX.finalStates):
            startStates = fsaX.startStates.union(set([state + fsaX.numStates for state in fsaY.startStates]))
        #preserve old transitions
        alphabetTransitions = {letter : [(fsaX.alphabetTransitions[letter][i]+[0 for j in range(fsaY.numStates)]) for i in range(fsaX.numStates)]+[([0 for j in range(fsaX.numStates)]+fsaY.alphabetTransitions[letter][i]) for i in range(fsaY.numStates)] for letter in "abc"}
        #add transitions from those pre final X states to start states of Y
        for letter in "abc":
            transitionMatrix = alphabetTransitions[letter]
            for j in range(fsaX.numStates):
                for state in fsaX.finalStates:
                    if transitionMatrix[j][state] == 1:
                        for state_y in fsaY.startStates:
                            transitionMatrix[j][state_y+fsaX.numStates] = 1
            alphabetTransitions[letter] = transitionMatrix
        return FSA(numStates, startStates, finalStates, alphabetTransitions)
    # +
    def operatorPlus(self, fsaX, fsaY):
        #Just 2 separate automata working parallely
        numStates = fsaX.numStates + fsaY.numStates
        startStates = fsaX.startStates.union(set([state + fsaX.numStates for state in fsaY.startStates]))
        finalStates = fsaX.finalStates.union(set([state + fsaX.numStates for state in fsaY.finalStates]))
        alphabetTransitions = {letter : [(fsaX.alphabetTransitions[letter][i]+[0 for j in range(fsaY.numStates)]) for i in range(fsaX.numStates)]+[([0 for j in range(fsaX.numStates)]+fsaY.alphabetTransitions[letter][i]) for i in range(fsaY.numStates)] for letter in "abc"}
        return FSA(numStates, startStates, finalStates, alphabetTransitions)
    # *
    def operatorStar(self, fsaX):
        #Glushkov's construction with the fusion step skipped(Any start to fina transition in old fsa becomes self loop)
        numStates = fsaX.numStates + 1 # Adding 1 extra state that is the start and final state of result fsa
        startStates = {numStates-1}
        finalStates = {numStates-1}
        alphabetTransitions = {letter: [fsaX.alphabetTransitions[letter][i]+[0]for i in range(fsaX.numStates)]+[[0 for j in range(numStates)]] for letter in "abc"}
        for letter in "abc":
            transitionMatrix = alphabetTransitions[letter]
            for j in range(numStates-1):
                for state in fsaX.startStates: # Add corresponding transitions from the new state to some other state if there is a same transition from some old starting states to that state 
                    if transitionMatrix[state][j] == 1:
                        transitionMatrix[-1][j] = 1
                        if j in fsaX.finalStates: #Self Loops
                            transitionMatrix[-1][-1] = 1
                for state in fsaX.finalStates: #Add corresponding transitions from states to the new state if there is that transition from that state to any of the old final states 
                    if transitionMatrix[j][state] == 1:
                        transitionMatrix[j][-1] = 1
            print(transitionMatrix)
            alphabetTransitions[letter] = transitionMatrix  
        return FSA(numStates, startStates, finalStates, alphabetTransitions)
                
            
    # a, b, c and e for epsilon
    def alphabet(self, symbol):
        #Simple 1 or 2 state FSA accepting just that particular alphabet only or only the empty string
        if symbol == 'e':
            return FSA(1, {0}, {0}, {letter : [[0]] for letter in "abc"})
        return FSA(2, {0}, {1}, {symbol : [[0, 1], [0, 0]]}|{letter:[[0,0],[0,0]] for letter in "abc" if letter != symbol})
        

    # Traverse the regular expression tree(ETree)
    # calling functions on each node and hence
    # building the automaton for the regular
    # expression at the root.
    
    def recursiveFSA(self, root):
        #To traverse the expression tree and build the automata
        if root.val == '.':
            return self.operatorDot(self.recursiveFSA(root.left), self.recursiveFSA(root.right))
        elif root.val == '+':
            return self.operatorPlus(self.recursiveFSA(root.left), self.recursiveFSA(root.right))
        elif root.val == '*':
            return self.operatorStar(self.recursiveFSA(root.left))
        else:
            return self.alphabet(root.val)
    def buildNFA(self, root):
        if root == None:
            print("Tree not available")
            exit(0)

        numStates = 0
        initialState = set()
        finalStates = set()
        transitions = {}

        # write code to populate the above datastructures for a regex tree
        fsa = self.recursiveFSA(root)
        numStates,initialState,finalStates,transitions = fsa.numStates,fsa.startStates,fsa.finalStates,fsa.alphabetTransitions
        self.nfa = NFA(numStates, initialState, finalStates, transitions)

        # print NFA

        return self.nfa

    ######################################################################
