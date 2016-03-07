#!/usr/bin/env python

import subprocess as sp
import argparse
import sys
import re
import time
import os

'''
this script implement a very simple job manager
it starts up the process and monitoring the exit
status of the job, and decide to restart the job 
or not
'''

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

    exec_file = ['mpirun -np 32 -hostfile hostfile ' + args['exec']]
    exec_args = args['args']
    restart_args = args['restart']

    print(exec_file, exec_args, restart_args, exec_file + exec_args)

    print 'exec: ', ' '.join(exec_file+exec_args)

    start = time.time()
    status = sp.call([' '.join(exec_file + exec_args)], shell=True)

    while status == 23:
        status = sp.call([' '.join(exec_file + restart_args)], shell=True)

    end = time.time()
    print "Total execution time: ", (end - start)



