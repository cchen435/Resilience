#!/usr/bin/env python

import subprocess as sp
from optparse import OptionParser
import sys
import re
import time
import os

'''
this script implement an injector using gdb
'''

'''
init: create a gdb subprocess to debug the 
	target. target is an executable, args is 
	a list of arguments (inputs) required to 
	execute the target
'''
def init(target, args):
	# starting GDB to debug the target
	print 'target:', target
	print 'cmd', ['gdb', '--args', target] + args
	p = sp.Popen(['gdb', '--args', target] + args, 
					stdin=sp.PIPE);
	
	return p;

def finish(proc):
	print 'quit gdb'
	proc.stdin.write('quit\n');	
	proc.wait();

'''
read_file: read faults config from file, file contents should
	follow some formats:
	(entry), (step_name), (step_val), (mem), (point), (fault)
'''
def read_file(filename):
	faults = list()
	fault = dict()
	step = dict()
	try:
		handler = open(filename, 'r')
	except:
		print 'open file error'
		sys.exit(1)
	
	for line in handler:
		tmp = line.strip().split(',')
		fault['entry'] = tmp[0];
		step['name'] = tmp[1];
		step['val'] = tmp[2];
		fault['step'] = step;
		fault['mem'] = tmp[3];
		fault['point'] = tmp[4];
		fault['fault'] = tmp[5];

		faults.append(fault);

	handler.close()
	return faults



''' inject a falt to process proc, 
	params is a dict with variables 
	including fault location and fault ratio
	params = {'step':{'name':'istep', 'val':'20'}, 'fault': '0.5', 
			'point': 'file:line or func', 'mem':'p->a->d[20]', 
			'entry':'func or file:line' }
	point is reserved for break...if command, currently using watch cmd so not 
	need it

	entry is for the scope where time step varialbe is defined, default is main
'''
def inject(proc, params):
	
	try:
		# indicating inject a fault at which time step, int type 
		step_name = params['step']['name'];
		step_val = params['step']['val'];

		# fault ratio, double type 
		fault = params['fault'];
		# break at which file and line, "filename:line", string type
		point = params['point'];
		# target where the fault should be injected.
		var = params['mem'];
		# executable file
		entry = params['entry'];
	except:
		print 'maybe param is not correct: ', params
		sys.exit(1)


	# set the first breakpoint where time step varialbe is defined
	cmd = ' '.join(['b', str(entry)]) + '\nr\n';	
	proc.stdin.write(cmd)

	# setup the watchpoint for timestep varialbe
	# a more general way could be using break ... if, if
    # the target is not defined in the function where mainloop is	
	
	cmd = 'watch ' + step_name + '==' + step_val + '\n'
	proc.stdin.write(cmd)
	proc.stdin.flush()

	# continue exec until the expired timestep
	proc.stdin.write('c\n')	
	proc.stdin.flush()

	# inject the faults to target memory. 
	# to-do: get the value first, then add fault, then write value back
	# need to using pipe to read the output.
	
	print '\n\n*************** injecting a fault to %s **************'%(var)
	cmd = 'print ' + var + '\n'
	print 'value before injection:'
   	proc.stdin.write(cmd);


	cmd = 'set ' + var + '=' + fault + '\n'
	print '------------------ set:', cmd
	proc.stdin.write(cmd);
	proc.stdin.flush()
	
	
	cmd = 'print ' + var + '\n'
	print 'value after injection: '
   	proc.stdin.write(cmd);
	print '\n'
	

	# continue exec until finish
	proc.stdin.write('c\nc\n');
	proc.stdin.flush()

	# delete all breakpoint and watchpoints
	proc.stdin.write('delete\ny\n');	

		

if __name__ == "__main__":
	usage = "usage: %prog fault-file, exec, args for exec"
	filename=str();
	parser = OptionParser(usage=usage)

	(opts, args) = parser.parse_args()
	if len(args) == 0:
		parser.print_help();
		sys.exit(-1);

	target = args[1];
	exec_args = args[2:];
	faults_file = args[0];
	print 'exec:', target
	print 'exec args:', exec_args
	print 'faults:', faults_file

	faults = read_file(faults_file);
	print 'number of faults: ', len(faults)

	for i in range(len(faults)):
		print range(len(faults))
		print 'inject the {0:2d}th faults:'.format(i), faults[i]
		print ''
		time.sleep(10)
		subp = init(target, exec_args);
		inject(subp, faults[i]);
		print '\n\n'
		finish(subp);
		dirname = str(i)
		os.system('mkdir '+ dirname)
		os.system('mv *.bp '+ dirname) 
	

