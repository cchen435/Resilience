#!/usr/bin/env python

import numpy
from Scientific.IO import NetCDF as nf
import os

'''
this file implements the I/O
operations for netCDF files.
and bp files
'''

def ncget(fname):
    variables = dict()
    fh = nf.NetCDFFile(fname, 'r')
    for v in fh.variables:
        data = fh.variables[v][:].ravel()
        variables[v] = data
    fh.close()
    return variables

def bpget(fname):
    variables = dict()
    tmpfile = '/tmp/fault'
    tmpdatafile = '/tmp/faultdata'

    # using 'bpls' command to get the vairalbe lists
    cmd = 'bpls ' + fname +  ' > ' + tmpfile
    os.system(cmd)

    # analyze each line of 'bpls output'
    # and only focuse on double type array data
    with open(tmpfile, 'r') as fh:
        for line in fh:
            line = line.strip()
            if line.startswith('double'):
                line = line.replace('{', '')
                line = line.replace('}', '')
                line = line.replace(',', '')
                line = line.split()

                # get the variable name and dimention info
                name = line[1]
                dim = (int(line[2]), int(line[3]), int(line[4]))
                #print line, name, dim

                # extract the related data for the variable using 'bp2ascii'
                # utility
                cmd = (' ').join(['bp2ascii -v', name, fname, tmpdatafile, '> /tmp/tmpfile'])
                os.system(cmd)

                with open(tmpdatafile, 'r') as f:
                    data =numpy.array(map(float, f.read().split()))
                    variables[name] = data

    return variables
'''
if __name__ == '__main__':
        print 'nc:'
        variables = ncget('h.fault.1.nc')

        print variables.keys()
        '''
    for v in variables:
        print 'name:', v[0], 'size', v[1].size, 'shape', v[1].shape
    '''

    print 'bp:'
    var = bpget('MOMENTS.bp')
    '''
    for v in var:
        print 'name:', v[0], 'size', v[1].size
    '''
    print var.keys()
'''
