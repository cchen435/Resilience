#!/usr/bin/env python

'''
this file defines an wrapper to GDB using
GDB/MI interface, the work is intended for 
fault inject, not fully utilize all features
of GDB

Author: Chao Chen
'''

import os
import os.path
import sys
import subprocess as sp
import fcntl
import re

import pdb


'''
read_file: read faults config from file, file contents should
    follow some formats:
    (entry), (step_name), (step_val), (mem), (point), (fault)
'''
def read_file(filename):
	faults = list()
	step = dict()
	try:
		handler = open(filename, 'r')
	except:
		print 'open file error'
		sys.exit(1)
	
	for line in handler:
	        fault = dict()
		tmp = line.strip()
		if len(tmp) == 0:
			continue
		tmp = tmp.split(';')
		fault['entry'] = tmp[0].strip();
		step['name'] = tmp[1].strip();
		step['val'] = tmp[2].strip();
		fault['step'] = step.copy();
		fault['mem'] = tmp[3].strip();
		fault['point'] = tmp[4].strip();
		fault['fault'] = tmp[5].strip();
		faults.append(fault.copy());
		fault.clear()

	handler.close() 
	return faults


class Session():
    def __init__(self, target, args=[], language = 'c'):
        '''
        constructor of Session class:
        target, the executable into which the fault will be injected
        args, arguments used by target
        language, the programming language used by target
        '''
        self.lang = language
        self.token = 0

        # check whether GDB exists
        gdb = self.__which('gdb')
        if gdb is None:
            sys.exit('GDB is not found')

        p = sp.Popen( args = [gdb, 
                        '--quiet',          # inhibit dumping info at start-up
                        '--nx',             # inhibit window interface
                        '--nw',             # ignore .gdb.init
                        '--interpreter=mi', # use GDB/MI interface
                        '--args',           # parsing arguments to target
                        target ] + args,
                stdin = sp.PIPE, stdout = sp.PIPE,
                bufsize = 0, close_fds = True)

        self.process = p
        self.stop_reason=''
        ''' end __init__ definition '''



    # start the process, and stop at the main function 
    def start(self, entry = 'main'):
        self.__send('-break-insert %s' % entry)
        self.__send('-exec-run')
        status = self.wait_for('*stopped,')
        reason = status.split(',')[0].lstrip('reason=')
        reason = reason.strip('\"')
        if reason != 'breakpoint-hit':
            sys.exit('stop reason \"%s\" is not as expected \
                    for cmd \"%s\"' % (reason, '-exec-run'))
        self.stop_reason = reason


    def __which(self, filename):
        ''' implement the 'which' utility in shell '''
        locations = os.environ.get('PATH').split(os.pathsep)
        for location in locations:
            candidate = os.path.join(location, filename)
            if os.path.isfile(candidate):
                return candidate 
        return None
    
    # send an command to GDB, and read back the status
    def __send(self, cmd):
        self.token += 1
        token = '%d' % self.token
        p = self.process
        p.stdin.write(token + cmd + '\n')
        p.stdin.flush()
        result = self.wait_for(token)
        if result.startswith('^error'):
            sys.exit(result);
        elif result.startswith('^done'):
            return result.lstrip('^done,')


    # continue the execution
    def exec_continue(self):
        self.__send('-exec-continue')
        status = self.wait_for('*stopped,')
        reason = status.split(',')[0].lstrip('reason=')
        reason = reason.strip('\"')
        self.stop_reason = reason 

    # insert a break point, return the breakpoint number
    # location could be identified using a function name 
    # e.g. istep or file name and line number, e.g. main.c:20
    def break_insert(self, location, condition=None):
        if condition is None:
            cmd = '%s %s' % ('-break-insert', location)
        else:
            cmd = '%s %s -c %s' % ('-break-insert', location, condition)
        result = self.__send(cmd)
        # adding code to check the execut result

    # insert a watch point, return the watchpoint number
    def watch_insert(self, var, value=None):
        if value is None:
            cmd = '%s %s' % ('-break-watch', var)
        else:
            value=value.strip()
            if self.lang in 'cCc++C++':
                cmd = '%s %s==%s' % ('-break-watch', var, value)
            elif self.lang in 'fortranFortran':
                cmd = '%s %s.eq.%s' % ('-break-watch', var, value)
  
        print 'DEBUG (watch_insert): %s' % cmd
        result = self.__send(cmd)


    # set the value to a varilabe
    def __set(self, var, val='0'):
        cmd = 'set var %s = %s' %(var, val)
        #print "DEBUG __set: %s %s" % (var, cmd)
        self.__send(cmd)

    
    # get the value of a variable, returned type is a string
    def get(self, var):
        cmd = '-data-evaluate-expression %s' % var;
        
        #print "DEBUG __GET: %s %s" % (var, cmd)

        result = self.__send(cmd)
        val = result.lstrip('value=').strip('\"')
        return val

    # inject the faults
    def inject(self, var, fault_ratio):
        self.__send('-break-delete') 

        fault_ratio = float(fault_ratio)
        # check whether the var is accessible by listing local variables
        cmd = '-stack-list-variables 0'
        if self.lang in ['fortran', 'Fortran', 'FORTRAN']:
            if var.find('::') < 0:          # no defined scope
                result = self.__send(cmd)
                if var.split('(')[0] not in result:
                    sys.exit('var \"%s\" is not accessible in current frame' % var)
        elif self.lang in 'cCc++C++':
            result = self.__send(cmd)
            tmp = re.findall('\w+', var)[0]
            if tmp not in result:
                sys.exit('var \"%s\" is not accessible in current frame %s' % (tmp, result))

        print '\n---------------------------->>>>>'
        print 'Injecting the fault (%4.6f) into variable \"%s\"' % (fault_ratio, var)
        #get old value
        old_val = float(self.get(var))
        print '%15s: %4.6f' % ('old value', old_val)

        if fault_ratio > 1 or old_val == 0 :
            new_val = str(fault_ratio)
        else:
            new_val = str(old_val * (1 + fault_ratio))
        self.__set(var, new_val)

        new_val = float(self.get(var))
        print '%15s: %4.6f' % ('new value', new_val)
        print 'fault (%4.6f) is injected into varialbe \"%s\"' % (fault_ratio, var)
        print '<<<<<----------------------------\n'

        
    # read the subprocess outout
    def __readline(self):
        p = self.process
        return p.stdout.readline().strip('\n')

    def __handle(self, line):
        
        ''' 
        out-of-band-record processing 
        including async and stream -record
        '''
        if line[0] == '*':      # exec message
            pass 
        elif line[0] == '+':    # status message
            pass
        elif line[0] == '=':    # notify message
            pass
        elif line[0] == '~':    # console stream
            pass
        elif line[0] == '@':    # target stream
            pass
        elif line[0] == '&':    # log stream
            pass


    # output
    def wait_for(self, token):
        while True:
            line = self.__readline()
            if len(line) == 0:
				continue
            elif line.find(token) >= 0:
                line = line.lstrip(token)
                return line
            elif line[0] in '+~=$@*^&':
                self.__handle(line)
            elif not line.lower().startswith('(gdb)'):
                print line


    def finish(self):
        while self.stop_reason != 'exited-normally':
            status = self.wait_for('*stopped,')
            reason = status.split(',')[0].lstrip('reason=')
            reason = reason.strip('\"')
            self.stop_reason = reason
        p = self.process
        self.__send('-gdb-exit')
        p.wait()


'''
test code
'''

'''
if __name__ == '__main__':
    s = Session(target = 'hello', args = [], language = 'c')
    p = s.process
    s.start()
    s.watch_insert('i', '50')
    s.exec_continue()
    print 'i:', s.get('i')
    s.inject('f', 1.5)
    s.exec_continue()
    s.finish()
'''
