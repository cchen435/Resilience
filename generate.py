#!/usr/bin/env python

from optparse import OptionParser
import sys

'''
this script generates the faults to be injected
'''


'''
argument callback function
'''
def vararg_callback(option, opt, value, parser):
	setattr(parser.values, option.dest, value.split(','))


if __name__ == "__main__":

	usage = "usage: %prog -t stepname,stepval -r steprange -v variables[,], -b breakpoint, -e entrypoint"
	
	parser = OptionParser(usage=usage)
	parser.add_option('-t', '--timestep', type='string', dest='step',
					action='callback', help="timestep var", callback=vararg_callback);
	parser.add_option('-r', '--range', type='int', dest='range',
					help="timestep range");
	parser.add_option('-v', '--target', type='string', dest='vars',
					action='callback', help="variables to inject faults",
				   	callback=vararg_callback);
	parser.add_option('-e', '--entry', type='string', dest='entry',
					help="entry point where timestep variable defined");
	parser.add_option('-b', '--breakpoint', type='string', dest='point',
					help="break point where target variable accessed");
	parser.add_option('-o', '--output', type='string', dest='file',
					help="output file name");
	parser.add_option('-f', '--fault', type='string', dest='fault',
					help="fault");
    
	(opts, args) = parser.parse_args()
	opts = vars(opts)

	if None in opts.values():
		parser.print_help()
		sys.exit(-1)

	step_name = opts['step'][0]
	step_vals = opts['step'][1:]
	r		  = opts['range']
	variables = opts['vars']
	entry     = opts['entry']
	point 	  = opts['point']
	fname	  = opts['file']
	fault	  = opts['fault']

	try:
		fh = open(fname, 'w')
	except:
		print 'failed to open file'
		sys.exit(1)

	print 'vars:', variables
	print 'steps:', step_vals	
	for var in variables:
		if len(var) == 0:
			continue
		for step in step_vals:
			if len(step) == 0:
				continue
			
			record='; '.join([entry, step_name, step, var, point, fault]);
			s = str(record);
			s=s.lstrip('(').rstrip(')') + '\n';
			
			print 'record:', s, 'len(step)', len(step)
			fh.write(s);

	fh.close()



