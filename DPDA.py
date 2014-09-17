#!/usr/bin/env python

# Nicholas LaRosa
# CSE 30151
# Project 2

import os
import sys

class DPDA:
	
	def __init__(self, name):					# represents a complete NFA definition
		
		self.name = name
		self.states = list()					# Q
		self.inputAlphabet = list()				# Sigma
		self.stackAlphabet = list()				# Gamma
		self.transitions = list()				# Transitions
		self.startState = ""					# q0
		self.acceptStates = list()				# F

	def getName(self):
		
		return self.name

	def processFile(self, fileName):			# file will be processed for NFA definition
		
		file = open(fileName)
		lines = file.readlines()				# lines array contains entire file

		for line in lines:
		
			if line[0] == 'A':
		
				if self.addInputAlphabet(line.rstrip()) == 0:

					return 0
		
			elif line[0] == 'Z':
			
				if self.addStackAlphabet(line.rstrip()) == 0:

					return 0
			
			elif line[0] == 'Q':
			
				if self.addStates(line.rstrip()) == 0:

					return 0
		
			elif line[0] == 'T':
		
				if self.addTransition(line.rstrip()) == 0:

					return 0
		
			elif line[0] == 'S':
		
				if self.addStartState(line.rstrip()) == 0:

					return 0
		
			elif line[0] == 'F':
		
				if self.addAcceptStates(line.rstrip()) == 0:

					return 0
		
			else:
		
				print('State syntax: "Q:" followed by comma-separated states.')
				print('Input Alphabet syntax: "A:" followed by comma-separated symbols.')
				print('Stack Alphabet syntax: "Z:" followed by comma-separated symbols.')
				print('Transition syntax: "T:" followed by comma-separated start state, input, top stack element to be popped, resulting state, and symbol to be written to stack.')
				print('Start state syntax: "S:" followed by a state.')
				print('Accept state syntax: "F:" followed by comma-separated states.')
				return 0

		if self.testTransitions() == 1:

			return 1

		else:

			return 0

	def getInput(self):							# process a single set of tape input
		
		if len(self.states) == 0:
		
			print('Establish state list via addStates().')
			return 0
		
		if len(self.inputAlphabet) == 0:
		
			print('Establish input alphabet via addInputAlphabet().')
			return 0
		
		if len(self.stackAlphabet) == 0:
		
			print('Establish stack alphabet via addStackAlphabet().')
		
		if len(self.transitions) == 0:
		
			print('Establish transition rules via addTransition().')
			return 0
		
		if len(self.startState) == 0:
		
			print('Establish start state via addStartState().')
			return 0
		
		if len(self.acceptStates) == 0:
		
			print('Establish accept state list via addAcceptStates().')
			return 0

		line = sys.stdin.readline()

		try:
		
			line = int(line)					# confirm first line as integer
		
		except ValueError:
		
			print('Invalid input tape declaration.')
			print('First line in an input tape is an integer representing the number of following tape lines.')
			return 0

		output = ''								# string will be built containing output
		
		for lineNum in range(line):
			
			line = sys.stdin.readline()
			newOutput = self.processInputLine(line.rstrip())
		
			if newOutput != '':
		
				output = output + newOutput
		
			else:
	
				return 0
		
			output = output + '\n'
		
		sys.stdout.write( output )

	def processInputLine(self, inputString):	# each input line results in state listing
	
		currState = self.startState
		transitionTaken = self.transitions[0]	# each input will result in a transition b/c of DPDA
		stack = list()

		inputs = inputString.split(',')
		
		for i in range( len( inputs ) ):

			if inputs[i] == '':

				inputs.pop( i )

		output = ''

		done = 0
		transitionFound = 0

		while( done == 0 ):					# each state has a destination because this is a DPDA

			if len( inputs ) == 0:

				done = 1

			emptyTransition = self.transitionOnEmpty( currState, stack )	# begin by checking if transition on empty input occurs
			transitionFound = 1							# transition found on input (assume true)

			if emptyTransition[ 'taken' ] == 'yes':		# we have an empty transition

				transitionTaken = emptyTransition	

			elif len( inputs ) > 0:									# search for a transition on given input

				transitionFound = 0									# we need to find a transition on this input, or else we will reject (because there was no empty transition)
				input = inputs.pop(0)

				for transition in self.transitions:

					if transition[ 'startState' ] == currState:		# deal with transitions only on this state

						if transition[ 'inputSymbol' ] == input or transition[ 'inputSymbol' ] == 'e':	# transition is defined for input symbol
		
							if ( len( stack ) > 0 and transition[ 'stackSymbolPop' ] == stack[-1] ) or transition[ 'stackSymbolPop' ] == 'e':		# stack symbol to be popped is present

								transitionFound = 1
								transitionTaken = transition	
								break											# we can stop once we have found result b/c DPDA
	
			else:										# no inputs left, no empty transition

				transitionFound = 0
	
			if transitionFound == 0:					# did not find a transition on input, exit

				break

			if len( stack ) > 0:						# we now have the taken transition, pop from stack

				if stack[-1] == transitionTaken[ 'stackSymbolPop' ]:			# top of stack should be popped

					stack.pop()

			if transitionTaken[ 'stackSymbolPush' ] != 'e':		# and then push to stack

				stack.append( transitionTaken[ 'stackSymbolPush' ] )
	
			currState = transitionTaken[ 'resultState' ]

			output = output + transitionTaken[ 'startState' ] + '; ' + transitionTaken[ 'inputSymbol' ] + '; ' + transitionTaken[ 'stackSymbolPop' ] + '; '
			output = output + transitionTaken[ 'resultState' ] + '; ' 

			stack.reverse()			# temporarily reverse stack for printing

			for j in range( len( stack ) ):
				
				if j == len( stack ) - 1:			# no comma after last

					output = output + stack[j]
					break

				output = output + stack[j] + ','
			
			stack.reverse()			# stack back to correct order
			output = output + '\n'

		if transitionFound == 0:					# this occurs only when no transition is found on an input (ie. could not transition on input and stopped)

			output = output + 'REJECT' + '\n'

		elif transitionTaken[ 'resultState' ] in self.acceptStates:

			output = output + 'ACCEPT' + '\n'
		
		else:

			output = output + 'REJECT' + '\n'

		return output

	def transitionOnEmpty(self, state, stack):				# transition from given state on empty input

		transitionTaken = { 'taken': 'no' }

		for transition in self.transitions:

			if transition[ 'startState' ] == state:

				if transition[ 'inputSymbol' ] == 'e':		# empty input

					if ( len( stack ) > 0 and transition[ 'stackSymbolPop' ] == stack[-1] ) or transition[ 'stackSymbolPop' ] == 'e':		# top of stack matches (or doesn't pop)

						transitionTaken = transition
						transitionTaken[ 'taken' ] = 'yes'				# indicate to read transition
						break

					else:

						transitionTaken[ 'taken' ] = 'no'				# indicate to ignore the return
						break
	
		return transitionTaken 

	def addStates(self, stateString):				# format - Q;q1,q2,q3...
		
		if stateString[0] != 'Q':
		
			print('State syntax: "Q:" followed by comma-separated states.')
			return 0
		
		else:
		
			states = stateString[2:].split(',')
		
			for state in states:
		
				self.states.append(state)
		
			return 1

	def addInputAlphabet(self, alphabetString):		# format - A:0,1...
		
		if alphabetString[0] != 'A':
		
			print('Input alphabet syntax: "A:" followed by comma-separated symbols.')
			return 0
		
		else:
		
			symbols = alphabetString[2:].split(',')
		
			for symbol in symbols:

				self.inputAlphabet.append(symbol)
		
			return 1

	def addStackAlphabet(self, alphabetString):		# format - Z:0,1...
			
		if alphabetString[0] != 'Z':
			
			print('Stack alphabet syntax: "Z:" followed by comma-separated symbols.')
			return 0
		
		else:
		
			symbols = alphabetString[2:].split(',')
		
			for symbol in symbols:
		
				self.stackAlphabet.append(symbol)
		
			return 1

	def addTransition(self, transitionString):
		
		if transitionString[0] != 'T':
			
			print('Transition syntax: "T:" followed by comma-separated start state, input, top stack element to be popped, resulting state, and symbol to be written to stack.')
			return 0
		
		elif len(self.states) == 0 or len(self.inputAlphabet) == 0 or len(self.stackAlphabet) == 0:	# alphabet and state list must be established
		
			print('Establish input alphabet, stack alphabet and states via addInputAlphabet(), addStackAlphabet() and addStates(), respectively.')
			return 0
		
		else:
			
			transition = transitionString[2:].split(',')								# just get the 5 states/symbols
	
			if len(transition) != 5:
				
				print('Transition syntax: "T:" followed by comma-separated start state, input, top stack element to be popped, resulting state, and symbol to be written to stack.')
				return 0
			
			elif transition[0] in self.states and ( transition[1] in self.inputAlphabet or transition[1] == 'e' ) and \
					( transition[2] in self.stackAlphabet or transition[2] == 'e' ) and transition[3] in self.states and \
					( transition[4] in self.stackAlphabet or transition[4] == 'e' ):

				currTransition = {}														# each transition represented by dictionary

				try:

					currTransition[ 'startState' ] = transition[0]
					currTransition[ 'inputSymbol' ] = transition[1]
					currTransition[ 'stackSymbolPop' ] = transition[2]
					currTransition[ 'resultState' ] = transition[3]
					currTransition[ 'stackSymbolPush' ] = transition[4]

					self.transitions.append( currTransition )

				except Exception as ex:

					print 'addTransition() error: ' + str( ex )
					return 0


			else:

				print('Establish input alphabet, stack alphabet and states via addInputAlphabet(), addStackAlphabet() and addStates(), respectively.')
				return 0

	def addStartState(self, startString):
	
		if startString[0] != 'S':
	
			print('Start state syntax: "S:" followed by a state.')
			return 0
	
		else:
	
			start = startString[2:].split(',')
	
			if len(start) != 1:
		
				print('Only one start state allowed per NFA.')
				return 0
	
			elif start[0] in self.states:
	
				self.startState = start[0]
				return 1
	
			else:
	
				print('Establish state list via addStates().')
				return 0

	def addAcceptStates(self, acceptString):
		
		if acceptString[0] != 'F':
		
			print('Accept state syntax: "F:" followed by comma-separated states.')
			return 0
		
		else:
		
			accepts = acceptString[2:].split(',')
		
			for accept in accepts:
		
				if accept in self.states:
		
					self.acceptStates.append(accept)
		
				else:
		
					print('Establish state list via addStates().')
					return 0
		
			return 1

	# TRANSITION HELPERS

	def printRule( self, ruleNum ):							# print specific DPDA rule

		if ruleNum == 1:

			print( '\n\tRule #1: at most one transition on a given input character and stack character.' )

		elif ruleNum == 2:

			print( '\n\tRule #2: if a transition doesn\'t read the stack, all others cannot' )
			print( '\tread (the stack but not input) and other transitions cannot read the' )
			print( '\tsame input and the stack.\n' )

		elif ruleNum == 3:

			print( '\n\tRule #3: if a transition reads the stack but not input, other' )
			print( '\ttransitions cannot read (input but not stack) and other transitions' )
			print( '\tthat read the same stack symbol cannot read input.\n' )

		elif ruleNum == 4:

			print( '\n\tRule #4: if a transition reads no input and no stack, no other transitions' )
			print( '\tare allowed.\n' )

		else:

			print( '\n\tRule N/A.\n' )

	def testTransitions( self ):

		self.removeDuplicateTransitions()					# duplicates will trigger a failure

		for transition in self.transitions:					# test all transitions

			ruleNum = self.isValidTransition( transition )

			if ruleNum != 0: 								# invalid transition

				print( 'Following transition fails DPDA rule ' + str( ruleNum ) + ':' )
				print( transition )
				self.printRule( ruleNum )
				return 0

		return 1

	def removeDuplicateTransitions( self ):

		for i in range( len( self.transitions ) ):

			for j in range( len( self.transitions ) ):

				if i == j:					# do not compare to itself

					continue

				else:

					if self.transitions[i] == self.transitions[j]:		# duplicate

						self.transitions.pop( i )						# remove

	'''
	def isSameTransition(self, transition1, transition2):	# compare two transitions to avoid false positive
	
		return 	transition1[ 'startState' ] == transition2[ 'startState' ] and \
					transition1[ 'resultState' ] == transition2[ 'resultState' ] and \
						transition1[ 'inputSymbol' ] == transition2[ 'inputSymbol' ] and \
							transition1[ 'stackSymbolPop' ] == transition2[ 'stackSymbolPop' ] and \
								transition1[ 'stackSymbolPush' ] == transition2[ 'stackSymbolPush' ] 
	'''

	def isValidTransition(self, testTransition):	# will return 1 if valid transition according to DPDA rules (must pass all four)

		return self.testDPDA_Rule1( testTransition ) or self.testDPDA_Rule2( testTransition ) or self.testDPDA_Rule3( testTransition ) or self.testDPDA_Rule4( testTransition )

	def testDPDA_Rule1(self, testTransition):	# rule #1: at most one transition on a given input character and stack character

		for transition in self.transitions:

			if transition == testTransition:	# do not compare a transition to itself

				continue

			if transition[ 'startState' ] == testTransition[ 'startState' ]:			# compare transitions on same states

				if transition[ 'inputSymbol' ] == testTransition[ 'inputSymbol' ]:

					if transition[ 'stackSymbolPop' ] == testTransition[ 'stackSymbolPop' ]:

						#print( 'Fails rule 1.' )
						return 1														# same inputSymbol and stackSymbol

		return 0

	def testDPDA_Rule2(self, testTransition):	# rule #2: if a transition doesn't read the stack, all others cannot read (the stack but not input)
												# and other transitions cannot read the same input and the stack
		
		if testTransition[ 'stackSymbolPop' ] == 'e':

			for transition in self.transitions:

				if transition == testTransition:	# do not compare a transition to itself

					continue
	
				if transition[ 'startState' ] == testTransition[ 'startState' ]:		# compare transitions on same states

					if transition[ 'stackSymbolPop' ] != 'e':										# reads stack

						if transition[ 'inputSymbol' ] == 'e' or transition[ 'inputSymbol' ] == testTransition[ 'inputSymbol' ]:	# not input or same input

							#print( 'Fails rule 2.' )
							return 2

		return 0

	def testDPDA_Rule3(self, testTransition):	# rule #3: if a transition reads the stack but not input, other transitions cannot read (input but not stack)
												# and other transitions that read the same stack symbol cannot read input
		
		if testTransition[ 'stackSymbolPop' ] != 'e' and testTransition[ 'inputSymbol' ] == 'e':	# stack but not input

			for transition in self.transitions:

				if transition == testTransition:	# do not compare a transition to itself

					continue

				if transition[ 'startState' ] == testTransition[ 'startState' ]:		# compare transitions on same states

					if transition[ 'inputSymbol' ] != 'e':											# reads input

						if transition[ 'stackSymbolPop' ] == 'e' or transition[ 'stackSymbolPop' ] == testTransition[ 'stackSymbolPop' ]:	# not stack or same stack

							#print( 'Fails rule 3.' )
							return 3

		return 0

	def testDPDA_Rule4(self, testTransition):	# rule #4: if a transition reads no input and no stack, no other transitions are allowed

		if testTransition[ 'inputSymbol' ] == 'e' and testTransition[ 'stackSymbolPop' ] == 'e':

			for transition in self.transitions:

				if transition == testTransition:	# do not compare a transition to itself

					continue

				if transition[ 'startState' ] == testTransition[ 'startState' ]:		# compare transitions on same states

					#print( 'Fails rule 4.' )
					return 4

		return 0

	# PRINT FUNCTIONS

	def printDescription(self):

		return self.printStates() and self.printInputAlphabet() and self.printStackAlphabet() and self.printTransitions() and self.printStartState() and self.printAcceptStates()

	def printInputAlphabet(self):
	
		if len(self.inputAlphabet) == 0:
	
			print('Establish input alphabet via addInputAlphabet().')
			return 0
	
		else:
	
			sys.stdout.write('A:')
	
			for symbol in self.inputAlphabet[:-1]:
	
				sys.stdout.write(symbol)
				sys.stdout.write(',')
	
			sys.stdout.write(self.inputAlphabet[-1])
			sys.stdout.write('\n')
	
			return 1

	def printStackAlphabet(self):
	
		if len(self.stackAlphabet) == 0:
	
			print('Establish stack alphabet via addStackAlphabet().')
			return 0
	
		else:
	
			sys.stdout.write('Z:')
	
			for symbol in self.stackAlphabet[:-1]:
	
				sys.stdout.write(symbol)
				sys.stdout.write(',')
	
			sys.stdout.write(self.stackAlphabet[-1])
			sys.stdout.write('\n')
	
			return 1

	def printStates(self):
	
		if len(self.states) == 0:
	
			 print('Establish state list via addStates().')
			 return 0
	
	 	else:
			
			sys.stdout.write('Q:')
		
			for state in self.states[:-1]:
		
				sys.stdout.write(state)
				sys.stdout.write(',')
		
			sys.stdout.write(self.states[-1])
			sys.stdout.write('\n')
		
			return 1

	def printTransitions(self):
		
		if len(self.transitions) == 0:
		
			print('Establish new transition rule via addTransition().')
			return 0
		
		else:
		
			for transition in self.transitions:
	
				sys.stdout.write( 'T:' + transition[ 'startState'] + ',' + transition[ 'inputSymbol' ] + ',' + transition[ 'stackSymbolPop' ] + ',' )
				sys.stdout.write( transition[ 'resultState' ] + ',' + transition[ 'stackSymbolPush' ] + '\n')
	
			return 1
		
	def printStartState(self):
	
		if self.startState == "":
	
			print('Establish start state via addStartState().')
			return 0
	
		else:
	
			sys.stdout.write('S:' + self.startState + '\n')
			return 1

	def printAcceptStates(self):
	
		if len(self.acceptStates) == 0:
	
			print('Establish accept states via addAcceptStates().')
			return 0
	
		else:
	
			sys.stdout.write('F:')
	
			for state in self.acceptStates[:-1]:
	
				sys.stdout.write(state)
				sys.stdout.write(',')
	
			sys.stdout.write(self.states[-1])
			sys.stdout.write('\n')
			return 1

