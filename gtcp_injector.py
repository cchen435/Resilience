#!/usr/bin/env python

from optparse import OptionParser
import sys
import re
import time
import os

import gdbmi

'''
this script implement an injector using gdb
'''


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
		tmp = line.strip()
		if len(tmp) == 0:
			continue
		tmp = tmp.split(',')
		fault['entry'] = tmp[0];
		step['name'] = tmp[1];
		step['val'] = tmp[2];
		fault['step'] = step;
		fault['mem'] = tmp[3];
		fault['point'] = tmp[4];
		fault['fault'] = tmp[5];
		faults.append(fault.copy());
	
	handler.close()
	return faults


if __name__ == "__main__":
	usage = "usage: %prog fault-file, exec, args for exec"

	prefix = '/home/cchen/GTCP/data/'

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
	for i in faults:
		print i
	print '\n\n'

	folder = 0
	currvar = ''
	for fault in faults:
		print 'inject the fault:', fault
		print ''
		
                step_var = fault['step']['name']    # the step variable name
                step    = fault['step']['val']      # the step when the fault will be injected 
                var = fault['mem']                  # the varilabe where the fault will be injected 

                fault_val = fault['fault']
                s = Session(target = target, \
                        args = exec_args, \
                        language = 'c')

                s.start()
                s.watch_insert(step_var, step)
		s.exec_continue()
                s.inject(var, fault_val)
		s.exec_continue()
                s.finish()

                # moving data
		var = var.replace('->', '.')
		var = var[:var.find('[')]
		if currvar != var:
			currvar = var
			folder = 0
		
		folder = folder+1
                prefix = prefix.strip(' ')
		var = var.strip(' ')
		dirname = prefix + var
		print 'checking: ', dirname
		if not os.path.exists(dirname):
			print 'creating: ', dirname
			os.system('mkdir '+ dirname)

		dirname = prefix + var + '/' + str(folder);
		
		print 'checking: ', dirname
		if not os.path.exists(dirname):
			print 'creating: ', dirname
			os.system('mkdir '+ dirname)
		
		os.system('mv *.bp '+ dirname)	

		src = '/home/cchen/GTCP/data/normal '
		dst = prefix + var + '/0'

		if not os.path.exists(dst):
			cmd = 'ln -s ' + src + dst
			print 'link dir \'0\' to correct data: ', cmd
			os.system(cmd);

		time.sleep(2)
		print '\n\n\n\n'

