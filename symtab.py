#!/usr/bin/env python

'''
this script is to get the symbol info 
using readelf tools
'''

import os
import getopt
import sys
import subprocess
import re

symbol = None


def symtab( target ):
	infocmd = 'readelf --debug-dump=info ' + target;
	abbrevcmd = 'readelf --debug-dump=abbrev ' + target;

	debug_info = os.popen(infocmd).read().split('\n');
	debug_abbrev = os.popen(abbrevcmd).read().split('\n');

	'''
	print "info:"
	print debug_info;

	print "\n\nabbrev:"
	print debug_abbrev;
	'''

	'''
	for line in debug_info:
		if line.find("DW_TAG") != -1:
			print line;
	'''
	for line in debug_info:
		if re.search("DW_TAG", line): # the line indicates begin of a new tag
			print line

			# extract the type e.g DW_TAG_Variable
			attr = re.findall('\((\S+)\)', line);
			
			# get abbrev nunmber
			abbrN = re.findall('Abbrev Number: ([0-9]+)', line);
			print attr, abbrN

			if attr[0] == 'DW_TAG_variable':
				print 'handle variable', attr[0]
			elif attr[0] == 'DW_TAG_subprogram':
				print 'handle subprogram', attr[0]
			else:
				print attr[0], "Not handled"
			print ''

# code used for testing
def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
	except getopt.error, msg:
		print msg
		sys.exit(2)

	if len(args) ==0 or len(args) > 1 :
		print "Usage:", sys.argv[0], "target";
		sys.exit(2)

	print args
	symtab(args[0]);

if __name__ == "__main__":
	main()

