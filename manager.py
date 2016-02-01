#!/usr/bin/env python

import subprocess as sp
import argparse
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            usage='%(prog)s exec [exec_args] [-r restart_exec_args]',
            description='a simple job manager',
            add_help=False )

    parser.add_argument('exec', help='executable binary' )
    parser.add_argument('args', nargs='*', help='executable arguments if any')
    parser.add_argument('-r', '--restart', dest='restart', nargs='*', 
                help='arguments used when restart')

    args = parser.parse_args()
    args = vars(args)
    print (args['exec'], args['args'], args['restart'])

    exec_file = [args['exec']]
    exec_args = args['args']
    restart_args = args['restart']

    print(exec_file, exec_args, restart_args, exec_file + exec_args)

    status = sp.call(exec_file + exec_args, shell=True)

    while status != 0:
        status = sp.call(exec_file + restart_args, shell=True)




