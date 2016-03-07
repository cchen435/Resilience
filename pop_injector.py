#!/usr/bin/env python

import subprocess as sp
from optparse import OptionParser
import sys
import re
import time
import os

import gdbmi

'''
this script implement an injector using gdb
'''

if __name__ == "__main__":
	usage = "usage: %prog fault-file, exec, args for exec"
	prefix = '/home/cchen/sc12-demo/test/data'
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

	faults = gdbmi.read_file(faults_file);
	print 'number of faults: ', len(faults)
	for i in faults:
		print i
	print '\n\n'

	folder = 0
	currvar = ''
	for fault in faults:
		print 'inject the fault:', fault
		print ''
                step_var = fault['step']['name']
                step = fault['step']['val']
		var = fault['mem']
                fault_val = fault['fault']
        
                s = gdbmi.Session(target = target, \
                        args = exec_args,       \
                        language = 'fortran')
                s.start()
                s.watch_insert(step_var, step)
                s.exec_continue()
                s.inject(var, fault_val)
                s.exec_continue()
                s.finish() 

		
                '''
		move data to a center
		'''
		var = var.replace('::', '.')
		var = var[:var.find('(')]
		if currvar != var:
			currvar = var
			folder = 0
		
		folder = folder+1
		
		# creating directory for injected variable
		prefix = prefix.strip(' ')
		
		# cireat subdir for restart and move related data
		restart_dir = prefix + '/restart';
		while not os.path.exists(restart_dir):
			print 'creating: ', restart_dir
			os.system('mkdir '+ restart_dir)
                
                var = var.strip(' ')
		dirname = restart_dir + '/' + var
		print 'checking: ', dirname
		while not os.path.exists(dirname):
			print 'creating: ', dirname
			os.system('mkdir '+ dirname)


		new_dir = dirname + '/' + str(folder)
		while not os.path.exists(new_dir):
			print 'creating: ', new_dir
			os.system('mkdir '+ new_dir)
		
		os.system('mv data/restart/* '+ new_dir)	
		print 'mv data/restart/* '+ new_dir	
		
		src = '/home/cchen/sc12-demo/test/data/normal/restart '
		dst = dirname + '/0'

		while not os.path.exists(dst):
			cmd = 'ln -s ' + src + dst
			print 'link dir \'0\' to correct data: ', cmd
			os.system(cmd);
		'''
		# cireat subdir for hist and move related data
		hist_dir = dirname + '/hist';
		if not os.path.exists(hist_dir):
			print 'creating: ', hist_dir
			os.system('mkdir '+ hist_dir)

		new_dir = hist_dir + '/' + str(folder)
		if not os.path.exists(new_dir):
			print 'creating: ', new_dir
			os.system('mkdir '+ new_dir)
		
		os.system('mv data/hist/*.nc '+ new_dir)	
		
		src = '/home/cchen/sc12-demo/test/data/normal/hist '
		dst = hist_dir + '/0'

		if not os.path.exists(dst):
			cmd = 'ln -s ' + src + dst
			print 'link dir \'0\' to correct data: ', cmd
			os.system(cmd);
		
		# create subdir tavg and move related data						 
		tavg_dir = dirname+'/tavg'

		if not os.path.exists(tavg_dir):
			print 'creating: ', tavg_dir
			os.system('mkdir '+ tavg_dir)
		
		new_dir = tavg_dir + '/' + str(folder)
		if not os.path.exists(new_dir):
			print 'creating: ', new_dir
			os.system('mkdir '+ new_dir)
		
		os.system('mv data/tavg/*.nc '+ new_dir)	

		
		src = '/home/cchen/sc12-demo/test/data/normal/tavg '
		dst = tavg_dir + '/0'

		if not os.path.exists(dst):
			cmd = 'ln -s ' + src + dst
			print 'link dir \'0\' to correct data: ', cmd
			os.system(cmd);
		'''
		time.sleep(2)
		print '\n\n\n\n'

