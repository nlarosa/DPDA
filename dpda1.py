#!/usr/bin/python

# Nicholas LaRosa
# CSE 30151
# Project 2

import sys
import re
import os
import math
from DPDA import DPDA

if len(sys.argv) != 2:
	raise Exception('Usage: dpda.py <nfa_description>\n')

location = sys.argv[1]

ourDPDA = DPDA( 'dpda' )

if ourDPDA.processFile( location ) == 1:

	ourDPDA.getInput()

