#!/usr/bin/env python

from optparse import OptionParser
import sys
import re
import time
import os

import gdbmi
import pdb

'''
this script implement an injector using gdb
'''

def move(normal, src, dst, var, folder):
    # check whether the restart destination folder exist
    while not os.path.exists(dst):
        print 'creating: ', dst
        os.system('mkdir '+ dst) 
       
    #create the folder to store data with fault injected
    var = var.strip(' ')
    dirname = os.path.join(dst, var)

    print 'checking: ', dirname
    while not os.path.exists(dirname):
        print 'creating: ', dirname
        os.system('mkdir '+ dirname)

    fault_dir = os.path.join(dirname, str(folder))
    
    while not os.path.exists(fault_dir):
        print 'creating: ', fault_dir
        os.system('mkdir '+ fault_dir)
       
    cmd  = ' '.join(['mv', src+'/*.bp', fault_dir])
    os.system(cmd)    


    dst = os.path.join(dirname, '0')

    while not os.path.exists(dst):
        cmd = ' '.join(['ln -s', normal, dst])
        os.system(cmd);
    ''' end of moving data '''

if __name__ == "__main__":
    usage = "usage: %prog fault-file, exec, args for exec"

    dst = '/net/hp101/cchen435/GTCP2/'
    src = os.getcwd()
    normal = '/net/hp101/cchen435/gtcp_normal'


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
        
        step_var = fault['step']['name']    # the step variable name
        step    = fault['step']['val']      # the step when the fault will be injected 
        var = fault['mem']                  # the varilabe where the fault will be injected 

        fault_val = fault['fault']
        point = fault['point']

        s = gdbmi.Session(target = target, \
                args = exec_args, \
                language = 'c')
        
        s.start()
        s.watch_insert(step_var, step)
        s.exec_continue()
        s.break_insert(point)
        s.exec_continue()
        #pdb.set_trace()
        s.inject(var, fault_val)
        s.break_delete()
        s.exec_continue()
        s.finish()
        
        # moving data
        var = var.replace('->', '.')
        var = var[:var.find('[')]
        if currvar != var:
            currvar = var
            folder = 0
        
        folder = folder+1
        move(normal, src, dst, var, folder)

        time.sleep(2)
        print '\n\n\n\n'

